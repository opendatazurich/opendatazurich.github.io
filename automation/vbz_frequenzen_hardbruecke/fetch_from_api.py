# -*- coding: utf-8 -*-

import os
import sys
import csv
import traceback
from datetime import datetime, date, timedelta
import requests
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

user = os.getenv('SSZ_USER')
pw = os.getenv('SSZ_PASS')

# get locations
r = requests.get('https://vbz.diamondreports.ch:8012/api/location', auth=(user, pw))
locations = r.json()

try:
    field_names = ['In', 'Out', 'Timestamp', 'Name']
    writer = csv.DictWriter(sys.stdout, field_names, quoting=csv.QUOTE_NONNUMERIC)
    writer.writeheader()

    start_date = date(2020, 1, 1)
    today = datetime.now().date()
    total_days = 366 
    for loc in locations:
        for day in range(total_days):
            current_date = (start_date + timedelta(days=day))
            if current_date > today:
                break
            cr = requests.get(
               'https://vbz.diamondreports.ch:8012/api/location/counter/%s' % loc['Name'],
                auth=(user, pw),
                params={
                    'aggregate': 5,
                    'date': current_date.strftime('%Y%m%d')
                }
            )
            counter = cr.json()
            if len(counter['Counters']) == 0:
                continue

            for obs in counter['Counters'][0]['Counts']:
                writer.writerow({
                    'In': obs['In'],
                    'Out': obs['Out'],
                    'Timestamp': obs['Timestamp'],
                    'Name': loc['Name']
                })
except Exception as e:
    print("Error: %s" % e, file=sys.stderr)
    print(traceback.format_exc(), file=sys.stderr)
    sys.exit(1)
finally:
    sys.stdout.flush()
