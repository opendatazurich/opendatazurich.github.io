# -*- coding: utf-8 -*-
"""Fetch CSV and from Hystreet API

Usage:
  fetch_from_api.py --file <path-to-csv> --geojson <path-to-geojson> --parquet <path-to-parquet> [--no-verify]
  fetch_from_api.py (-h | --help)
  fetch_from_api.py --version

Options:
  -h, --help                      Show this screen.
  --version                       Show version.
  -f, --file <path-to-csv>        Path to CSV file
  -g, --geojson <path-to-geojson> Path to GeoJSON file
  -p, --parquet <path-to-parquet> Path to Parquet file
  --no-verify                     Option to disable SSL verification for reqests.

"""


import pandas as pd
import requests
import os
from datetime import datetime, timedelta
import pytz
from docopt import docopt
from dotenv import load_dotenv, find_dotenv
import json
import geojson


load_dotenv(find_dotenv())
arguments = docopt(__doc__, version='Fetch CSV from hystreet API 1.0')

__location__ = os.path.realpath(os.getcwd())
path = os.path.join(__location__, "data")

location_api = 'https://api.hystreet.com/locations'
API_KEY = os.getenv('HYSTREET_API_KEY')


# requests to hystreet API (incl. API KEY)
def hystreet_request(api, params={}):
    headers = {
        'X-API-Token': API_KEY,
    }
    if arguments['--no-verify']:
        r = requests.get(api, headers=headers, params=params, verify=False)
    else:
        r = requests.get(api, headers=headers, params=params)
    r.raise_for_status()
    data = r.json()
    return data


# generator for date ranges
def daterange(start_date, end_date, step=1):
    tz = pytz.timezone('Europe/Zurich')
    total_days = int((end_date - start_date).days)
    local_start = tz.localize(start_date)
    for n in range(0, total_days, step):
        yield (local_start + timedelta(n), local_start + timedelta(n + step - 1))


def convert_to_df(data, location_id):
    # create records for Pandas
    records = []
    for row in data['measurements']:
        record = {}
        record['timestamp'] = ''
        record['location_id'] = location_id
        record['location_name'] = data['name']
        record['ltr_label'] = data['metadata']['ltr_label']
        record['rtl_label'] = data['metadata']['rtl_label']
        record.update(row)
        record.update(record['details'])
        del record['details']
        del record['min_temperature']
        
        for zone in (record['zones'] or []):
            for k, v in zone.items():
                if k == 'id':
                    continue
                record[f"zone_{zone['id']}_{k}"] = v

        del record['zones']
        
        records.append(record)
    df = pd.DataFrame(records)
    return df


# save measurements and save as pickled DataFrame
def save_measurements(location_id, start_date, end_date, df_path='.'):
    if not os.path.exists(df_path):
        os.mkdir(df_path)
        
    params = {
        'resolution': 'hour',
        'from': start_date.isoformat(),
        'to': end_date.replace(hour=23, minute=59, second=59).isoformat()
    }
    data = hystreet_request(f"{location_api}/{location_id}", params=params)
    print(f"{data['statistics']['timerange_count']} rows loaded.")
    df = convert_to_df(data, location_id)
    pickle_path = os.path.join(df_path, f'{location_id}_{start_date.date().isoformat()}_{end_date.date().isoformat()}.pks')
    df.to_pickle(pickle_path)
    print(f"Saved pickle at {pickle_path}")


def save_geojson_to_file(geojson_path, data):
    print(f"Save geojson at {geojson_path}")
    with open(geojson_path, 'w') as f:
        f.write(geojson.dumps(data))

# get all measurements
print("Get location geojson...")
locations = hystreet_request(location_api)
for loc in locations:
    start_date = datetime(2021, 9, 29) # first day with measurements
    end_date = datetime.now() + timedelta(1) # tomorrow
    for cur_date, cur_end_date in daterange(start_date, end_date, step=14):
        save_measurements(loc['id'], cur_date, cur_end_date, path)

df = pd.concat([pd.read_pickle(os.path.join(path, x)) for x in os.listdir(path) if x.endswith('.pks')])
df['timestamp'] = pd.to_datetime(df['timestamp'], utc=True)
df = df.sort_values(by=['timestamp', 'location_name'])

csv_path =  arguments['--file']
df_today = df[df.timestamp <= 'today'].reset_index(drop=True)
# save to csv
df_today.tail(20).to_csv(csv_path, index=False, encoding='utf-8', date_format='%Y-%m-%dT%H:%M:%SZ')
# save to parquet
df_today.to_parquet(arguments['--parquet'])

# get GeoJSON of locations
locations = hystreet_request(location_api)
features = []
for loc in locations:
    loc_details = data = hystreet_request(f"{location_api}/{loc['id']}", params={})
    geo = geojson.loads(json.dumps(loc_details['geojson']))
    props = {
        "hystreet_location_id": loc['id'],
        "name": loc['name'],
        "city": loc['city'],
    }
    features.append(geojson.Feature(geometry=geo, id=loc['id'], properties=props))

feature_col = geojson.FeatureCollection(features)
geo_path =  arguments['--geojson']
save_geojson_to_file(geo_path, feature_col)