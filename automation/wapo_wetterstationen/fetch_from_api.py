# -*- coding: utf-8 -*-

import os
import sys
import csv
import traceback
from datetime import datetime, date, timedelta
import pytz
import requests
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

__location__ = os.path.realpath(
    os.path.join(
        os.getcwd(),
        os.path.dirname(__file__)
    )
)

stations = {
    'mythenquai': {
        'url': 'https://www.tecson-data.ch/zurich/mythenquai/download/csvdat.php',
        'user': os.getenv('WAPO_MY_USER'),
        'password': os.getenv('WAPO_MY_PASS'),
    },
    'tiefenbrunnen': {
        'url': 'https://www.tecson-data.ch/zurich/tiefenbrunnen/download/csvdat.php',
        'user': os.getenv('WAPO_TB_USER'),
        'password': os.getenv('WAPO_TB_PASS'),
    },
}


def safefloat(s):
    if not s:
        return s
    return float(s)


def safeint(s):
    if not s:
        return s
    f = float(s)
    r = round(f)
    if f == r:
        return int(f)
    else:
        raise ValueError(f"Can't parse {s} as int without losing precision")


def request_data(station):
    config = stations[station]
    payload = {
        'feld': 1,
        'datum_von': date(date.today().year, 1, 1).strftime('%d.%m.%Y'),
        'datum_bis': date.today().strftime('%d.%m.%Y'),
    }
    r = requests.post(config['url'], data=payload, auth=(config['user'], config['password']))
    r.raise_for_status()
    lines = r.text.splitlines()
    reader = csv.DictReader(lines, delimiter=';')
    return reader


def save_csv_file(data, path):
    field_names = [
        'timestamp_utc',
        'timestamp_cet',
        'air_temperature',
        'water_temperature',
        'wind_gust_max_10min',
        'wind_speed_avg_10min',
        'wind_force_avg_10min',
        'wind_direction',
        'windchill',
        'barometric_pressure_qfe',
        'barometric_pressure_qnh',
        'precipitation',
        'dew_point',
        'global_radiation',
        'humidity',
        'water_level',
    ]
    with open(path, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, field_names, quoting=csv.QUOTE_NONNUMERIC)
        writer.writeheader()
        for row in data:
            from pprint import pprint
            pprint(row)
            zurich_tz = pytz.timezone('Europe/Zurich')
            row_date = datetime.strptime(row['Datum'], '%d.%m.%Y %H:%M:%S')
            date_cet = zurich_tz.localize(row_date)
            date_utc = date_cet.astimezone(pytz.utc)
            mapped_row = {
                'timestamp_utc': date_utc.isoformat(),
                'timestamp_cet': date_cet.isoformat(),
                'air_temperature': safefloat(row.get('Temp2m', '')),
                'water_temperature': safefloat(row.get('TempWasser', '')),
                'wind_gust_max_10min': safefloat(row.get('WGmax', '')),
                'wind_speed_avg_10min': safefloat(row.get('WGavr', '')),
                'wind_force_avg_10min': safefloat(row.get('Umr_Beaufort')),
                'wind_direction': safeint(row.get('WRvek', '')),
                'windchill': safefloat(row.get('Windchill', '')),
                'barometric_pressure_qfe': safefloat(row.get('LuftdruckQFE', '')),
                'barometric_pressure_qnh': safefloat(row.get('LuftdruckQNH', '')),
                'precipitation': safefloat(row.get('Regen', '')),
                'dew_point': safefloat(row.get('Taupunkt', '')),
                'global_radiation': safeint(row.get('Strahlung', '')),
                'humidity': safefloat(row.get('Feuchte', '')),
                'water_level': safefloat(row.get('Pegel', '')),
            }
            pprint(mapped_row)
            writer.writerow(mapped_row)

try:
    # get mythenquai data
    reader = request_data('mythenquai')
    path = os.path.join(__location__, f'messwerte_mythenquai_{date.today().year}.csv')
    save_csv_file(reader, path)

    # get tiefenbrunnen data
    reader = request_data('tiefenbrunnen')
    path = os.path.join(__location__, f'messwerte_tiefenbrunnen_{date.today().year}.csv')
    save_csv_file(reader, path)

except Exception as e:
    print("Error: %s" % e, file=sys.stderr)
    print(traceback.format_exc(), file=sys.stderr)
    sys.exit(1)
finally:
    sys.stdout.flush()