# -*- coding: utf-8 -*-

import os
import sys
import csv
import re
from collections import defaultdict
from bs4 import BeautifulSoup
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
        'url': 'https://www.tecson-data.ch/zurich/mythenquai/',
    },
    #'tiefenbrunnen': {
    #    'url': 'https://www.tecson-data.ch/zurich/tiefenbrunnen/',
    #},
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
        r =  request_data(v['url'])
        soup = BeautifulSoup(r.text, 'html.parser')

        tags = soup.select("table td span")
        titles = {
            'Datum': re.compile(r'^.*Aktuelle.*Werte.*$', re.MULTILINE|re.DOTALL),
            'Wind': re.compile(r'Wind Aktuell'),
            'Lufttemperatur_ds': re.compile(r'Lufttemperatur \(Ø\)'),
            'Lufttemperatur': re.compile(r'Lufttemperatur'),
            'Sturmwarnstufe': re.compile(r'Sturmwarnstufe'),
            'Luftfeuchte': re.compile(r'Luftfeuchte'),
            'Windchill': re.compile(r'Windchill'),
            'LuftdruckQHN': re.compile(r'Luftdruck QNH'),
            'LuftdruckQFE': re.compile(r'Luftdruck QFE'),
            'Regen': re.compile(r'Regen'),
            'Globalstrahlung': re.compile(r'Globalstrahlung'),
            'Wassertemperatur': re.compile(r'Wassertemperatur'),
            'Pegel': re.compile(r'Pegel'),
            'Taupunkt': re.compile(r'Taupunkt'),
            'Monatszusammenfassung': re.compile(r'Monatszusammenfassung'),
        }
        values = defaultdict(list)
        key = None
        for tag in tags:
            text = tag.get_text()

            for title, regex in titles.items():
                if regex.match(text):
                    key = title
                    break
            
            if key and not titles[key].match(text):
                values[key].append(text)
    
        parsed_values = {
            'Datum': (re.search(r"(\d{2}\.\d{2}\.\d{4} \d{2}:\d{2}).*Uhr", " ".join(values['Datum'])) or ['', ''])[1],
            'Lufttemperatur': (re.search(r"([\d,\.]+).*°C", values['Lufttemperatur'][0]) or ['', ''])[1],
            'Luftfeuchte': (re.search(r"([\d,\.]+).*%", values['Luftfeuchte'][0]) or ['', ''])[1],
            'Windboeen': '',
            'Windgeschw': (re.search(r"([\d,\.]+).*m/s", values['Wind'][1]) or ['', ''])[1],
            'Windstaerke': (re.search(r"([\d,\.]+).*bft", values['Wind'][2]) or ['', ''])[1],
            'Windrichtung': (re.search(r"\(([\d,\.]+).*°\)", values['Wind'][0]) or ['', ''])[1],
            'Windchill': (re.search(r"([\d,\.]+).*°C", values['Windchill'][0]) or ['', ''])[1],
            'LuftdruckQNH': (re.search(r"([\d,\.]+).*hPa", values.get('LuftdruckQHN', [''])[0]) or ['', ''])[1],
            'LuftdruckQFE': (re.search(r"([\d,\.]+).*hPa", values.get('LuftdruckQFE', [''])[0]) or ['', ''])[1],
            'Niederschlag': (re.search(r"([\d,\.]+).*mm", values.get('Regen', [''])[0]) or ['', ''])[1],
            'Taupunkt': (re.search(r"([\d,\.]+).*°C", values.get('Taupunkt', [''])[0]) or ['', ''])[1],
            'Globalstrahlung': (re.search(r"([\d,\.]+).*W/m", values.get('Globalstrahlung', [''])[0]) or ['', ''])[1],
            'Wassertemperatur': (re.search(r"([\d,\.]+).*°C", values['Wassertemperatur'][0]) or ['', ''])[1],
            'Pegel': (re.search(r"([\d,\.]+).*m", values.get('Pegel', [''])[0]) or ['', ''])[1],
        }
        data = {k: v.replace(',', '.') for k, v in parsed_values.items()}

        path = os.path.join(__location__, f'messwerte_{k}_today.csv')
        save_csv_file([data], path)

except Exception as e:
    print("Error: %s" % e, file=sys.stderr)
    print(traceback.format_exc(), file=sys.stderr)
    sys.exit(1)
finally:
    sys.stdout.flush()
