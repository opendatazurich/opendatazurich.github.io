# -*- coding: utf-8 -*-

import os
import sys
import csv
import traceback
from datetime import datetime, date, timedelta
import pandas as pd
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
        'url': 'https://www.tecson-data.ch/zurich/mythenquai/uebersicht/messwerte.php',
        'user': os.getenv('WAPO_MY_USER'),
        'password': os.getenv('WAPO_MY_PASS'),
    },
    'tiefenbrunnen': {
        'url': 'https://www.tecson-data.ch/zurich/tiefenbrunnen/uebersicht/messwerte.php',
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


def request_data(url, data={}, auth=None, verify=True):
    http = requests.Session()
    http.auth = auth
    headers = {'user-agent': 'Mozilla Firefox: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:53.0) Gecko/20100101 Firefox/53.0'}
    r = http.post(url, data=data, headers=headers, timeout=10, verify=verify)
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
            zurich_tz = pytz.timezone('Europe/Zurich')
            row_date = datetime.strptime(row['Datum'], '%d.%m.%Y %H:%M:%S')
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
    today = '05.08.2022'
    enddate = '15.08.2022'
    for k, v in stations.items():
        data = {
            "messw_beg": today,
            "messw_end": enddate,
            "auswahl": "2",
            "combilog": k,
            "suchen": "Werte+anzeigen"
        }
    
        # get data
        r =  request_data(v['url'], data=data, auth=(v['user'], v['password']))
        df = pd.read_html(r.text, header=0)[1]
        new_names = {
            'Datum\xa0/\xa0Uhrzeit\xa0(MEZ)': 'Datum',
            'Lufttemperatur\xa0(°C)': 'Lufttemperatur',
            'Luftfeuchte\xa0(%)': 'Luftfeuchte',
            'Windböen (max) 10 min.\xa0(m/s)': 'Windboeen',
            'Windgeschw. Ø 10min.\xa0(m/s)': 'Windgeschw',
            'Windstärke Ø 10 min.\xa0(bft)': 'Windstaerke',
            'Windrichtung\xa0(°)': 'Windrichtung',
            'Windchill\xa0(°C)': 'Windchill',
            'Luftdruck QNH\xa0(hPa)': 'LuftdruckQNH',
            'Luftdruck QFE\xa0(hPa)': 'LuftdruckQFE',
            'Niederschlag\xa0(mm)': 'Niederschlag',
            'Taupunkt\xa0(°C)': 'Taupunkt',
            'Globalstrahlung\xa0(W/m²)': 'Globalstrahlung',
            'Wassertemperatur\xa0(°C)': 'Wassertemperatur',
            'Pegel (NS 406.0m)\xa0(m)': 'Pegel',
        }
        df = df.rename(columns=new_names)
        data = df.to_dict('records')
        
        path = os.path.join(__location__, f'messwerte_{k}_today.csv')
        save_csv_file(data, path)

except Exception as e:
    print("Error: %s" % e, file=sys.stderr)
    print(traceback.format_exc(), file=sys.stderr)
    sys.exit(1)
finally:
    sys.stdout.flush()
