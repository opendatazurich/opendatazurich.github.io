# -*- coding: utf-8 -*-
"""Fetch CSV from CKAN API

Usage:
  get_dummy_data.py --file <path-to-csv> --parquet <path-to-parquet> [--no-verify]
  get_dummy_data.py (-h | --help)
  get_dummy_data.py --version

Options:
  -h, --help                      Show this screen.
  --version                       Show version.
  -f, --file <path-to-csv>        Path to CSV file
  -p, --parquet <path-to-parquet> Path to parquet file
  --no-verify                     Option to disable SSL verification for reqests.

"""

import pandas as pd
import os
from docopt import docopt
from dotenv import load_dotenv, find_dotenv
import pyarrow
import fastparquet
from ckanapi import RemoteCKAN, NotFound
import ssl  
ssl._create_default_https_context = ssl._create_unverified_context

# Load environment variables from a .env file in the project directory
load_dotenv(find_dotenv())

# Parse command line arguments using docopt > __doc__ references to docstring (special attribute)
arguments = docopt(__doc__, version='Fetch CSV from CKAN API 1.0')
#
# # Get the absolute path of the current working directory
# __location__ = os.path.realpath(os.getcwd())
#
# # Join the current working directory path with a subdirectory named "data"
# path = os.path.join(__location__, "data")
#

# Getting dummy_resource.csv vom INT (dataset: dummy_dataset)
url = "https://data.integ.stadt-zuerich.ch/dataset/dummy_dataset/download/dummy_resource.csv"
res_pd = pd.read_csv(url)

# saving as csv
print("Saving csv")
csv_path = arguments['--file']
res_pd.to_csv(csv_path, index=False, encoding='utf-8', date_format='%Y-%m-%dT%H:%M:%SZ')

# saving as parquet
print("saving as parquet")
parquet_path = arguments['--parquet']
res_pd.to_parquet(parquet_path, index=False)
