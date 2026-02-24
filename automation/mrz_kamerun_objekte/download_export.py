# -*- coding: utf-8 -*-
"""
Export data from MuseumPlus.

Items are exported based on the export id and saved at the specified path.

Example:
    python download_export.py \
        --export 71028 \
        --item-id 51030 \
        --module Object \
        --field ObjObjectGroupsRef \
        --dir automation/mrz_kamerun_objekte/export \
        --limit 1000 \
        --filename kamerun.json
"""

import argparse
import os
import requests
import museumpy
from dotenv import load_dotenv, find_dotenv


def parse_args():
    parser = argparse.ArgumentParser(
        description="Download an export from MuseumPlus."
    )

    parser.add_argument(
        "--export", "-e",
        required=True,
        help="ID of the export in MuseumPlus."
    )

    parser.add_argument(
        "--item-id", "-i",
        required=True,
        help="ID of the item in MuseumPlus."
    )

    parser.add_argument(
        "--module", "-m",
        required=True,
        help="Module name in MuseumPlus."
    )

    parser.add_argument(
        "--field", "-f",
        required=True,
        help="Field name in MuseumPlus."
    )

    parser.add_argument(
        "--dir", "-d",
        required=True,
        help="Directory to save the file."
    )

    parser.add_argument(
        "--limit", "-l",
        required=True,
        help="Maximum number of records to pull."
    )

    parser.add_argument(
        "--filename", "-fn",
        required=True,
        help="Output filename."
    )

    parser.add_argument(
        "--version",
        action="version",
        version="Export data from MuseumPlus 1.0"
    )

    return parser.parse_args()


def main():
    load_dotenv(find_dotenv())
    args = parse_args()

    item_id = args.item_id
    ogd_export_id = args.export
    module = args.module
    field = args.field
    data_dir = args.dir
    limit = args.limit
    output_filepath = os.path.join(data_dir, args.filename)

    # env vars
    base_url = os.getenv("MRZ_BASE_URL")
    user = os.getenv("MRZ_USER")
    pw = os.getenv("MRZ_PASS")

    # connect to API
    s = requests.Session()
    s.auth = (user, pw)
    s.headers.update({
        "Accept-Language": "de",
    })

    client = museumpy.MuseumPlusClient(
        base_url=base_url,
        session=s
    )

    # ensure directory exists
    os.makedirs(data_dir, exist_ok=True)

    # download the export
    filepath = client.module_export(
        module=module,
        field=field,
        value=item_id,
        export_id=ogd_export_id,
        limit=limit,
        dir=data_dir
    )
    print("Downloaded to:", filepath)

    # clean rename
    if os.path.exists(output_filepath):
        os.remove(output_filepath)

    os.rename(filepath, output_filepath)
    print("Renamed to", output_filepath)


if __name__ == "__main__":
    main()
