VISUALIZE = False # if True, it just shows the plot; if false, the plot is saved to PDF

import sys        
import easygui
from dendrite.make_summary import IMARISDendriteSumary
import os

if __name__ == "__main__":
    if  len(sys.argv)>1:
        directory = sys.argv[1]
    else: 
        directory= easygui.diropenbox()+os.sep
    processor = IMARISDendriteSumary(directory)
    samples_data = processor.ProcessData()

    processor.SaveToExcel(samples_data)
    for feature in processor.sheets.keys():
         processor.GenerateBoxPlot(samples_data,feature,visualize=VISUALIZE)
    
