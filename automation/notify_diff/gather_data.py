import os
import sys
import re
import json
import csv
import chardet
from pprint import pprint
import requests
from ckanapi import RemoteCKAN
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

import urllib3
urllib3.disable_warnings()

__location__ = os.path.realpath(
    os.path.join(
        os.getcwd(),
        os.path.dirname(__file__)
    )
)

requests_kwargs = {"verify": False, "proxies": {}}

def convert_attributes(json_attr):
    # insert attributes
    try:
        attributes = json.loads(json_attr)
    except json.decoder.JSONDecodeError as e:
        print(f"Error: {e}", file=sys.stderr)
        attributes = []
    attrs = []
    for attribute in attributes:
        m = re.match(
            r"^(?P<name>.+?)(\s*\(technisch: (?P<tech_name>.+?)\))?$", attribute[0]
        )
        assert m, f"Could not match name and tech_name from {attribute[0]}"
        attr = {
            "description": attribute[1],
            "name": m["name"],
            "tech_name": m["tech_name"],
        }
        attrs.append(attr)
    return attrs

def get_csv_attributes(urls):
    # use the first URL
    print(f"   - Download resource from {urls[0]}")

    partial_path = os.path.join(__location__, 'partial.csv')
    download_partial_csv(urls[0], partial_path)

    partial_rows = rows_from_csv(partial_path, delimiter=',')
    return list(partial_rows[0].keys())

def download_partial_csv(url, path):
    remote = requests.Session()
    remote.verify = False # do not verify SSL certs

    print("Get ")
    r = remote.get(url, stream=True)
    with open(path, 'wb') as f:
        # break after some chunks
        total_chunks = 3
        for chunk in r.iter_lines(1024):
            f.write(chunk)
            f.write(b"\r\n")

            total_chunks -= 1
            if total_chunks == 0:
                break

def rows_from_csv(input_file, delimiter=';', input_encoding='detect'):
    if input_encoding == 'detect':
        input_encoding = _detect_file_encoding(input_file)

    with open(input_file, 'r', encoding=input_encoding) as f:
        # if a list of delimiters is given, try to sniff the correct one
        if isinstance(delimiter, list):
            dialect = csv.Sniffer().sniff(f.read(), delimiter)
            f.seek(0)
            reader = csv.DictReader(f, dialect=dialect)
        else:
            reader = csv.DictReader(f, delimiter=delimiter)
        rows = [r for r in reader]
    return rows


def _detect_file_encoding(input_file, line_count=20):
    with open(input_file, 'rb') as f:
        # read some lines
         rawdata = b''.join([f.readline() for _ in range(line_count)])
    return chardet.detect(rawdata)['encoding']


BASE_URL = os.getenv('CKAN_BASE_URL')
API_KEY = os.getenv('CKAN_API_KEY')
ckan = RemoteCKAN(BASE_URL, apikey=API_KEY)


# pagination
more_results = True
max_rows = 100
start = 0

rows = []
while(more_results):  
    results = ckan.call_action(
        "package_search", {"q": "res_format:csv -tags:geodaten", "start": start, "rows": max_rows}, requests_kwargs=requests_kwargs
    )
    start += max_rows
    if start > results['count']:
        more_results = False

    for dataset in results["results"]:
        print(f"Getting data from {dataset['name']}...")
        try:
            ckan_attributes = convert_attributes(dataset['sszFields'])
        except AssertionError as e:
            print(f"Error getting CKAN attributes: {e}")
            continue
        try:
            csv_attributes = get_csv_attributes([r['url'] for r in dataset['resources'] if r['format'].lower() == 'csv'])
        except (requests.HTTPError,IndexError) as e:
            print(f"Error getting CSV attributes: {e}")
            continue
        row = {
            "author": dataset["author"],
            "dataset_name": dataset['name'],
            "dataset_title": dataset['title'],
            "ckan_attributes": json.dumps([a['tech_name'] or a['name'] for a in ckan_attributes]),
            "csv_attributes": json.dumps(csv_attributes),
        }
        rows.append(row)
        print("")


csv_path = os.path.join(__location__, 'ckan_attributes.csv')
print(f"Save gathered data to CSV: {csv_path}")
with open(csv_path, 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(
        f,
        list(rows[0].keys()),
        delimiter=',',
        quotechar='"',
        lineterminator='\n',
        quoting=csv.QUOTE_MINIMAL
    )
    writer.writeheader()
    writer.writerows(rows)