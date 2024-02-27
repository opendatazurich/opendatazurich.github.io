# -*- coding: utf-8 -*-

import os
import sys
import csv
import traceback
from datetime import datetime, timedelta
import requests
from dotenv import load_dotenv, find_dotenv
# load_dotenv(find_dotenv())

user = os.getenv('VBZ_SSZ_USER_N')
pw = os.getenv('VBZ_SSZ_USER')
#user = os.getenv('VBZ_SSZ_USER')
#pw = os.getenv('VBZ_SSZ_PASSWORD')


try:
    url = "https://zuerich.pas.ch/v2/api/Auth/login"
    payload = {
        'username':user,  # ENTER THE USERNAME
        'password': pw,  # ENTER THE PASSWORD
    }
    print(url)
    print(user)

    bearer = requests.request("POST", url, json=payload)
    token = bearer.json()['accessToken']
    print(token)
    # get locations
    # s = requests.Session()
    # s.auth = (user, pw)
    # r = s.get('https://vbz.diamondreports.ch:8012/api/location')
    # r.raise_for_status()
    # locations = r.json()
    #
    # field_names = ['In', 'Out', 'Timestamp', 'Name']
    # writer = csv.DictWriter(sys.stdout, field_names, quoting=csv.QUOTE_NONNUMERIC)
    # writer.writeheader()
#
#     today = datetime.now().date()
#     total_days = 3
#     for loc in locations:
#         for day in range(total_days):
#             current_date = (today - timedelta(days=day))
#             cr = s.get(
#                 f"https://vbz.diamondreports.ch:8012/api/location/counter/{loc['Name']}",
#                 params={
#                     'aggregate': 5,
#                     'date': current_date.strftime('%Y%m%d')
#                 }
#             )
#             cr.raise_for_status()
#             counter = cr.json()
#             if len(counter['Counters']) == 0:
#                 continue
#
#             for obs in counter['Counters'][0]['Counts']:
#                 writer.writerow({
#                     'In': obs['In'],
#                     'Out': obs['Out'],
#                     'Timestamp': obs['Timestamp'],
#                     'Name': loc['Name']
#                 })

except Exception as e:
    print("Error: %s" % e, file=sys.stderr)
    print(traceback.format_exc(), file=sys.stderr)
    sys.exit(1)
finally:
    sys.stdout.flush()
