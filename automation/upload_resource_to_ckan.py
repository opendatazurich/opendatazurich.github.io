# -*- coding: utf-8 -*-
"""Update resource to CKAN.

Usage:
  upload_resource_to_ckan.py --file <path-to-file> --dataset <dataset-name> [--no-verify]
  upload_resource_to_ckan.py (-h | --help)
  upload_resource_to_ckan.py --version

Options:
  -h, --help                  Show this screen.
  --version                   Show version.
  -f, --file <path-to-file>   Path to the file to upload.
  -d, --dataset <dataset-name> Name of the dataset to upload file to.
  --no-verify                  Option to disable SSL verification for requests.

"""

import os
import sys
import traceback
import requests
from docopt import docopt
from ckanapi import RemoteCKAN, NotFound
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())
arguments = docopt(__doc__, version='Upload resource to CKAN 1.0')

try:
    BASE_URL = os.getenv('CKAN_BASE_URL')
    API_KEY = os.getenv('CKAN_API_KEY')
    SSL_VERIFY = os.getenv('SSL_VERIFY')

    session = requests.Session()
    if SSL_VERIFY == "true":
        session.verify = True
    elif SSL_VERIFY == "false":
      session.verify = False
    else:
        session.verify = not arguments['--no-verify']
        
    ckan = RemoteCKAN(BASE_URL, session=session, apikey=API_KEY)

    path = arguments['--file']
    dataset = arguments['--dataset']

    filename = os.path.basename(path).lower()
    try:
        print("Getting dataset %s..." % dataset)
        ckan_dataset = ckan.call_action('package_show', {'id': dataset})
    except NotFound:
         print('Dataset %s not found!' % dataset, file=sys.stderr)
         sys.exit(1)

    resources = ckan_dataset['resources']
    existing = list(filter(lambda r: r['name'].lower() == filename, resources))
    if existing:
        res = existing[0]
        print("Updating existing resource %s" % res['name'])
      
        file_size_kb = os.path.getsize(path) / 1024
        print(f"The size of the file '{path}' is {file_size_kb:.2f} KB.")
      
        ckan.action.resource_update(
            id=res['id'],
            upload=open(path, "rb")
        )
    else:
        print("Create new resource %s" % filename)
        ckan.action.resource_create(
            package_id=ckan_dataset['id'],
            upload=open(path, "rb"),
            url='upload',
            name=filename
        )
except Exception as e:
    print("Error: %s" % e, file=sys.stderr)
    print(traceback.format_exc(), file=sys.stderr)
    sys.exit(1)
