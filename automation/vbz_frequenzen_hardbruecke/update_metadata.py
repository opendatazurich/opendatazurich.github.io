# -*- coding: utf-8 -*-
"""Update metadata on CKAN.

Usage:
  update_metadata.py --dataset <dataset-name>
  update_metadata.py (-h | --help)
  update_metadata.py --version

Options:
  -h, --help                   Show this screen.
  --version                    Show version.
  -d, --dataset <dataset-name> Name of the dataset to upload file to.

"""

import os
import sys
import traceback
from datetime import datetime
import pytz
from docopt import docopt
from ckanapi import RemoteCKAN, NotFound
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())
arguments = docopt(__doc__, version='Update metadata on CKAN 1.0')

try:
    BASE_URL = os.getenv('CKAN_BASE_URL')
    API_KEY = os.getenv('CKAN_API_KEY')
    ckan = RemoteCKAN(BASE_URL, apikey=API_KEY)

    dataset = arguments['--dataset']
    now_utc = pytz.utc.localize(datetime.utcnow())
    now_cet = now_utc.astimezone(pytz.timezone("Europe/Berlin"))
    data = {
        'id': dataset,
        'dateLastUpdated': now_cet.date().strftime('%d.%m.%Y')
    }
    print("Updating dateLastUpdated on dataset %s to %s" % (dataset, data['dateLastUpdated']))
    try:
        ckan.call_action('package_patch', data)
    except NotFound:
         print('Dataset %s not found!' % dataset, file=sys.stderr)
         raise
except Exception as e:
    print("Error: %s" % e, file=sys.stderr)
    print(traceback.format_exc(), file=sys.stderr)
    sys.exit(1)
