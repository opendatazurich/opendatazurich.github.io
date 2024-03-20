# -*- coding: utf-8 -*-

import os
import sys
import csv
import io
from ftplib import FTP
from datetime import datetime
import pytz
import traceback
from dotenv import load_dotenv, find_dotenv


__location__ = os.path.realpath(
    os.path.join(
        os.getcwd(),
        os.path.dirname(__file__)
    )
)

load_dotenv(find_dotenv())

# host, user, pw aus dem .env File lesen
host = os.getenv('WAPO_FTP_HOST')
user = os.getenv('WAPO_FTP_USER')
pw = os.getenv('WAPO_FTP_PASSWORD')

# Definition der max. Zeilen im CSV bis die Datei gelöscht wird
# Lesebeispiel: 3h * 6 Zeilen = 18 Zeilen, wenn die CSV Datei mehr als 18 Zeilen hat, wird diese gelöscht
# Das soll verhindern, dass die Datei unendlich anwächst aber trotzdem keine Datenlücke entsteht (3h Puffer)
ROWS_PER_HOUR = 6
MAX_HOURS = 3
MAX_ROWS = ROWS_PER_HOUR * MAX_HOURS

 # config
stations = [
    {
        "directory": '/domains/open-data-transfer.space/tecson/upload_mythenquai',
        "filename": 'Mythenquai_406m.csv',
        "output_file": os.path.join(__location__, 'messwerte_mythenquai_today.csv'),
    },
    {
        "directory": '/domains/open-data-transfer.space/tecson/upload_tiefenbrunnen',
        "filename": 'Tiefenbrunnen_406m.csv',
        "output_file": os.path.join(__location__, 'messwerte_tiefenbrunnen_today.csv'),
    },
]


class NoFileOnFTPServer(Exception):
    """
    This error is raised if there is currently on file on the FTP server to be loaded.
    """


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


def convert_csv_delim(output_path, input_path, input_delim=';', input_encoding='iso-8859-1'):
    rows = []
    with open(input_path, 'r', encoding=input_encoding) as f:
        reader = csv.DictReader(f, delimiter=input_delim)
        for r in reader:
            # strip keys and values of whitespace characters
            row = {k.strip(): v.strip() for k, v in r.items()}

            # skip row if the header is repeated
            if row['Datum/Zeit'] == 'Datum/Zeit':
                continue
            rows.append(row)

    header = [
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
    with open(output_path, 'w', newline='', encoding='utf-8') as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=header, delimiter=',', quoting=csv.QUOTE_MINIMAL)
        writer.writeheader()
        for row in rows:
            zurich_tz = pytz.timezone('Europe/Zurich')
            row_date = datetime.strptime(row['Datum/Zeit'], '%d.%m.%Y %H:%M:%S')
            date_cet = zurich_tz.localize(row_date)
            date_utc = date_cet.astimezone(pytz.utc)

            pressure_qfe = safefloat(row.get('Luftdruck QFE', ''))
            pressure_qnh = safefloat(row.get('Luftdruck QNH', ''))
            if not pressure_qfe and pressure_qnh:
                pressure_qfe = pressure_qnh - 47 # local pressure, QFE = QNH - 47hPa

            mapped_row = {
                'timestamp_utc': date_utc.isoformat(),
                'timestamp_cet': date_cet.isoformat(),
                'air_temperature': safefloat(row.get('Temp.1, 2m', '')),
                'water_temperature': safefloat(row.get('Temp. Wasser', '')),
                'wind_gust_max_10min': safefloat(row.get('WG m/s max.', '')),
                'wind_speed_avg_10min': safefloat(row.get('WG m/s avr.', '')),
                'wind_force_avg_10min': safefloat(row.get('Umr. Beaufort')),
                'wind_direction': safeint(row.get('WR vekt.', '')),
                'windchill': safefloat(row.get('Windchill', '')),
                'barometric_pressure_qfe': pressure_qfe,
                'precipitation': safefloat(row.get('Niederschlag', '')),
                'dew_point': safefloat(row.get('Taupunkt (°C)', row.get('Taupunkt', ''))),
                'global_radiation': safeint(row.get('Globalstrahlung', '')),
                'humidity': safefloat(row.get('rel. Feuchte', '')),
                'water_level': safefloat(row.get('Pegelstand', '')),
            }
            writer.writerow(mapped_row)
    return len(rows)


try:
    # login on FTP
    ftp = FTP(host, timeout=20)
    ftp.login(user, pw)

    for station in stations:
        # change to directory
        ftp.cwd(station['directory'])
        
        # check if file exists
        files_in_cwd = [f[0] for f in ftp.mlsd()]
        if station['filename'] not in files_in_cwd:
            raise NoFileOnFTPServer(f"File {station['filename']} not on FTP server in path {station['directory']}")

        # get data
        input_path = os.path.join(__location__, station['filename'])
        with open(input_path, 'wb') as fp:
            ftp.retrbinary(f"RETR {station['filename']}", fp.write)

        # convert files to UTF-8 with comma delimiter
        number_of_rows = convert_csv_delim(station['output_file'], input_path, input_delim=';', input_encoding='iso-8859-1')

        # let the file grow for a period, then delete it
        if number_of_rows > MAX_ROWS:
            # delete the file on the FTP if everything was okay until here
            ftp.delete(station['filename'])

    ftp.quit()

except Exception as e:
    print("Error: %s" % e, file=sys.stderr)
    print(traceback.format_exc(), file=sys.stderr)
    sys.exit(1)
