# IMARIS data "restructor" 

## Dependencies

You should have pre-installed Python 3 installed.

Additionally, install the dependencies under _requirements.txt_ :
```
pip install -r requirements.txt
```

## Usage

### How to run?

Open a terminal and enter
`cd path\to\restructIMARIS\restructdata`
and either run

`python process_dendrite_data.py` or

`python process_cells_data.py`


In both cases, you will be prompted to select a folder. This folder shall contain the "Sample"'s data where for example a folder shall have:

```
process_cells_data
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

```
process_dendrite_data
(SELECTED FOLDER)
¦   
+---SampleA
¦       Series10.xls
¦       Series11.xls
¦       (...)
¦       
+---(...)
```

## Purpose
### Process Cells Data

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

By editing the :page_facing_up: `config_cells.json` you can set:
+ sample names (to replace SampleA, and so on, name)
+ sheet and columns name in source excel files

### Process Dendrite Data

This is a simpler application which aggregates the information from different selected sheets and saves to an excel file the selected metrics (mean, max, min, sum, 50%), which can be set in the configuration file (:page_facing_up: `config_dendrite.json`). 

As previously, you can rename the samples. Similar plots are generated as well.


## Report Error or Feature

In [Github](https://github.com/ninja-asa/cells_stats_utils/), go to tab <kbd>Issues</kbd> at the top, create an Issue and assign the appropriate label. :smiley:
