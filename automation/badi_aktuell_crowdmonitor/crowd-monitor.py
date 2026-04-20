import os
import json
import logging
from datetime import datetime

import requests
import pandas as pd
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
    df["retrievaltime"] = pd.Timestamp.now()
    
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

print(result_df)

output_path = "automation/badi_aktuell_crowdmonitor"
os.makedirs(output_path, exist_ok=True)
output_filename = "crowd-monitor.csv"
output_filepath = os.path.join(output_path, output_filename)

columns = ["retrievaltime","name","currentfill","maxfill","uid",]
result_df[columns].to_csv(output_filepath, index=False)

logging.info(f"Saved CSV to: {output_filepath}")
