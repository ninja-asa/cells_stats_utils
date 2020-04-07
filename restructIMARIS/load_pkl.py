from restruct_data import IMARISDataProcessor
import sys        
import easygui
import os
import pandas as pd
if __name__ == "__main__":
    if  len(sys.argv)>1:
        cells_data = sys.argv[1]
    else: 
        file_path= easygui.fileopenbox(msg="Select cells_xxx_.pkl file.")
    directory =  os.path.dirname(file_path)+os.sep
    processor = IMARISDataProcessor(directory)
    
    samples_data = pd.read_pickle(file_path)
    if samples_data.empty: 
        easygui.msgbox("No data. Are you sur you provided the correct path?", "Error")
        sys.exit()
   
    for feature in processor.CELLS_SHEET_COLUMN.keys():
         processor.GenerateBoxPlot(samples_data,feature,visualize=False)
