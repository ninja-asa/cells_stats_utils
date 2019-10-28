# IMARIS cell data extractor

## Dependencies

You should have pre-installed Python 3 installed.

Additionally, the following Python packages are required:
- pandas
- seaborn
- easygui 
- openpyxl
- xlrd

## How to run?

Open a terminal and run
`python restruct_data`

You will be prompted to select a folder. This folder shall contain the "Sample"'s data where for example a folder shall have:
```
(SELECTED FOLDER)
¦   
+---SampleA
¦       Series10_cells.xls
¦       Series10_spots.xls
¦       Series11_cells.xls
¦       Series11_spots.xls
¦       Series12_cells.xls
¦       (...)
¦       
+---(...)
```

Once you run, the script will generate _per sample_, a excel sheet containing all the detected cells containing ≥ 1 vesicles across all series and, for each cell, the respective:
- number of vesicles
- sphericity
- volume
- mean intensity channel 2
- number of spots (one instance per serie)

Furthermore, 
- a boxplot overlapped with a swarm plot will be generated for each feature (to compare across samples) and saved to the folder.
![BoxPlot](https://user-images.githubusercontent.com/26262402/67725215-7b198400-f9d9-11e9-8bc5-7de20af7ff83.png)
- an excel sheet with the summary of the results generated (per sample, the average nr. of spots, vesicles, sphericity, volume, mean intensity of channel 2 and % %MBP+ cells.

You can configure the y-labels by editing in the script the dictionary `SAMPLE_LABELS`.

## How to request more features or communicate bugs?

Go to tab <kbd>Issues</kbd> at the top, create an Issue and assign the appropriate label. :smiley:
