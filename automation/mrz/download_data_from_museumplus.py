# -*- coding: utf-8 -*-
"""Download data from MuseumPlus

Items are downloaded based on the search term and attachments are saved in the specified directory.

Usage:
  download_data_from_museumplus.py --search <search-term> [--attachments <path-to-dir>]
  download_data_from_museumplus.py (-h | --help)
  download_data_from_museumplus.py --version

Options:
  -h, --help                      Show this screen.
  --version                       Show version.
  -s, --search <search-term>      A search term to query MuseumPlus.
  -a, --attachments <path-to-dir> Path to directory [default: .].

"""

import os
import sys
import traceback
from pprint import pprint
import csv
from random import randint
from time import sleep
import museumpy
from docopt import docopt
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

arguments = docopt(__doc__, version='Download data from MuseumPlus 1.0')

base_url = os.getenv('MRZ_BASE_URL')
user = os.getenv('MRZ_USER')
pw = os.getenv('MRZ_PASS')


def map_to_csv(item):
    mapped_record = {
	'inventar_nummer': item['ObjObjectNumberTxt'],
	'bezeichnung': item['ObjObjectTitleGrp'],
	'urheber': item['ObjPerAssociationRef'],
	'geo':  item['ObjGeograficGrp'],
	'datum': item['ObjDateTxt'],
	'masse': item['ObjDimAllGrp'],
	'material_technik': item['ObjMaterialTechniqueGrp'],
	'sammlung': '',
	'creditline': item['ObjCreditlineGrp'],
	'provenienz': item['ObjOwnershipRef'],
	'kurzbeschreibung': item['ObjScientificNotesClb'],
	'literatur': item['ObjLiteratureRef'],
	'bildunterschrift': item['ObjMultimediaRef'],
    }
    return mapped_record

try:
    client = museumpy.MuseumPlusClient(
        base_url=base_url,
        requests_kwargs={'auth': (user, pw)}
    )

    search_term = arguments['--search']
    group_result = client.search(
        field='OgrNameTxt',
        value=search_term,
        module='ObjectGroup'
    )
    assert group_result.count == 1, "More than one ObjectGroup found"
    group = group_result[0]['raw']
    ref = group['moduleItem']['moduleReference']

    header = [
        'inventar_nummer',
        'bezeichnung',
        'urheber',
        'geo',
        'datum',
        'masse',
        'material_technik',
        'sammlung',
        'creditline',
        'provenienz',
        'kurzbeschreibung',
        'literatur',
        'bildunterschrift',
        'dateiname',
    ]
    writer = csv.DictWriter(
        sys.stdout,
        header,
        delimiter=',',
        quotechar='"',
        lineterminator='\n',
        quoting=csv.QUOTE_MINIMAL
    )
    writer.writeheader()
    for ref_item in ref['moduleReferenceItem']:
        item = client.module_item(ref_item['moduleItemId'], ref['targetModule'])
        if item['hasAttachments'] == 'true':
            attachment_path = client.download_attachment(ref_item['moduleItemId'], ref['targetModule'], arguments['--attachments'])
        sleep(randint(1,3))
        row = map_to_csv(item)
        row['dateiname'] = os.path.basename(attachment_path)
        writer.writerow(row)
except Exception as e:
    print("Error: %s" % e, file=sys.stderr)
    print(traceback.format_exc(), file=sys.stderr)
    sys.exit(1)
finally:
    sys.stdout.flush()

