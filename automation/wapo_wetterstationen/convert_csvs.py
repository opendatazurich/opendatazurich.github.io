#!/usr/bin/env python3
"""Convert Tecson/Namnick CSV to our CSV format

Usage:
  convert_csvs.py --input <path-to-file> --output <path-to-file>
  convert_csvs.py (-h | --help)
  convert_csvs.py --version

Options:
  -h, --help                   Show this screen.
  --version                    Show version.
  -i, --input <path-to-file>   Path to input CSV file
  -o, --output <path-to-file>  Path to output CSV file

"""

from datetime import datetime
import pytz
import csv
import traceback
import os
import sys
from docopt import docopt


arguments = docopt(__doc__, version='Convert Tecson/Namnick CSV to our CSV format 1.0')
__location__ = os.path.realpath(
    os.path.join(
        os.getcwd(),
        os.path.dirname(__file__)
    )
)

# Method to convert string to floating point (if possible)
def safefloat(s):
    if not s:
        return s
    return float(s)


# Method to convert string to integer (if possible)
def safeint(s):
    if not s:
        return s
    f = float(s)
    r = round(f)
    if f == r:
        return int(f)
    else:
        raise ValueError(f"Can't parse {s} as int without losing precision")


# Method to convert the Tecson-CSV (with semicolon, ISO-8859-1 encoding) to a OGD CSV (comma-separated, UTF-8)
def convert_csv_delim(output_path, input_path, input_delim=';', input_encoding='iso-8859-1'):
    with open(input_path, 'r', encoding=input_encoding) as f:
        reader = csv.DictReader(f, delimiter=input_delim)
        rows = []
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
            # add new column for UTC date
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


try:
    input_path = arguments['--input']
    output_path = arguments['--output']
    convert_csv_delim(output_path, input_path)
except Exception as e:
    print("Error: %s" % e, file=sys.stderr)
    print(traceback.format_exc(), file=sys.stderr)
    sys.exit(1)
