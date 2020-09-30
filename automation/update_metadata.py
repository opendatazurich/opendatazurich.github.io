# -*- coding: utf-8 -*-
"""Update metadata on CKAN.

Usage:
  update_metadata.py --dataset <dataset-name> --file <path-to-file> [--no-verify]
  update_metadata.py (-h | --help)
  update_metadata.py --version

Options:
  -h, --help                   Show this screen.
  --version                    Show version.
  -d, --dataset <dataset-name> Name of the dataset to upload file to.
  -f, --file <path-to-file>    Path to meta.xml file.
  --no-verify                  Option to disable SSL verification for requests.

"""

import os
import sys
import traceback
from datetime import datetime
import pytz
import json
from docopt import docopt
from ckanapi import RemoteCKAN, NotFound
from pprint import pprint
import read_meta_xml
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())
arguments = docopt(__doc__, version='Update metadata on CKAN 1.0')


def map_metadata_to_ckan(metadata):
    return {
        'title': metadata['titel'],
        'url': metadata['lieferant'],
        'notes': metadata['beschreibung'],
        'author': metadata['quelle'],
        'license_id': metadata['lizenz'],
        'spatialRelationship': metadata['raeumliche_beziehung'],
        'dateFirstPublished': metadata['erstmalige_veroeffentlichung'],
        'dateLastUpdated': metadata['aktualisierungsdatum'],
        'updateInterval': metadata['aktualisierungsintervall'],
        'dataType': metadata['datentyp'],
        'dataQuality': metadata['datenqualitaet'],
        'legalInformation': metadata['rechtsgrundlage'],
        'version': metadata['aktuelle_version'],
        'timeRange': metadata['zeitraum'],
        'maintainer': 'Open Data Zürich',
        'maintainer_email': 'opendata@zuerich.ch',
        'tags': [{'name': t} for t in metadata['schlagworte']],
        'groups': [{'name': k} for k in metadata['kategorie']],
        'sszBemerkungen': convert_comments(metadata['bemerkungen']),
        'sszFields': json.dumps([(k, v) for k, v in metadata['attributliste'] if v]),
        #'extras': [],
    }

def convert_comments(comments):
    if comments is None:
       return None
    markdown = ''
    for comment in comments:
        if comment.get('title'):
            markdown += f"**{comment['title']}**\n\n"
        if comment.get('text'):
            markdown += f"{comment['text']}\n\n"
        if comment.get('link'):
            label = comment['link'].get('label')
            url = comment['link'].get('url')
            markdown += f"[{label}]({url})\n\n"
    return markdown 


try:
    BASE_URL = os.getenv('CKAN_BASE_URL')
    API_KEY = os.getenv('CKAN_API_KEY')
    ckan = RemoteCKAN(BASE_URL, apikey=API_KEY)

    # meta.xml
    meta_xml_path = arguments['--file']
    meta = read_meta_xml.read_meta_xml(meta_xml_path)
    ckan_metadata = map_metadata_to_ckan(meta)

    dataset = arguments['--dataset']
    now_utc = pytz.utc.localize(datetime.utcnow())
    now_cet = now_utc.astimezone(pytz.timezone("Europe/Berlin"))
    data = {
        'id': dataset,
        'dateLastUpdated': now_cet.date().strftime('%d.%m.%Y')
    }
    data.update(ckan_metadata)
    print(f"Updating metadata on dataset {dataset} to {pprint(data)}")
    try:
        if arguments['--no-verify']:
            ckan.call_action('package_patch', data, requests_kwargs={'verify': False})
        else:
            ckan.call_action('package_patch', data)
    except NotFound:
         print('Dataset %s not found!' % dataset, file=sys.stderr)
         raise
except Exception as e:
    print("Error: %s" % e, file=sys.stderr)
    print(traceback.format_exc(), file=sys.stderr)
    sys.exit(1)
