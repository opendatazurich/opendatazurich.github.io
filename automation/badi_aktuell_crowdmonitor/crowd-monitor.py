import os
import json
import logging

import requests
import pandas as pd
import numpy as np
from dotenv import load_dotenv


# -------------------------------------------------------
# Setup
# -------------------------------------------------------


load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

CROWD_MONITOR_USER = os.getenv("CROWD_MONITOR_USER")
CROWD_MONITOR_PW = os.getenv("CROWD_MONITOR_PW")

BASE_URL = "https://premises.crowdmonitor.ch"
HEADERS = {
    "x-api-key": CROWD_MONITOR_PW,
    "x-api-user": CROWD_MONITOR_USER,
}


# -------------------------------------------------------
# Helper: API GET with error handling
# -------------------------------------------------------

def api_get(endpoint: str) -> dict:
    """GET request with basic error handling."""
    url = f"{BASE_URL}/{endpoint}"
    logging.info(f"Requesting: {url}")

    response = requests.get(url, headers=HEADERS)

    try:
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        logging.error(f"HTTP error: {e} - Response: {response.text}")
        raise
    except json.JSONDecodeError:
        logging.error("Response was not valid JSON")
        raise

# -------------------------------------------------------
# Helpers for occupancy
# -------------------------------------------------------


def compute_occupancy(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate occupancy in the same way as shown here: 
    https://www.stadt-zuerich.ch/de/stadtleben/sport-und-erholung/sport-und-badeanlagen/sommerbaeder/badi-aktuell.html
    """
    df = df.copy()

    df["maxfill"] = df["maxfill"].astype("Int64")
    df["currentfill"] = df["currentfill"].astype("Int64")

    # Validierung
    data_invalid = (df["maxfill"] <= 0) | (df["currentfill"] < 0)

    # Verhältnis berechnen
    occupied_ratio = df["currentfill"] / df["maxfill"]

    # JS-Logik exakt nachgebaut
    occupancy = np.floor(occupied_ratio * 100 / 25) + 1
    occupancy = np.minimum(occupancy, 4)

    # Ungültige Daten behandeln
    occupancy = occupancy.where(~data_invalid, np.nan)

    df["occupancy"] = occupancy.astype("Int64")  # nullable integer

    return df


def compute_icons(df: pd.DataFrame) -> pd.DataFrame:
    """
    Create occupancy icons in the same way as shown here: 
    https://www.stadt-zuerich.ch/de/stadtleben/sport-und-erholung/sport-und-badeanlagen/sommerbaeder/badi-aktuell.html
    """
    df = df.copy()

    iconname_transparent =  "○" # "⬜" 
    iconname_filled_blue = "●" #  "🟦" 

    def row_to_icons(occ):
        if pd.isna(occ):
            return "-"

        occ = int(occ)

        filled = min(max(occ, 0), 4)
        transparent = 4 - filled

        icon_str = iconname_filled_blue * filled + iconname_transparent * transparent
        return icon_str

    df["occupancy_icons"] = df["occupancy"].apply(row_to_icons)

    return df




# -------------------------------------------------------
# Fetch locations
# -------------------------------------------------------

locations_data = api_get("qdata/locations")
location_df = pd.DataFrame(locations_data)
logging.info(f"Fetched locations: {len(location_df)}")
# drop locations that are not baths
locations_to_drop = ["Letzigrund", "Josel-Areal", "Messehalle 9"]
logging.info(f"Removing locations, if present: {locations_to_drop}")
location_df = location_df[~location_df["name"].isin(locations_to_drop)]
logging.info(f"Remaining locations: {len(location_df)}")

# -------------------------------------------------------
# Fetch store data for all locations
# -------------------------------------------------------

all_entries = []

for location_uid in location_df["uid"].unique():
    location_name = location_df.loc[location_df["uid"]==location_uid, "name"].values[0]
    logging.info(f"Fetching store data for UID: {location_uid}: {location_name}")

    store_data = api_get(f"qdata/store/{location_uid}")
    df = pd.DataFrame(store_data)
    df["retrievaltime"] = pd.Timestamp.now(tz="Europe/Zurich")
    
    all_entries.append(df)


# -------------------------------------------------------
# Combine and save results
# -------------------------------------------------------

result_df = pd.concat(all_entries, ignore_index=True)

# some location donot have meaningful information
# drop locations where maxfill is zero
locations_withou_data = result_df.loc[result_df["maxfill"]==0, "name"].to_list()
logging.info(f"There are locations with maxfill=0. Drop those: {locations_withou_data}")
result_df = result_df[result_df["maxfill"]>0]

# -------------------------------------------------------
# Compute occupancy
# -------------------------------------------------------
logging.info("Computing occupancy icons")

result_df = compute_occupancy(result_df)
result_df = compute_icons(result_df)

print(result_df)

output_path = "automation/badi_aktuell_crowdmonitor"
os.makedirs(output_path, exist_ok=True)
output_filename = "crowd-monitor.csv"
output_filepath = os.path.join(output_path, output_filename)

columns = [
    "retrievaltime",
    "name",
    "currentfill",
    # "maxfill",
    "occupancy_icons",
    "uid",]
result_df[columns].to_csv(output_filepath, index=False)

logging.info(f"Saved CSV to: {output_filepath}")
