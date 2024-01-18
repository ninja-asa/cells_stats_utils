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
        easygui.msgbox("No data. Are you sure you provided the correct path?", "Error")
        sys.exit()
    metrics = processor.ExtractMetricsForSamples(samples_data, samples_spots,save_to_excel=True)
    print("==============")
    print("Generating plots - if you don't wish to wait press Ctrl+C or Ctrl+X to quit process")
    for feature in processor.CELLS_SHEET_COLUMN.keys():
         print(f"Generating box plot for {feature}")
         processor.GenerateBoxPlot(samples_data,feature,visualize=VISUALIZE)

    