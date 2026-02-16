# -*- coding: utf-8 -*-
"""Export data from MuseumPlus

Items are exported based on the export id and saved at the specified path.

Usage:
  download_export.py --export <export-id> --item-id <item-id> --module <module> --field <field> --dir <dir> --limit <limit> --filename <filename>
  download_export.py (-h | --help)
  download_export.py --version

Options:
  -h, --help                      Show this screen.
  --version                       Show version.
  -e, --export <export-id>        ID of the export in MuseumPlus.
  -i, --item-id <item-id>         ID of the item in MuseumPlus.
  -m, --module <module>           Module name in MuseumPlus.
  -f, --field <field>             Field name in MuseumPlus.
  -d, --dir <dir>                 Directory to write fi
  -l, --limit <limit>             Maximum number of records to pull from MuseumPlus.
  -fn, --filename <filename>      Name of the downloaded file.

"""

import os
import requests
import museumpy
from docopt import docopt
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())


# get arguments
arguments = docopt(__doc__, version='Export data from MuseumPlus 1.0')

item_id = arguments['--item-id'] #"51030"
ogd_export_id = arguments['--export'] #"71028"
module = arguments['--module'] #"Object"
field = arguments['--field'] #"ObjObjectGroupsRef"
data_dir = arguments['--dir'] # 'automation/mrz_kamerun_objekte/export'
limit = arguments['--limit'] #1000
output_filepath = os.path.join(data_dir, arguments['--filename'])


# get environment variables
base_url = os.getenv('MRZ_BASE_URL')
user = os.getenv('MRZ_USER')
pw = os.getenv('MRZ_PASS')


# connect to api
s = requests.Session()
s.auth = (user, pw)
s.headers.update({
    "Accept-Language": "de",
})
client = museumpy.MuseumPlusClient(
    base_url=base_url,
    session=s
)


# files will be saved in sub directory
os.makedirs(data_dir, exist_ok=True)


# download the export
filepath = client.module_export(module=module, field=field, value=item_id,  export_id=ogd_export_id, limit=limit, dir=data_dir)
print("Downloaded to:", filepath)


# exports come with uuid filename. We rename them, so we can find them easier in subsequent workflows
if os.path.exists(output_filepath):
    os.remove(output_filepath) # if file exits, delete it
os.rename(filepath, output_filepath)
print("Renamed to", output_filepath)

