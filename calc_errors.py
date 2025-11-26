import pandas as pd
import numpy as np

# config
INPUT_DATA_PATH = "output/processed_results.csv"
ANSWER_KEY_PATH = "sources/answer_key_template.csv"
OUTPUT_PATH = "output/final_results_with_error.csv"

def haversine_distance(lat1, lon1, lat2, lon2):
    """
    Vectorized Haversine Formula:
    calculates distance between two sets of coordinates in km.
    input: series (Columns) of Lat/Lons in DEGREES.
    output: series of distances in KM.
    see https://stackoverflow.com/questions/25767596/vectorised-haversine-formula-with-a-pandas-dataframe
    """
    R = 6371  # earth radius in km

    # step 1: convert degrees to radians
    phi1, phi2 = np.radians(lat1), np.radians(lat2)
    dphi = np.radians(lat2 - lat1)
    dlambda = np.radians(lon2 - lon1)

    # step 2: apply formula
    a = np.sin(dphi/2)**2 + \
        np.cos(phi1) * np.cos(phi2) * np.sin(dlambda/2)**2
    
    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))
    
    return R * c

def calculate_errors():
    # 1. load data
    print("loading input & answer key...")
    df = pd.read_csv(INPUT_DATA_PATH)
    keys = pd.read_csv(ANSWER_KEY_PATH)

    # 2.loop through each question in answer key
    print(f"found {len(keys)} targets in answer key")

    for index, row in keys.iterrows():
        qid = row['Question_ID']
        true_lat = row['True_Lat']
        true_lon = row['True_Lon']
        
        # define the column names in user data
        user_lat_col = f"{qid}_Calc_Lat"
        user_lon_col = f"{qid}_Calc_Lon"
        error_col = f"{qid}_Error_km"

        # sanity check: does question exist in the user data?
        if user_lat_col not in df.columns:
            print(f"warning: Could not find columns for {qid} in survey data. skipping.")
            continue
        
        print(f"calculating error for {qid}...")

        # 3. calculate cistance
        # pass the  column of user guesses vs the single true coordinate
        df[error_col] = haversine_distance(
            df[user_lat_col], df[user_lon_col],
            true_lat, true_lon
        )

    # 4. save final file
    print(f"saving final analysis to {OUTPUT_PATH}...")
    df.to_csv(OUTPUT_PATH, index=False)
    print("finished.")

if __name__ == "__main__":
    calculate_errors()