#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Export CKAN metadata to CSVs for DK-ÜL import

Usage:
  ckan_to_dkuel.py --query <query> --output <path-to-dir> [--no-verify]
  ckan_to_dkuel.py (-h | --help)
  ckan_to_dkuel.py --version

Options:
  -h, --help                   Show this screen.
  --version                    Show version.
  -q, --query <query>          CKAN query to select the datasets for export.
  -o, --output <path-to-dir>   Path to output directory to save the CSVs
  --no-verify                  Option to disable SSL verification for requests.

"""

import os
import sys
import traceback
import re
import json
import collections
from datetime import datetime
from docopt import docopt
from ckanapi import RemoteCKAN, NotFound
import pandas as pd
from markdown import markdown
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())
arguments = docopt(__doc__, version="Export CKAN metadata to CSVs 1.0")

requests_kwargs = {}
if arguments["--no-verify"]:
    requests_kwargs = {"verify": False}


def map_metadata_to_rechtsgrundlage(metadata):
    return {
        "RGBezeichnung": metadata["legalInformation"],
    }

def convert_markdown(text):
    html = markdown(text)
    return html.replace("\n", " ")

def map_metadata_to_datenbestand(metadata):
    start, end = split_time_range(metadata["timeRange"])
    return {
        "DBMDQuellsystemID": metadata["name"],
        "DBMDQuellsystem": "Open-Data-Katalog der Stadt Zürich",
        "DBName": f"{metadata['title'][:50]}",
        "DBBeschreibung": convert_markdown(metadata["notes"]),
        "DBKategorie": ", ".join([g["title"] for g in metadata["groups"]]),
        "DBOGDRechtsgrundlagen": metadata["legalInformation"],
        "DBDienstabteilung": "SSZ",
        "DBDienstabteilungID": "4",
        "DBDatenlieferant": "SSZ",
        "DBDatenlieferantID": "4",
        "DBDatenvon": start,
        "DBDatenbis": end,
        "DBOGDPruefung": "Ja",
        "DBOGDStatus": "bereits veröffentlicht",
        "DBOGDStatusID": "72",
        "DBRisiken": metadata["dataQuality"],
        "DBMetadatenFreigabedatum": convert_date(metadata["dateFirstPublished"]),
        "DBAktualisierungsDatum": convert_date(metadata["dateLastUpdated"]),
        "DBAktualisierung": metadata["updateInterval"][0],
        "DBSchluesselwoerter": ", ".join([t["name"] for t in metadata["tags"]]),
        "DBOGDLizenz": metadata["license_id"],
        "DBBeschreibungBemerkungen": convert_markdown(ckan_metadata["sszBemerkungen"]),
        "StatusNummer": "1",
    }


def map_metadata_to_datenobjekt(metadata):
    start, end = split_time_range(metadata["timeRange"])
    return {
        "DOMDQuellsystemID": metadata["name"],
        "DOMDQuellsystem": "Open-Data-Katalog der Stadt Zürich",
        "DOuebergordneterDBID": metadata["name"],
        "DOName": metadata["title"],
        "DOBeschreibung": convert_markdown(metadata["notes"]),
        "DOKategorie": ", ".join([g["title"] for g in metadata["groups"]]),
        "DOOGDRechtsgrundlagen": metadata["legalInformation"],
        "DORaeumlicheBeziehung0": metadata["spatialRelationship"],
        "DODienstabteilung": metadata["url"],
        "DODatenlieferant": "SSZ",
        "DODatenlieferantID": "4",
        "DODatenvon": start,
        "DODatenbis": end,
        "DORisiken": metadata["dataQuality"],
        "DOMetadatenFreigabedatum": convert_date(metadata["dateFirstPublished"]),
        "DOAktualisierungsDatum": convert_date(metadata["dateLastUpdated"]),
        "DOAktualisierung": metadata["updateInterval"][0],
        "DOSchluesselwoerter": ", ".join([t["name"] for t in metadata["tags"]]),
        "DOOGDLizenz": metadata["license_id"],
        "DOBeschreibungBemerkungen": convert_markdown(ckan_metadata["sszBemerkungen"]),
        "DOOGDStatus": "bereits veröffentlicht",
        "DOOGDStatusID": "72",
        "StatusNummer": "1",
    }


def map_metadata_to_datenattribut(metadata):
    attributes = convert_attributes(metadata["sszFields"])
    export_attr = []
    for a in attributes:
        ogd_attr = {
            "DAMDQuellsystem": "Open-Data-Katalog der Stadt Zürich",
            "DAuebergordnetesDOID": metadata["name"],
            "DAtechFeldname": a['tech_name'],
            "DAName": f"{metadata['name']}: {a['name']}",
            "DABeschreibung": a['description'],
            "StatusNummer": "1",
        }
        export_attr.append(ogd_attr)
    return export_attr


def split_time_range(r):
    split_chars = ['bis', "-", "–", "seit"]
    for sc in split_chars:
        if sc in r:
            sr = r.split(sc, 1)
            assert len(sr) == 2
            return (sr[0].strip(), sr[1].strip())
    return (r, "")

def convert_date(d):
    if d:
        m = re.match(r"\d{2}\.\d{2}\.\d{4}", d)
        if m:
            return datetime.strptime(m[0], '%d.%m.%Y').date().isoformat()
    return d

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


try:
    BASE_URL = os.getenv("CKAN_BASE_URL")
    API_KEY = os.getenv("CKAN_API_KEY")
    ckan = RemoteCKAN(BASE_URL, apikey=API_KEY)

    # get datasets
    query = arguments["--query"]
    results = ckan.call_action(
        "package_search", {"q": query, "rows": 500}, requests_kwargs=requests_kwargs
    )

    rechtsgrundlagen = []
    datenbestaende = []
    datenobjekte = []
    datenattribute = []
    for dataset in results["results"]:
        print(f"Extracting metadata from dataset {dataset['title']}.")
        ckan_metadata = ckan.call_action(
            "package_show", {"id": dataset["id"]}, requests_kwargs=requests_kwargs
        )

        rechtsgrundlagen.append(map_metadata_to_rechtsgrundlage(ckan_metadata))
        datenbestaende.append(map_metadata_to_datenbestand(ckan_metadata))
        datenobjekte.append(map_metadata_to_datenobjekt(ckan_metadata))
        datenattribute.extend(map_metadata_to_datenattribut(ckan_metadata))

    # create dataframes
    df_rg = pd.DataFrame(rechtsgrundlagen)
    df_rg.groupby(["RGBezeichnung"], as_index=False).count().reset_index(drop=True)
    df_rg = df_rg[df_rg.RGBezeichnung != ""].reset_index(drop=True)

    df_db = pd.DataFrame(datenbestaende)
    df_do = pd.DataFrame(datenobjekte)
    df_da = pd.DataFrame(datenattribute)

    # export as CSV
    out = arguments["--output"]
    df_rg.to_csv(os.path.join(out, "01_ogd_rechtsgrundlagen.csv"), index=False)
    df_db.to_csv(os.path.join(out, "02_ogd_datenbestaende.csv"), index=False)
    df_do.to_csv(os.path.join(out, "03_ogd_datenobjekte.csv"), index=False)
    df_da.to_csv(os.path.join(out, "04_ogd_datenattribute.csv"), index=False)


except Exception as e:
    print("Error: %s" % e, file=sys.stderr)
    print(traceback.format_exc(), file=sys.stderr)
    sys.exit(1)