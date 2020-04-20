import pandas as pd
import json
import os
from datetime import date
import seaborn as sns
import matplotlib.pyplot as plt
class IMARISDendriteSumary:
    def __init__(self, directory, dir_config = None):
        if dir_config is None:
            self.config_filename_path = "." +os.sep
        else:
            self.config_filename_path = dir_config+os.sep
        self.config_filename_path = os.path.join(
            self.config_filename_path,"config_dendrite.json"
        )
        self.directory = directory + os.sep
        self.ReadConfigFile()


    def ReadConfigFile(self):
        with open(self.config_filename_path) as json_data_file:
            data=json.load(json_data_file)
        self.sample_labels = data['SampleLabels']
        self.sheets = data['Sheets']
        self.overall = data["OverallSheet"]

    def ProcessData(self):
        self.samples = self.IdentifySamples()
        self.samples_df = pd.DataFrame()
        for sample in self.samples:
            sample_data = self.GetSampleData(sample)
            sample_col_df  = pd.DataFrame(
                    {'Sample':
                       [sample]*sample_data.shape[0]},index=sample_data.index.values)
            sample_data = pd.concat([sample_data,sample_col_df],axis=1)
            self.samples_df = pd.concat([self.samples_df,sample_data],axis=0)
        
        self.samples_df['Sample']=self.samples_df.apply(self.ReplaceSampleLabels,axis=1)
        self.samples_df.to_pickle(self.directory+'dendrites_data_'+ date.today().strftime("%Y%m%d")+ ".pkl")
        return self.samples_df

    def ReplaceSampleLabels(self,datarow):
        return self.sample_labels[datarow['Sample']]
    def IdentifySamples(self):
        """IdentifySamples finds all the samples (each sample has its own folder)  
        
        Returns:
            [list]: contains sample names
        """

        list_samples =[]
        entries = os.listdir(self.directory) # all files/folder within provided directory
        for entry in entries:
            if os.path.isdir(self.directory+entry) and 'Sample' in entry: # if it is a folder and contains "Sample"
                list_samples.append(entry) # added to the list of samples
        list_samples.sort() # sort them 
        self.samples_name = list_samples
        self.VerifySampleNames()
        return list_samples        
    
    def VerifySampleNames(self):
        if not self.sample_labels:
            self.sample_labels= dict(zip(self.samples_name,self.samples_name))
        else:
            for identified_sample_name in self.samples_name:
                if identified_sample_name not in self.sample_labels.keys():
                    self.sample_labels[identified_sample_name]=identified_sample_name
   
    def IdentifySeries(self, sample_name):
        """IdentifySeries finds within a sample folder, all the series.
        def
        Returns:
            [list]: contains the list of series existing for a given sample
        """
        list_series = []
        entries = os.listdir(os.path.join(self.directory,sample_name))
        for entry in entries:
            splitted = os.path.splitext(entry) 
            if splitted[-1]==".xls": # we are expecting per series to exist a "spots" excel
                list_series.append(splitted[0].split('_')[0])
        list_series.sort()
        return list_series  

    def GetSampleData(self, sample_name):
        print("Processing {}".format(sample_name))
        sample_data = pd.DataFrame() # dataframe which will contain all the sample data
        filename = os.path.join(self.directory, sample_name)
        series = self.IdentifySeries(sample_name)
        for serie in series:
            print("Loading {} ...".format(serie))
            series_df = self.ExtractExcelData(sample_name,serie)
            sample_data = pd.concat([sample_data,series_df],axis=0)
        self.SaveSampleDataToExcel(sample_data,sample_name)
        # writer = pd.ExcelWriter(self.directory+sample_name+'.xlsx',mode='w')
        # sample_data.to_excel(writer)
        # writer.save()
        return sample_data
    


    def ExtractExcelData(self,sample_name,series_name):
        filename = os.path.join(self.directory, sample_name, series_name+".xls")
        xls = pd.ExcelFile(filename)
        series_df = pd.DataFrame()
        number_filaments = self.ExistFilaments(xls)
        if number_filaments == 0:
            return series_df
        
        for sheet in self.sheets.keys():
            sheet_series = pd.read_excel(xls,
                                sheet_name=sheet,
                                skiprows=2,usecols=[0],header=None)
            series_df = pd.concat([series_df, sheet_series],axis=1)
        name_cols = list(self.sheets.keys()) + ["Overall"]
        number_filaments_series = pd.Series([number_filaments] + [0]*(series_df.shape[0]-1))
        series_df = pd.concat([series_df,number_filaments_series],axis=1)
        series_df.set_axis([name for name in name_cols], axis=1, inplace=True)
        
        return series_df

    def ExistFilaments(self,xls_file):
        overall = list(self.overall.keys())[0]
        sheet_series = pd.read_excel(xls_file,sheet_name=overall,
                                skiprows=2,usecols=[0,1],header=None)
        number_of_filaments = sheet_series[sheet_series[0]==self.overall[overall]][1].values[0]
        return number_of_filaments
        
    def SaveSampleDataToExcel(self, sample_data,sample_name):
        print("Saving to {}".format(self.directory+sample_name+'.xlsx'))
        writer = pd.ExcelWriter(self.directory+sample_name+'.xlsx',mode='w')
        sample_data.to_excel(writer,sheet_name="series")
        metrics_df = sample_data.describe()
        metrics_df = metrics_df.unstack(1)
        output_metrics = pd.DataFrame()
        row = 0;
        cols_selection = []
        for sheet,out_metrics in self.sheets.items():
            metrics_df[sheet,'sum'] = sample_data[sheet].sum()
            sheet_vec = [sheet]*(len(out_metrics))
            l = list(zip(sheet_vec,out_metrics))
            cols_selection = cols_selection + l
        
        metrics_df['Overall', 'sum'] = sample_data['Overall'].sum()
        cols_selection = cols_selection + [('Overall', 'sum')]
        metrics_df[cols_selection].unstack(1).to_excel(writer,sheet_name="summary")
        writer.save()
        return                                
    def SaveToExcel(self, dendrites_data_):
        print("Saving to {}".format(self.directory+'summary.xlsx'))

        metrics_df = dendrites_data_.groupby('Sample').describe()
        output_metrics = pd.DataFrame()
        row = 0;
        cols_selection = []
        for sheet,out_metrics in self.sheets.items():
            metrics_df[sheet,'sum'] = dendrites_data_.groupby('Sample')[sheet].sum()
            sheet_vec = [sheet]*(len(out_metrics))
            l = list(zip(sheet_vec,out_metrics))
            cols_selection = cols_selection + l
        metrics_df['Overall', 'sum'] = dendrites_data_.groupby('Sample')['Overall'].sum()
        cols_selection = cols_selection + [('Overall', 'sum')]
        writer = pd.ExcelWriter(self.directory+'summary.xlsx',mode='w')
        metrics_df[cols_selection].unstack(1).to_excel(writer)
        writer.save()
    
    def GenerateBoxPlot(self,dataframe, feature, x_range = [], swarmplot=True, visualize = False):
        print("Saving boxplot for {}".format(feature))
        f, ax = plt.subplots() # Figure size is set here, you can adjust it
        sns.boxplot(x=feature, y="Sample", data=dataframe, palette=sns.light_palette((210, 90, 60), input="husl"))
        ax.xaxis.grid(True)
        ax.set(ylabel="")
        plt.tight_layout()
        if visualize:
            plt.show()
        else:
            f.savefig(self.directory+feature+date.today().strftime('%Y%m%d')+".pdf")
        return



        





    
                
        
