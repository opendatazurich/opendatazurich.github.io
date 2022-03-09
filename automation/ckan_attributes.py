# -*- coding: utf-8 -*-
"""Extract STZH CKAN attributes to csv

Usage:
  ckan_attributes.py --dataset <dataset-name> --file <path-to-file> [--no-verify]
  ckan_attributes.py (-h | --help)
  ckan_attributes.py --version

Options:
  -h, --help                   Show this screen.
  --version                    Show version.
  -d, --dataset <dataset-name> Name of the dataset to extract the metadata.
  -f, --file <path-to-file>    Path to CSV file
  --no-verify                  Option to disable SSL verification for requests.

"""

import os
import sys
import traceback
import re
import json
import collections
import csv
from docopt import docopt
from ckanapi import RemoteCKAN, NotFound
from dotenv import load_dotenv, find_dotenv

__location__ = os.path.realpath(
    os.path.join(
        os.getcwd(),
        os.path.dirname(__file__)
    )
)

load_dotenv(find_dotenv())
arguments = docopt(__doc__, version='Extract attributes 1.0')

try:
    BASE_URL = os.getenv('CKAN_BASE_URL')
    API_KEY = os.getenv('CKAN_API_KEY')
    ckan = RemoteCKAN(BASE_URL, apikey=API_KEY)

    # CKAN metadata
    dataset = arguments['--dataset']
    data = {
        'id': dataset,
    }
    print(f"Extracting metadata from dataset {dataset}.")
    try:
        if arguments['--no-verify']:
            ckan_metadata = ckan.call_action('package_show', data, requests_kwargs={'verify': False})
        else:
            ckan_metadata = ckan.call_action('package_show', data)
    except NotFound:
         print('Dataset %s not found!' % dataset, file=sys.stderr)
         raise

    rows = []
    # insert attributes
    attributes = json.loads(ckan_metadata['sszFields'])
    for attribute in attributes:
        m = re.match(r'^(?P<name>.+?)\s*\(technisch: (?P<tech_name>.+?)\)$', attribute[0])
        assert m, f"Could not match name and tech_name from {attribute[0]}"
        row = {
            'dataset': dataset,
            'attribute_name': m['name'],
            'attribute_tech_name': m['tech_name'],
            'attribute_desc': attribute[1],
        }
        rows.append(row)

    # save the file
    with open(arguments['--file'], 'w') as csvfile:
        field_names = ['dataset', 'attribute_name', 'attribute_tech_name', 'attribute_desc']
        writer = csv.DictWriter(
            csvfile,
            field_names,
            delimiter=',',
            quotechar='"',
            lineterminator='\n',
            quoting=csv.QUOTE_MINIMAL
        )
        writer.writeheader()
        writer.writerows(rows)

    print(f"Saved metadata to {arguments['--file']}.")
    
except Exception as e:
    print("Error: %s" % e, file=sys.stderr)
    print(traceback.format_exc(), file=sys.stderr)
    sys.exit(1)
