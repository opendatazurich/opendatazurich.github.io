# -*- coding: utf-8 -*-
"""Fetch CSV from CKAN API

Usage:
  fetch_from_api.py --file <path-to-csv> [--no-verify]
  fetch_from_api.py (-h | --help)
  fetch_from_api.py --version

Options:
  -h, --help                      Show this screen.
  --version                       Show version.
  -f, --file <path-to-csv>        Path to CSV file
  -g, --geojson <path-to-geojson> Path to GeoJSON file
  --no-verify                     Option to disable SSL verification for reqests.

"""

import pandas as pd
import os
from docopt import docopt
from dotenv import load_dotenv, find_dotenv

# Load environment variables from a .env file in the project directory
load_dotenv(find_dotenv())

# Parse command line arguments using docopt > __doc__ references to docstring (special attribute)
arguments = docopt(__doc__, version='Fetch CSV from CKAN API 1.0')

# Get the absolute path of the current working directory
__location__ = os.path.realpath(os.getcwd())

# Join the current working directory path with a subdirectory named "data"
path = os.path.join(__location__, "data")

# ckan instance
BASE_URL_PROD = "https://data.stadt-zuerich.ch"
ckan_prod = RemoteCKAN(BASE_URL_PROD)


# mapping ckan metadata attributes to metadata fields
def subsetting_datasets(metadata):
    return{
        'titel': metadata['title'],
        'beschreibung': metadata['notes'],
        'kategorie': ", ".join([g['title'] for g in metadata['groups']]),
        'raeumliche_beziehung': metadata['spatialRelationship'],
        'quelle': metadata['author'],
        'zeitraum': metadata['timeRange'],
        'datentyp': ','.join(metadata['dataType']),
        'aktualisierungsdatum': ','.join(metadata['updateInterval']),
        'dataset_name': metadata['name'],
        'dataset_id': metadata['id'],
        'license_id': metadata['license_id'],
        'anzahl_ressourcen': metadata['num_resources']

        ## fields not used in metadata dataset
        # 'schlagworte': ", ".join([g['name'] for g in metadata['tags']]),
        # 'lieferant': metadata['dateLastUpdated'],
	    # 'dataQuality': metadata['dataQuality'],
        # 'maintainer_email': metadata['maintainer_email'],
        # sszFields will no be mapped
        # 'sszBemerkungen': metadata['sszBemerkungen'], # not in all datasets
        # 'state': metadata['state'],
        #'dateFirstPublished':  metadata['dateFirstPublished'], # would be cool do integrate this field
        # 'version': metadata['version'],
        # 'num_tags': metadata['num_tags'],
        # # 'legalInformation': metadata['legalInformation'],
        # 'license_id': metadata['license_id'],
        # 'license_title': metadata['license_title'],
        # 'license_url': metadata['license_url'],
        # 'maintainer': metadata['maintainer'],
        # organization will not be mapped
        # 'owner_org': metadata['owner_org'],
        # 'url': metadata['url'],
        # 'data_publisher': metadata['data_publisher'],
        # 'metadata_created': metadata['metadata_created'],
        # 'metadata_modified': metadata['metadata_modified']
    }


# get all metadata measurements
print("Get all packages from ckan")
all_pkgs = ckan_prod.call_action("package_list")
len(all_pkgs)

# get medatadata of all pkgs and write it to empty list if type == dataset
print("Subsetting package and retrieving metadata")
all_details = [] # initialising empty list
for p in all_pkgs:
    p_detail = ckan_prod.call_action('package_show', {"id":p})
    if p_detail['type'] == 'dataset' and p_detail['private'] == False:
        p_detail['package_name'] = p
        all_details.append(subsetting_datasets(p_detail))

# list to csv
res_pd = pd.DataFrame(all_details)

# TODO getting around with encoding

# saving as csv
print("Saving csv")
csv_path = arguments['--file']
res_pd.to_csv(csv_path, index=False, encoding='utf-8', date_format='%Y-%m-%dT%H:%M:%SZ')

