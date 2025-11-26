# qualtrics heatmap georeferencer

converts qualtrics heatmap clicks from pixel coordinates into lat/lon using a georeferenced map (geotiff). In a second step calculates distance error.

## setup
```bash
pip install -r requirements.txt
```
## usage
1. inputs:
* `qualtrics_results.csv`: raw survey export (header row 1).
* `sources/kombikarte_georeferenziert.tif`: map with metadata.
* `answer_key.csv`: true coordinates for of speakers.

2. config:
* in `process_map_data.py`: adjust image dimensions (tif_width vs png_width) if necessary
* in `calc_errors.py`adjust ANSWER_KEY_PATH

3. run:
```bash
python process_map_data.py
python calc_errors.py
```
## output
* `processed_results.csv`: contains calculated _calc_lat and _calc_lon.
* `final_results_with_error.csv`: contains haversine distance error in km.
