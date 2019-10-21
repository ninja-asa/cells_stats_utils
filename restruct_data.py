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
    sample_dataframes = []
    
    for sample in samples_name:
        directory_data = directory+sample+'/'
        series = GetListSeries(directory_data)
        full_sample_data = pd.DataFrame()
        for serie in series:
            spots = GetSpotsData(directory_data+serie)
            
            samples_data = GetCellsData(directory_data+serie)
            if samples_data.empty:
                continue
            spots_col = [0]*samples_data.shape[0]
            spots_col[0]=spots
            spots_df = pd.DataFrame({'Nr. Spots':spots_col}, index=samples_data.index.values)
            full_series_data = pd.concat([samples_data,spots_df],axis=1)
            full_sample_data = pd.concat([full_sample_data,full_series_data])
        sample_dataframes.append(full_sample_data)
        full_sample_data.index.name = 'Cell ID'
        export_excel = full_sample_data.to_excel (directory+sample+'.xlsx', header=True,) 
        full_sample_data = pd.DataFrame()
    return full_sample_data
        
import sys        
import easygui
if __name__ == "__main__":
    if  len(sys.argv)>1:
        directory = sys.argv[1]
    else: 
        directory= easygui.diropenbox()+'\\'
    GetData(directory)