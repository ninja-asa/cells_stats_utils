import pandas as pd
import os

def GetListSeries(directory):
    list_series = []
    entries = os.listdir(directory)
    for entry in entries:
        splitted = os.path.splitext(entry) 
        if splitted[-1]==".xls" and 'spots' in splitted[0]:
            list_series.append(splitted[0].split('_')[0])
    list_series.sort()
    return list_series
            
def GetSamplesFolder(directory):
    list_samples =[]
    entries = os.listdir(directory)
    for entry in entries:
        if os.path.isdir(directory+entry) and 'Sample' in entry:
            list_samples.append(entry)
    list_samples.sort()
    return list_samples

def GetSpotsData(sample_file):
    xls = pd.ExcelFile(sample_file+'_spots.xls')
    return pd.read_excel(xls,sheet_name='Diameter',skiprows=1).shape[0]

def GetCellsData(sample_file):
    xls = pd.ExcelFile(sample_file+'_cells.xls')
    data_vesicles = pd.read_excel(xls,
                                  sheet_name='Cell Number Of Vesicles Ves-10',
                                  skiprows=1)
    # remove nr of vesicles <1
    indices = data_vesicles['Cell Number Of Vesicles']>0
    data_vesicles = data_vesicles[indices]['Cell Number Of Vesicles'] 
    
    data_green_chn = pd.read_excel(xls,
                                   sheet_name='Cell Intensity Mean Ch=2 Img=1',
                                   skiprows=1)
    data_green_chn = data_green_chn[indices]['Cell Intensity Mean']
    
    data_sphericity = pd.read_excel(xls,
                                   sheet_name='Cell Sphericity',
                                   skiprows=1)     
    data_sphericity = data_sphericity[indices]['Cell Sphericity']

    data_volume = pd.read_excel(xls,
                                   sheet_name='Cell Volume',
                                   skiprows=1)     
    data_volume = data_volume[indices]['Cell Volume']
    
    sample_data = pd.concat([data_vesicles,data_green_chn,data_sphericity,data_volume],
                            axis=1)
    
    return sample_data
        
def GetData(directory):
    samples_name = GetSamplesFolder(directory)
    sample_dataframes = pd.DataFrame()
    
    for sample in samples_name[0:3]:
        print("Processing {}".format(sample))
        directory_data = directory+sample+'/'
        series = GetListSeries(directory_data)
        full_sample_data = pd.DataFrame()
        for serie in series:
            spots = GetSpotsData(directory_data+serie)
            print("Loading {} ...".format(serie))
            samples_data = GetCellsData(directory_data+serie)
            if samples_data.empty:
                continue
            spots_col = [0]*samples_data.shape[0]
            spots_col[0]=spots
            sample_cols=[sample]*samples_data.shape[0]
            spots_df = pd.DataFrame({'Sample':sample_cols,'Nr. Spots':spots_col}, index=samples_data.index.values)
            full_series_data = pd.concat([spots_df,samples_data],axis=1)
            full_sample_data = pd.concat([full_sample_data,full_series_data])
        full_sample_data.index.name = 'Cell ID'
        full_sample_data.reset_index()
        sample_dataframes=sample_dataframes.append(full_sample_data)
        full_sample_data.to_excel (directory+sample+'.xlsx', header=True) 
        full_sample_data = pd.DataFrame()
    print("Data saved to {}".format(directory))
    return sample_dataframes

def ExtractMetrics(df,directory):
    vesicles = df[['Sample','Cell Number Of Vesicles']].groupby('Sample').sum()
    vesicles = vesicles.rename(columns = {'Cell Number Of Vesicles':'Total # Vesicles'})
    sphericity = df[['Sample','Cell Sphericity']].groupby('Sample').mean()
    sphericity= sphericity.rename(columns = {'Cell Sphericity':'Mean Sphericity'})
    volume_total = df[['Sample','Cell Volume']].groupby('Sample').sum()
    volume_total= volume_total.rename(columns = {'Cell Volume':'Total Volume'})
    volume_mean = df[['Sample','Cell Volume']].groupby('Sample').mean()
    volume_mean= volume_mean.rename(columns = {'Cell Volume':'Mean Volume'})
    chn_int = df[['Sample','Cell Intensity Mean']].groupby('Sample').mean()
    chn_int= chn_int.rename(columns = {'Cell Intensity Mean':'Mean Intensity'})
    spots = df[['Sample','Nr. Spots']].groupby('Sample').sum()
    new_df = pd.concat([vesicles,sphericity,volume_total,volume_mean,chn_int,spots],axis=1)
    new_df['%MBP+ cells']=new_df.apply(DetermineMBP,axis=1)
    new_df.to_excel (directory+'summary.xlsx', header=True)
    print("Created a summary of the results under {}".format(directory+'summary.xlsx'))

def DetermineMBP(data):
    
    return data['Total # Vesicles']/data['Nr. Spots']*100

def DetermineMBP2(data):
    
    return data['Cell Number Of Vesicles']/data['Nr. Spots']*100

import seaborn as sns
import matplotlib.pyplot as plt
def GenerateBoxPlots(data, x, x_range = [], swarmplot=True): 
    if x_range == []:
        x_range = [data[x].min(), data[x].max()]
    f, ax = plt.subplots(figsize=(7, 6))
    sns.boxplot(x=x, y="Sample", data=data, palette="pastel")
    sns.swarmplot(x=x, y="Sample", data=data, alpha=".75", color="0.3")
    ax.xaxis.grid(True)
    ax.set(ylabel="")
    f.savefig(x+".pdf", bbox_inches='tight')

    return

import sys        
import easygui
if __name__ == "__main__":
    #if  len(sys.argv)>1:
       # directory = sys.argv[1]
    #else: 
    directory= easygui.diropenbox()+'\\'
    samples_data = GetData(directory)
    ExtractMetrics(samples_data,directory)
    features = ['Cell Volume', 'Cell Intensity Mean', 'Cell Sphericity','Cell Number Of Vesicles']
    for feature in features:
        GenerateBoxPlots(samples_data,feature)

    