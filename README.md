# IMARIS cell data extractor

## Dependencies

You should have pre-installed Python 3 installed.

Additionally, install the dependencies under _requirements.txt_ :
```
pip install -r requirements.txt
```

## Usage
### How to run?

Open a terminal and run `python restruct_data`.

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
You can also provide the path as an argument when executing the script `python restruct_data path/to/folder`.

### What do I get?

Once you run, the script will generate _per sample_ an excel sheet containing all the detected cells containing ≥ 1 vesicles across all series and, for each cell, the respective:
- number of vesicles
- sphericity
- volume
- mean intensity channel 2
- number of spots (one instance per serie)

Additionally, you obtain a :page_facing_up: `summary.xls` with two sheets:
1. *summary*: per sample type, the total number of vesicles, the total nr of spots, mean of intensity, volume and sphericity and %MBP
2. *full statistics*: provides, per feature, the mean, standard deviation, max, min and median for sphericity, volume and intensity.

Plots are automatically generated as well: a boxplot overlapped with a swarm plot will be generated for each feature (to compare across samples).

![BoxPlot](https://user-images.githubusercontent.com/26262402/67725215-7b198400-f9d9-11e9-8bc5-7de20af7ff83.png)

You can configure the y-labels by editing in the script the dictionary `SAMPLE_LABELS`.

## Report Error or Feature

In [Github](https://github.com/ninja-asa/cells_stats_utils/), go to tab <kbd>Issues</kbd> at the top, create an Issue and assign the appropriate label. :smiley:
