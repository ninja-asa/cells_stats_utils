from dendrite.make_summary import IMARISDendriteSumary
import sys        
import easygui
import os
import pandas as pd
import numpy as np

if __name__ == "__main__":
    if  len(sys.argv)>1:
        cells_data = sys.argv[1]
    else: 
        file_path= easygui.fileopenbox(msg="Select dendrite_xxx_.pkl file.")
    directory =  os.path.dirname(file_path)+os.sep
    processor = IMARISDendriteSumary(directory)
    
    samples_data = pd.read_pickle(file_path)
    if samples_data.empty: 
        easygui.msgbox("No data. Are you sur you provided the correct path?", "Error")
        sys.exit()
   
    for feature in samples_data.columns.values:
        if (np.issubdtype(samples_data[feature].dtype, np.number)):
            processor.GenerateBoxPlot(samples_data,feature,visualize=False)
         
