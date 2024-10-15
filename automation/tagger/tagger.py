# -*- coding: utf-8 -*-
"""Update tags on CKAN

Usage:
  tagger.py [--config <path-to-config-yaml>] [--no-verify]
  tagger.py (-h | --help)
  tagger.py --version

Options:
  -h, --help                         Show this screen.
  --version                          Show version.
  -c, --config <path-to-config-yaml> Path to YAML configuration file.
  --no-verify                        Option to disable SSL verification for requests.

"""

import os
import sys
import traceback
import yaml
from docopt import docopt
from ckanapi import RemoteCKAN, NotFound
from pprint import pprint
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())
arguments = docopt(__doc__, version='Update tags on CKAN 1.0')


__location__ = os.path.realpath(
    os.path.join(os.getcwd(), os.path.dirname(__file__))
)

try:
    config_path = arguments['--config']
    verify = not arguments['--no-verify']
    if not config_path:
        config_path = os.path.join(__location__, 'config.yml')

    config = None
    with open(config_path, 'r') as config_file:  # noqa
        config = yaml.safe_load(config_file)


    if not config:
        print("Config is empty", file=sys.stderr)
        sys.exit(1)


    BASE_URL = os.getenv('CKAN_BASE_URL')
    API_KEY = os.getenv('CKAN_API_KEY')
    ckan = RemoteCKAN(BASE_URL, apikey=API_KEY)
    for k, item in config.items():
        print(f"Process config {k}...")
        if not item:
            continue
        datasets = []

        # update single datasets
        for d in item.get('datasets', []):
            data = {'id': d}
            try:
                res = ckan.call_action('package_show', data, requests_kwargs={'verify': verify})
                tags = [t['name'] for t in res['tags']]
                tags.extend(item['tags'])
                tags_dict = [{'name': t} for t in tags]
                datasets.append({'id': res['name'], 'tags': tags_dict}) 
            except NotFound:
                print('Dataset %s not found!' % d, file=sys.stderr)
                raise

        # run queries to get list of datasets
        for q in item.get('queries', []):
            data = {'q': q}
            res = ckan.call_action('package_search', data, requests_kwargs={'verify': verify})
            for d in res['results']:
                tags = [{'name': t['name']} for t in d['tags']]
                tags.extend([{'name': t} for t in item['tags']])
                datasets.append({'id': d['name'], 'tags': tags})

        for d in datasets:
            print(f"Updating tags on dataset {d['id']} to {[t['name'] for t in d['tags']]}")
            try:
                ckan.call_action('package_patch', d, requests_kwargs={'verify': verify})
            except NotFound:
                print('Dataset %s not found!' % d, file=sys.stderr)
                raise
        print(f"Finished processing config {k}.")
except Exception as e:
    print("Error: %s" % e, file=sys.stderr)
    print(traceback.format_exc(), file=sys.stderr)
    sys.exit(1)
