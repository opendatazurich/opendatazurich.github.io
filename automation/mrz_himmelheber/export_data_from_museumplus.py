# -*- coding: utf-8 -*-
"""Export data from MuseumPlus

Items are exported based on the search term saved at the specified path.

Usage:
  export_data_from_museumplus.py --search <search-term> --export <export-id> [--path <path-to-output>]
  export_data_from_museumplus.py (-h | --help)
  export_data_from_museumplus.py --version

Options:
  -h, --help                      Show this screen.
  --version                       Show version.
  -s, --search <search-term>      A search term to query MuseumPlus.
  -e, --export <export-id>        ID of the export in MuseumPlus.
  -p, --path <path-to-output>     Path to directory [default: .].

"""

import os
import sys
import traceback
import requests
import museumpy
from docopt import docopt
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

arguments = docopt(__doc__, version='Export data from MuseumPlus 1.0')

base_url = os.getenv('MRZ_BASE_URL')
user = os.getenv('MRZ_USER')
pw = os.getenv('MRZ_PASS')
s = requests.Session()
s.auth = (user, pw)
s.headers.update({'Accept-Language': 'de'})

try:
    client = museumpy.MuseumPlusClient(
        base_url=base_url,
        session=s
    )

    search_term = arguments['--search']
    group_result = client.search(
        field='OgrNameTxt',
        value=search_term,
        module='ObjectGroup'
    )
    assert group_result.count == 1, "More than one ObjectGroup found"
    item_id = group_result[0]['raw']['moduleItem']['id']

    ogd_export_id = arguments['--export'] # ID des Exports, definiert in MuseumPlus durch MRZ
    export_csv_path  = client.module_item_export(item_id, ogd_export_id, module='ObjectGroup')
    os.rename(export_csv_path, arguments['--path'])
except Exception as e:
    print("Error: %s" % e, file=sys.stderr)
    print(traceback.format_exc(), file=sys.stderr)
    sys.exit(1)
finally:
    sys.stdout.flush()

