# -*- coding: utf-8 -*-

import os
import sys
import csv
import re
import pandas as pd
import traceback
from datetime import datetime
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
        'url': 'https://www.tecson-data.ch/zurich/tiefenbrunnen/minianz/startseite.php?position=Mythenquai',
    },
    'tiefenbrunnen': {
        'url': 'https://www.tecson-data.ch/zurich/tiefenbrunnen/minianz/startseite.php?position=Tiefenbrunnen',
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


def request_data(url, data={}, auth=None, verify=True):
    http = requests.Session()
    http.auth = auth
    headers = {'user-agent': 'Mozilla Firefox: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:53.0) Gecko/20100101 Firefox/53.0'}
    r = http.get(url, headers=headers, timeout=10, verify=verify)
    r.raise_for_status()
    return r


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
        'precipitation',
        'dew_point',
        'global_radiation',
        'humidity',
        'water_level',
    ]
    with open(path, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, field_names, quoting=csv.QUOTE_MINIMAL)
        writer.writeheader()
        for row in data:
            print(row)
            zurich_tz = pytz.timezone('Europe/Zurich')
            row_date = datetime.strptime(row['Datum'], '%d.%m.%Y %H:%M')
            date_cet = zurich_tz.localize(row_date)
            date_utc = date_cet.astimezone(pytz.utc)

            pressure_qfe = safefloat(row.get('LuftdruckQFE', ''))
            pressure_qnh = safefloat(row.get('LuftdruckQNH', ''))
            if not pressure_qfe and pressure_qnh:
                pressure_qfe = pressure_qnh - 47 # local pressure, QFE = QNH - 47hPa

            mapped_row = {
                'timestamp_utc': date_utc.isoformat(),
                'timestamp_cet': date_cet.isoformat(),
                'air_temperature': safefloat(row.get('Lufttemperatur', '')),
                'water_temperature': safefloat(row.get('Wassertemperatur', '')),
                'wind_gust_max_10min': safefloat(row.get('Windboeen', '')),
                'wind_speed_avg_10min': safefloat(row.get('Windgeschw', '')),
                'wind_force_avg_10min': safefloat(row.get('Windstaerke')),
                'wind_direction': safeint(row.get('Windrichtung', '')),
                'windchill': safefloat(row.get('Windchill', '')),
                'barometric_pressure_qfe': pressure_qfe,
                'precipitation': safefloat(row.get('Niederschlag', '')),
                'dew_point': safefloat(row.get('Taupunkt', '')),
                'global_radiation': safeint(row.get('Globalstrahlung', '')),
                'humidity': safefloat(row.get('Luftfeuchte', '')),
                'water_level': safefloat(row.get('Pegel', '')),
            }
            writer.writerow(mapped_row)

try:
    today = datetime.now().strftime('%d.%m.%Y')

    for k, v in stations.items():
        # get data
        r =  request_data(v['url'], verify=False)
        df = pd.read_html(r.text, index_col=0)[3]
        df = df.rename(index={df.index[0]: 'Station'})
        df = df.transpose()
        df.columns = df.columns.str.replace(":", "")
        df['Station'] = df['Station'][2]
        df['Sturmwarnstufe'] = df['Sturmwarnstufe'][2]
        df = df[0:1]

        data = df.to_dict('records')[0]
    
        parsed_values = {
            'Datum': re.search(r"(\d{2}\.\d{2}\.\d{4} \d{2}:\d{2}).*Uhr", data['Station'])[1],
            'Lufttemperatur': data.get('Lufttemperatur', ''),
            'Luftfeuchte': data.get('Luftfeuchte', ''),
            'Windboeen': data.get('Windböen (max) 10 min.', ''),
            'Windgeschw': data.get('Windgeschw. Ø 10min.', ''),
            'Windstaerke': data.get('Windstärke Ø 10 min.', ''),
            'Windrichtung': re.search(r"\(([\d,\.]+).*°\)", data.get('Windrichtung', ''))[1],
            'Windchill': data.get('Windchill', ''),
            'LuftdruckQNH': data.get('Luftdruck QNH', ''),
            'LuftdruckQFE': data.get('Luftdruck QFE', ''),
            'Niederschlag': data.get('Niederschlag', ''),
            'Taupunkt': data.get('Taupunkt', ''),
            'Globalstrahlung': data.get('Globalstrahlung', ''),
            'Wassertemperatur': data.get('Wassertemperatur', ''),
            'Pegel':  data.get('Pegel (NS 406.0m)', ''),
        }

        path = os.path.join(__location__, f'messwerte_{k}_today.csv')
        save_csv_file([parsed_values], path)

except Exception as e:
    print("Error: %s" % e, file=sys.stderr)
    print(traceback.format_exc(), file=sys.stderr)
    sys.exit(1)
finally:
    sys.stdout.flush()
