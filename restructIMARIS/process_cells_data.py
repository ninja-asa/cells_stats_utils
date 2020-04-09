VISUALIZE = False # if True, it just shows the plot; if false, the plot is saved to PDF

import sys        
import easygui
from cells.restruct_data import IMARISDataProcessor
import os

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

    