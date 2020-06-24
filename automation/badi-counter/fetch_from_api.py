#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import csv
import traceback
from datetime import datetime
import pytz
import requests

# ZH slugs
zh_slugs = [
    'c5ed7c28b7b192',  # Freibad Allenmoos
    'c5ed7c2a3c5fa5',  # Freibad Auhof
    'c5eda072893782',  # Flussbad Au-Höngg
    'c5ed7c2be2e1d1',  # Freibad Heuried
    'c5ed7c330546ea',  # Seebad Katzensee
    'c5eb1917e9eedc',  # Freibad Letzigraben
    'c5ed7c35d2691a',  # Strandbad Mythenquai
    'c5ed7c38a83d5e',  # Flussbad Oberer Letten
    'c5ed7c3a043ac0',  # Freibad Seebach
    'c5ed7c3b370597',  # Frauenbad Stadthausquai
    'c5ed7c3c97c5c1',  # Strandbad Tiefenbrunnen
    'c5ed7c3ecaf50b',  # Flussbad Unterer Letten
    'c5ed7c4013bd69',  # Seebad Utoquai
    'c5ed7c41ae0016',  # Strandbad Wollishofen
    'c5ed7c2d6c3cfb',  # Freibad Zwischen den Hölzern
    'c5ed7c43707dff',  # Hallenbad Bläsi
    'c5ed7c44f09fcd',  # Hallenbad Bungertwies
    'c5eb19118e5824',  # Hallenbad City
    'c5ed7c466505e4',  # Hallenbad Leimbach
    'c5ed7c34806fc3',  # Hallenbad Oerlikon
    'c5ed7c47e86f10',  # Wärmebad Käferberg
]

zurich_tz = pytz.timezone('Europe/Zurich')

# get locations
page = 1
counters = []
count = 0

while page < 1000:  # stop at some point
    r = requests.get(
        'https://www.startupuniverse.ch/api/1.0/de/counters/list',
        params={'page': page}
    )
    resp = r.json()['response']
    if resp['data']:
        counters.extend(resp['data'])
        page += 1
        continue
    break

assert len(counters) == resp['found'], f"Data count does not match {len(counters)} != {resp['found']}"



try:
    field_names = [
        'date',
        'id',
        'slug',
        'name',
        'slug_badi_info',
        'status',
        'mode',
        'msg',
        'closed',
        'max',
        'occupancy_count',
        'waiting_count',
    ]
    writer = csv.DictWriter(sys.stdout, field_names, quoting=csv.QUOTE_NONNUMERIC)
    writer.writeheader()

    for counter in counters:
        if counter['slug'] in zh_slugs:
            rd = requests.get(
                f"https://www.startupuniverse.ch/api/1.0/de/counters/get/{counter['id']}",
            )
            data = rd.json()['response']['data']
            data['occupancy_count'] = data['counteritems'][0]['val']
            data['waiting_count'] = data['counteritems_waiting'][0]['val']

            timestamp = data['counteritems'][0]['ts_created']
            date = zurich_tz.localize(datetime.fromtimestamp(timestamp))
            data['date'] = date.isoformat()

            row = {f: data[f] for f in field_names}
            writer.writerow(row)
except Exception as e:
    print("Error: %s" % e, file=sys.stderr)
    print(traceback.format_exc(), file=sys.stderr)
    sys.exit(1)
finally:
    sys.stdout.flush()
