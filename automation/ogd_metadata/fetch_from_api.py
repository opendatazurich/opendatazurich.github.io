# -*- coding: utf-8 -*-
"""Fetch CSV from CKAN API

Usage:
  fetch_from_api.py --file <path-to-csv>
  fetch_from_api.py (-h | --help)
  fetch_from_api.py --version

Options:
  -h, --help                      Show this screen.
  --version                       Show version.
  -f, --file <path-to-csv>        Path to CSV file

"""

import json
import os
import time

import pandas as pd
import requests
from docopt import docopt

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

CKAN_API_LINK = "https://data.stadt-zuerich.ch/api/3/action/current_package_list_with_resources"

# Pagination settings: CKAN API uses limit/offset for pagination.
# 500 results per page is a good balance between API calls and payload size.
PAGE_LIMIT = 500
PAGE_SLEEP = 2  # seconds between API requests to be nice to the server

# Fieldmapping CKAN API columns -> published column names
metadata = {
    "title": "titel",
    "notes": "beschreibung",
    "groups": "kategorie",
    "spatialRelationship": "raeumliche_beziehung",
    "author": "quelle",
    "timeRange": "zeitraum",
    "dataType": "datentyp",
    "updateInterval": "aktualisierungsdatum",
    "name": "dataset_name",
    "id": "dataset_id",
    "license_id": "license_id",
    "num_resources": "anzahl_ressourcen",
}

# Parse command line arguments using docopt
arguments = docopt(__doc__, version='Fetch CSV from CKAN API 1.0')


def get_full_package_list(limit=500, sleep=2):
    """Get full package list from CKAN API. Returns pandas df."""
    offset = 0
    frames = []
    session = requests.Session()

    while True:
        print(f"{offset} packages retrieved.")
        url = CKAN_API_LINK + f"?limit={limit}&offset={offset}"
        res = session.get(url)
        data = json.loads(res.content)
        if data["result"] == []:
            break
        data = pd.DataFrame(pd.json_normalize(data["result"]))
        frames.append(data)
        if len(data) < limit:
            break
        offset += limit
        time.sleep(sleep)
    data = pd.concat(frames)
    data.reset_index(drop=True, inplace=True)
    print("Number of datasets", data.shape[0])
    return data

def extract_keywords(x, sep=', '):
    """
    Extract keywords from ckan metadata json. To be used in pandas.apply()
    Example: [{'description': '', 'display_name': 'Mobilität'},]
    """
    out_string = ''
    for elem in x:
        out_string += elem['display_name']+sep
    return out_string.rstrip(sep)

def extract_list(x, sep=', '):
    """
    Extract element from ckan metadata json list. To be used in pandas.apply()
    Example: ['taeglich']
    """
    out_string = ''
    for elem in x:
        out_string += elem+sep
    return out_string.rstrip(sep)
    
print("Getting metadata from CKAN")
packages = get_full_package_list(limit=PAGE_LIMIT, sleep=PAGE_SLEEP)

# flatten json sub elements
print("Extracting values from json sub elements")
packages["groups"] = packages["groups"].apply(extract_keywords)
packages["dataType"] = packages["dataType"].apply(extract_list)
packages["updateInterval"] = packages["updateInterval"].apply(extract_list)


# prepare df for output
print("Preparing df for output")
output_df = packages[metadata.keys()]
output_df = output_df.sort_values(by="name")
output_df = output_df.rename(columns=metadata)

print(output_df)

# saving as csv
csv_path = arguments['--file']
print("Saving csv to ", csv_path)
output_df.to_csv(csv_path, index=False, encoding='utf-8', date_format='%Y-%m-%dT%H:%M:%SZ')

