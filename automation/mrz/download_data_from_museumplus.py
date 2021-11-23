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
import requests
import museumpy
from docopt import docopt
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

arguments = docopt(__doc__, version='Download data from MuseumPlus 1.0')

base_url = os.getenv('MRZ_BASE_URL')
user = os.getenv('MRZ_USER')
pw = os.getenv('MRZ_PASS')
s = requests.Session()
s.auth = (user, pw)
s.headers.update({'Accept-Language': 'de'})

ZETCOM_NS = "http://www.zetcom.com/ria/ws/module"

def map_xml(record, xml_rec):
    parser = museumpy.xmlparse.XMLParser()
   
    def xml_text(xpath, rec=xml_rec):
        return parser.find(rec, xpath).text

    def xml_group(xpath, sep='; ', rec=xml_rec):
        groups = parser.findall(rec, xpath)
        return sep.join([g.text for g in groups])
    
    def map_mm_xml(mm_record, mm_xml):
        mm_record['bildnachweis'] = xml_text(
            f".//{{{ZETCOM_NS}}}dataField[@name='MulPhotocreditTxt']/{{{ZETCOM_NS}}}value",
            rec=mm_xml
        ) or ''
        mm_record['credits'] = xml_text(
            f".//{{{ZETCOM_NS}}}dataField[@name='MulRestrictionsClb']/{{{ZETCOM_NS}}}value",
            rec=mm_xml
        ) or ''
        mm_record['dateiname'] = xml_text(
            f".//{{{ZETCOM_NS}}}dataField[@name='MulOriginalFileTxt']/{{{ZETCOM_NS}}}value",
            rec=mm_xml
        ) or ''
        return mm_record

    # Multimedia 
    multimedia_id = record['refs']['Multimedia']['items'][0]['moduleItemId']
    mm_client = museumpy.MuseumPlusClient(
        base_url=base_url,
        map_function=map_mm_xml,
        session=s
    )
    mm_obj = mm_client.module_item(multimedia_id, 'Multimedia')

    # Material 
    material = []
    mat_recs = parser.findall(
        xml_rec,
        f".//{{{ZETCOM_NS}}}repeatableGroup[@name='ObjMaterialTechniqueGrp']/{{{ZETCOM_NS}}}repeatableGroupItem"
    )
    for mat_rec in mat_recs:
        mat_text = xml_text(
            f"./{{{ZETCOM_NS}}}dataField[@name='DetailsTxt']//{{{ZETCOM_NS}}}value",
            mat_rec
        )  or ''
        mat_notes = xml_text(
            f"./{{{ZETCOM_NS}}}dataField[@name='NotesClb']//{{{ZETCOM_NS}}}value",
            mat_rec
        )  or ''
        if mat_notes:
            material.append(f"{mat_text} (Bemerkung: {mat_notes})")
        else:
            material.append(mat_text)
    
    new_record = {
        'inventar_nummer': record['ObjObjectNumberTxt'],
        'bezeichnung': record['ObjObjectTitleGrp'],
        'kurzbeschreibung': record['ObjBriefDescriptionClb'],
        'datum': record['ObjDateTxt'],
        'bildnachweis': mm_obj['bildnachweis'],
        'dateiname': mm_obj['dateiname'].lower(),
        'credits': mm_obj['credits'],
        'urheber': xml_text(
            f".//{{{ZETCOM_NS}}}moduleReference[@name='ObjPerAssociationRef']"
            f"/{{{ZETCOM_NS}}}moduleReferenceItem"
            f"/{{{ZETCOM_NS}}}formattedValue"
        ) or '',
        'geo': xml_text(
            f".//{{{ZETCOM_NS}}}repeatableGroup[@name='ObjGeograficGrp']"
            f"//{{{ZETCOM_NS}}}vocabularyReference[@name='PlaceVoc']"
            f"//{{{ZETCOM_NS}}}formattedValue"
        ) or '',
        'masse': xml_text(
            f".//{{{ZETCOM_NS}}}repeatableGroup[@name='ObjDimAllGrp']"
            f"//{{{ZETCOM_NS}}}virtualField[@name='PreviewVrt']"
            f"//{{{ZETCOM_NS}}}value"
        ) or '',
        'sammlung': xml_text(
            f".//{{{ZETCOM_NS}}}vocabularyReference[@name='ObjMuseumCollectionVoc']"
            f"//{{{ZETCOM_NS}}}formattedValue"
        ) or '',
        'creditline': xml_text(
            f".//{{{ZETCOM_NS}}}repeatableGroup[@name='ObjCreditlineGrp']"
            f"//{{{ZETCOM_NS}}}dataField[@name='CreditlineTxt']"
            f"//{{{ZETCOM_NS}}}value"
        ) or '',
        'provenienz': xml_group(
            f".//{{{ZETCOM_NS}}}moduleReference[@name='ObjOwnershipRef']"
            f"/{{{ZETCOM_NS}}}moduleReferenceItem"
            f"/{{{ZETCOM_NS}}}formattedValue"
        ) or '',
        'literatur': xml_group(
            f".//{{{ZETCOM_NS}}}moduleReference[@name='ObjLiteratureRef']"
            f"/{{{ZETCOM_NS}}}moduleReferenceItem"
            f"/{{{ZETCOM_NS}}}formattedValue"
        ) or '',
        'material_technik': "; ".join(material),
    }
    
    return new_record.update(record)

try:
    search_client = museumpy.MuseumPlusClient(
        base_url=base_url,
        session=s
    )

    search_term = arguments['--search']
    group_result = search_client.search(
        field='OgrNameTxt',
        value=search_term,
        module='ObjectGroup'
    )
    assert group_result.count == 1, "More than one ObjectGroup found"
    group = group_result[0]['raw']
    ref = group['moduleItem']['moduleReference']

    client = museumpy.MuseumPlusClient(
        base_url=base_url,
        map_function=map_xml,
        session=s
    )
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
        'bildnachweis',
        'credits',
        'dateiname',
    ]
    writer = csv.DictWriter(
        sys.stdout,
        header,
        delimiter=',',
        quotechar='"',
        lineterminator='\r\n',
        quoting=csv.QUOTE_MINIMAL
    )
    writer.writeheader()
    for ref_item in ref['moduleReferenceItem']:
        row = client.module_item(ref_item['moduleItemId'], ref['targetModule'])
        writer.writerow(row)
except Exception as e:
    print("Error: %s" % e, file=sys.stderr)
    print(traceback.format_exc(), file=sys.stderr)
    sys.exit(1)
finally:
    sys.stdout.flush()

