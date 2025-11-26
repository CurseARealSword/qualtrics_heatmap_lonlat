# imports
import pandas as pd
import rasterio
from pyproj import Transformer
import os

# config
TIF_PATH = "sources/Kombikarte_georeferenziert.tif"  
CSV_PATH = "qualtrics_results.csv"
OUTPUT_PATH = "processed_results.csv" 

# distorition correction
TIF_WIDTH = 2604
TIF_HEIGHT = 3333

PNG_WIDTH = 2599
PNG_HEIGHT = 3335

SCALE_X = TIF_WIDTH / PNG_WIDTH
SCALE_Y = TIF_HEIGHT / PNG_HEIGHT

print(f"X-scale factor: {SCALE_X}")
print(f"Y-scale factor: {SCALE_Y}")
print(f"-------------")


def process_survey_data():
    # step 1: load map metadata
    if not os.path.exists(TIF_PATH):
        print(f"error: nothing in {TIF_PATH}")
        return

    print("loading geotiff metadata...")
    with rasterio.open(TIF_PATH) as src:
        tif_transform = src.transform 
        
        # which projection system?
        src_crs = src.crs 

    # prepare  math converter
    to_gps = Transformer.from_crs(src_crs, "EPSG:4326", always_xy=True) # always_xy=True --> order is long, lat

    # step 2: load survey data
    print("loading CSV data..")
    # to dataframe, use 1st row as header 
    df = pd.read_csv(CSV_PATH, header=0)
    df_clean = df.drop([0]).copy() # drop 2nd header row. I'm not sure why copy is needed

    # step 3: find coordinated columns
    # look for standard qualtrics format for heatmap: _1_x
    x_cols = [col for col in df_clean.columns if str(col).endswith("_1_x")]
    
    if not x_cols:
        print("error: no heatmap columns found in CSV")
        return

    print(f"found {len(x_cols)} questions to process: {x_cols}")

    # step 4: process all rows
    for x_col in x_cols:
        # find matching y column
        y_col = x_col.replace("_1_x", "_1_y")
        
        if y_col not in df_clean.columns:
            print(f"error: could not find matching Y column for {x_col}. skipping.")
            continue

        base_name = x_col.split("_")[0] # e.g "Q169"
        lat_col = f"{base_name}_Calc_Lat"
        lon_col = f"{base_name}_Calc_Lon"

        print(f"  > processing question {base_name}...")

        # we use apply() to run this logic on every single participant
        def get_coords(row):
            try:
                # 1. get raw qualtrics pixels
                raw_x = float(row[x_col])
                raw_y = float(row[y_col])
                
                # 2. fix distortion (PNG to TIF)
                tif_pixel_x = raw_x * SCALE_X
                tif_pixel_y = raw_y * SCALE_Y

                # 3. 3onvert Pixels -> map projection units
                map_x, map_y = tif_transform * (tif_pixel_x, tif_pixel_y)

                # 4. Convert Map Units -> GPS Lat/Lon
                lon, lat = to_gps.transform(map_x, map_y)

                
                return pd.Series([lat, lon])
            except (ValueError, TypeError, KeyError):
                # return empty if user didn't click
                return pd.Series([None, None])

        # run the function and get new columns
        df_clean[[lat_col, lon_col]] = df_clean.apply(get_coords, axis=1)

    # step 5: remove "unnamed" ghost columns
    df_clean = df_clean.loc[:, ~df_clean.columns.str.contains('^Unnamed')]

    # step : save results
    print(f"saving data to {OUTPUT_PATH}...")
    df_clean.to_csv(OUTPUT_PATH, index=False)
    print("finished!")

if __name__ == "__main__":
    process_survey_data()