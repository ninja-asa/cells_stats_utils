import pandas as pd
import os
from datetime import date
import seaborn as sns
import matplotlib.pyplot as plt
import json
class IMARISDataProcessor:
    """ This class expects a folder generated by IMARIS with the following format
    (SELECTED FOLDER)>SampleX>
                                Series??_cells
                                Series??_spots
    
    It will concatenate all (series) data correspondent to a single sample type in a single file and
    then provide statistics on the distribution on different features extracted:
    - intensity of Channel 2
    - number of vesicles
    - sphericity
    - volume
    - number of spots
    """
    CELLS_SHEET_COLUMN = {
        'Vesicles': ['Cell Cytoplasm Number of Ve-3','Cell Cytoplasm Number of Vesicles'],
        'Intensity' : ['Cell Intensity Mean Ch=2 Img=1','Cell Intensity Mean'],
        'Sphericity' : ['Cell Sphericity', 'Cell Sphericity'],
        'Volume' : ['Cell Volume', 'Cell Volume']
    }

    SPOTS_OUT_COL_NAME = 'Nr. Spots'

    def __init__(self, directory, sample_labels = {}):
        self.directory = directory
        self.ReadConfigFile()

    def ReadConfigFile(self):
        with open("config.json") as json_data_file:
            data=json.load(json_data_file)
        self.CELLS_SHEET_COLUMN = data['CellSheetColNames']
        self.sample_labels = data['SampleLabels']
        self.SPOTS_OUT_COL_NAME = data['SpotOutputName']

    
    def ExtractSamplesData(self, save_to_excel = True, save_to_pickle = False):
        """ExtractSamplesData returns dataframe containing the samples data
        
        Args:
            save_to_excel (bool, optional): Per sample, save an excel sheet per sample containing the respective series data. Defaults to True.
            save_to_pickle (bool, optional): Save dataframe containing all the samples data. Defaults to False.
        
        Returns:
            pd.DataFrame: Samples data
        """
        self.samples_name = self.IdentifySamples()
        self.VerifySampleNames()
        samples_dataframes = pd.DataFrame()
        samples_spots = pd.DataFrame() 
        # Iterating over each (sample) folder
        for sample in self.samples_name:
            print("Processing {}".format(sample))
            
            series = self.IdentifySeries(sample) # and getting all the series                        
            sample_data = pd.DataFrame() # dataframe which will contain all the sample data
            sample_spots = pd.DataFrame()
            for serie in series:
                print("Loading {} ...".format(serie))
                # Handle spots data              
                nr_spots = self.ExtractSerieSpotsData(sample, serie) # get the cells which we categorized as "spot"
                serie_spots = pd.DataFrame({'Sample':[sample],self.SPOTS_OUT_COL_NAME:[nr_spots]}, index=[0])
                sample_spots = pd.concat([sample_spots,serie_spots])

                # Handle cells data
                serie_data = self.ExtractSerieCellsData(sample, serie)
                if serie_data.empty:
                    continue
                
                sample_col_df  = pd.DataFrame(
                    {'Sample':self.CreateColumnForSerie(value=sample,nr_cells=serie_data.shape[0])}, 
                    index=serie_data.index.values)

                full_serie_data  = pd.concat([
                    sample_col_df,
                    serie_data],
                    axis=1)
                        
                    # concatenating series data to form the overall sample dataframe
                sample_data = pd.concat([sample_data,full_serie_data])
            
            sample_data.reset_index() # remove cell id as index to avoid overriding when concatenating
            sample_spots.reset_index()
            samples_dataframes = pd.concat((samples_dataframes,sample_data))
            samples_spots = pd.concat((samples_spots,sample_spots))
            if save_to_excel:
                with pd.ExcelWriter(directory+sample+'.xlsx') as writer:
                    sample_data.to_excel(writer,sheet_name="cell_data", header=True) 
                    sample_spots.to_excel(writer,sheet_name="spots_data", header=True) 
        print("Data saved to {}".format(directory))
        if samples_dataframes.empty:
            return samples_dataframes, samples_spots

        samples_dataframes['Sample']=samples_dataframes.apply(self.ReplaceSampleLabels,axis=1)
        samples_spots['Sample']=samples_spots.apply(self.ReplaceSampleLabels,axis=1)

        if save_to_pickle:
            samples_dataframes.to_pickle(self.directory+'cells_data_'+ date.today().strftime("%Y%m%d")+ ".pkl")
            samples_spots.to_pickle(self.directory+'spots_data_'+date.today().strftime("%Y%m%d")+ ".pkl")
            
        return samples_dataframes, samples_spots
            
    def IdentifySamples(self):
        """IdentifySamples finds all the samples (each sample has its own folder)  
        
        Returns:
            [list]: contains sample names
        """

        list_samples =[]
        entries = os.listdir(self.directory) # all files/folder within provided directory
        for entry in entries:
            if os.path.isdir(directory+entry) and 'Sample' in entry: # if it is a folder and contains "Sample"
                list_samples.append(entry) # added to the list of samples
        list_samples.sort() # sort them 
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
        
        Returns:
            [list]: contains the list of series existing for a given sample
        """
        list_series = []
        entries = os.listdir(os.path.join(self.directory,sample_name))
        for entry in entries:
            splitted = os.path.splitext(entry) 
            if splitted[-1]==".xls" and 'spots' in splitted[0].lower(): # we are expecting per series to exist a "spots" excel
                list_series.append(splitted[0].split('_')[0])
        list_series.sort()
        return list_series  

    def ExtractSerieSpotsData(self, sample_name, serie_name):
        """ExtractSeriesSpotsData from the provided filename, it extracts the number of spots by checking 
            , in the "Diameter" sheet, the number of rows of data. 
        
        Args:
            sample_file ([string]): filename containing the spots data
        
        Returns:
            [int]: number of spots in serie 
        """
        xls = pd.ExcelFile(os.path.join(self.directory, sample_name, serie_name)+'_Spots.xls')
        return pd.read_excel(xls,sheet_name='Diameter',skiprows=1).shape[0] 

    def ExtractSerieCellsData(self, sample_name, serie_name):
        """ExtractCellsData extracts serie's cells data from the "Series[XX]_cells.xls" file
        
        Args:
            sample_filename ([string]): filename containing the cells data
        
        Returns:
            [pd.DataFrame]: dataframe with columns Number of Vesicles, Intensity Mean, Sphericity,
                Volume and ID. Only the cells with at least a vesicles were left in the DataFrame
        """
        xls = pd.ExcelFile(os.path.join(self.directory, sample_name, serie_name)+'_Cells.xls')
        data_dict = {}
        for assigned_name, sheet_col_name in self.CELLS_SHEET_COLUMN.items():
            data_dict[assigned_name] = pd.read_excel(xls,
                                sheet_name=sheet_col_name[0],
                                skiprows=1)[sheet_col_name[1]]
            # data_dict[assigned_name] = df[sheet_col_name[1]].rename(
            #                             columns = {sheet_col_name[1]:assigned_name}
            #                         )
        # remove nr of vesicles <1
        indices = data_dict['Vesicles']>0

        
        sample_data = pd.concat([data[indices.values] for data in data_dict.values()],
                                axis=1)
        for assigned_name, sheet_col_name in self.CELLS_SHEET_COLUMN.items():
            sample_data.rename(columns = {sheet_col_name[1]:assigned_name},inplace=True)
        sample_data.index.name="Cell ID"
        

        return sample_data

    def CreateColumnForSerie(self, value, nr_cells):
        """CreateColumnForSerie Generate column nr_cells long containing only value or having only the first cell with value and the remainder filled with zero.
        
        Args:
            value ([str, int, float]): value to be added present in the column
            nr_cells ([int]): number of cells the column contains
            only_first (bool, optional): Whehter the column is filled with the same value or just the first cell bears the value whereas the remainder are set to zero. Defaults to True.
        
        Returns:
            [list]: list containing value (in every cell or only the first)
        """

        new_col=[value]*nr_cells
        return new_col
        

    def ExtractMetricsForSamples(self, cells_df, spots_df, save_to_excel=True):
        """ExtractMetricsForSamples groups dataframe by Sample and extracts statistical information on each of the features.
        
        Args:
            df (pd.DataFrame): input dataframe with the full information on the cells
            save_to_excel (bool, optional): whether metrics should be exported as an excel file. Defaults to True.
        
        Returns:
            [pd.DataFrame]: contains statistics per sample type of the input dataframe
        """

        metrics = cells_df.groupby('Sample').describe(percentiles=[])
        
        if save_to_excel:

            with pd.ExcelWriter(self.directory+'summary.xlsx',mode = 'w') as writer:  # doctest: +SKIP
                temp = metrics.unstack(1)[:,'mean'].unstack(0)
                sum_vesicles = cells_df.groupby('Sample').sum()['Vesicles']
                sum_spots = spots_df.groupby('Sample').sum()[self.SPOTS_OUT_COL_NAME]
                sum_vesicles_spots = pd.concat([sum_vesicles, sum_spots],axis=1)
                temp['Vesicles'] = sum_vesicles_spots['Vesicles']
                temp[self.SPOTS_OUT_COL_NAME] = sum_vesicles_spots[self.SPOTS_OUT_COL_NAME]
                temp['%MBP']=temp.apply(self.DetermineMBP, axis=1)
                metrics = metrics.drop(columns = 'count', level=1)
                metrics = metrics.drop(columns = 'Vesicles')
                temp.to_excel(writer, sheet_name= 'summary')
                metrics.unstack(1).to_excel(writer, sheet_name="full statistics")
            
            print("Created a summary of the results under {}".format(self.directory+'summary.xlsx'))

        return metrics
    
    def DetermineMBP(self,data):
        return data['Vesicles']/data[self.SPOTS_OUT_COL_NAME]*100

    def ReplaceSampleLabels(self,datarow):
        return self.sample_labels[datarow['Sample']]

    def GenerateBoxPlot(self,dataframe, feature, x_range = [], swarmplot=True, visualize = False):
        if x_range == []:
            x_range = [dataframe[feature].min(), dataframe[feature].max()]
        f, ax = plt.subplots(figsize=( 20 , len(dataframe['Sample'].unique())*1.5)) # Figure size is set here, you can adjust it
        sns.boxplot(x=feature, y="Sample", data=dataframe, palette=sns.light_palette((210, 90, 60), input="husl"))
        sns.swarmplot(x=feature, y="Sample", data=dataframe, alpha=".75", color="0.3")
        ax.xaxis.grid(True)
        ax.set(ylabel="")
        plt.tight_layout()
        if visualize:
            plt.show()
        else:
            f.savefig(self.directory+feature+date.today().strftime('%Y%m%d')+".pdf")

        return
            


VISUALIZE = False # if True, it just shows the plot; if false, the plot is saved to PDF

import sys        
import easygui

if __name__ == "__main__":
    if  len(sys.argv)>1:
        directory = sys.argv[1]
    else: 
        directory= easygui.diropenbox()+os.sep
    processor = IMARISDataProcessor(directory)
    samples_data, samples_spots = processor.ExtractSamplesData(save_to_excel=True, save_to_pickle=True)
    if samples_data.empty: 
        easygui.msgbox("No data. Are you sur you provided the correct path?", "Error")
        sys.exit()
    metrics = processor.ExtractMetricsForSamples(samples_data, samples_spots,save_to_excel=True)
   
    for feature in processor.CELLS_SHEET_COLUMN.keys():
         processor.GenerateBoxPlot(samples_data,feature,visualize=VISUALIZE)

    