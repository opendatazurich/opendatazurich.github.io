# -*- coding: utf-8 -*-

import os
import sys
import csv
import traceback
from datetime import datetime, timedelta
import requests
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

user = os.getenv('SSZ_USER')
pw = os.getenv('SSZ_PASS')

start_date = 20240101                 # ENTER THE START DATE in YYYYMMDD FORMAT
end_date = 202403045                  # ENTER THE END DATE in YYYYMMDD FORMAT
granularity = "FiveMinutes"           # change granularity if needed (e.g. "Hour")
required_location_names = ["TVH Ost", "TVH West"] # Ost und West separat

today = datetime.today()
start_date = today - timedelta(days=3)
start_date = start_date.strftime("%Y%m%d")
end_date = today - timedelta(days=1)
end_date = end_date.strftime("%Y%m%d")

#user = os.getenv('VBZ_SSZ_USER')
#pw = os.getenv('VBZ_SSZ_PASSWORD')

try:






except Exception as e:
    print("Error: %s" % e, file=sys.stderr)
    print(traceback.format_exc(), file=sys.stderr)
    sys.exit(1)
finally:
    sys.stdout.flush()
