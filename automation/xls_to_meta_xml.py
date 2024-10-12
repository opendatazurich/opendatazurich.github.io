# -*- coding: utf-8 -*-
"""Convert a metadata xls file to a meta.xml

Usage:
  xls_to_meta_xml.py --file <path-to-file> [--outfile <path-to-file>]
  xls_to_meta_xml.py (-h | --help)
  xls_to_meta_xml.py --version

Options:
  -h, --help                   Show this screen.
  --version                    Show version.
  -f, --file <path-to-file>    Path to the xls file.
  -o, --outfile <path-to-file> Path to the output XML file [default: meta.xml].

"""

from docopt import docopt
import xlrd
# xlrd quickfix: https://stackoverflow.com/questions/64264563/attributeerror-elementtree-object-has-no-attribute-getiterator-when-trying
xlrd.xlsx.ensure_elementtree_imported(False, None)
xlrd.xlsx.Element_has_iter = True
import xml.etree.ElementTree as ET
import codecs
import os
from datetime import date


arguments = docopt(__doc__, version='XLS to meta.xml 1.0')

__location__ = os.path.realpath(
    os.path.join(
        os.getcwd(),
        os.path.dirname(__file__)
    )
)

path = arguments['--file']
meta_xls = xlrd.open_workbook(path)
metadata_sheet = meta_xls.sheet_by_name('metadata')


class MetadataFieldMissingError(Exception):
    pass


# iterate over rows
metadata = {}
for row_num in range(1, metadata_sheet.nrows):
    value = str(metadata_sheet.cell_value(row_num, 0))
    if value in ['bemerkungen', 'attributliste']:
        metadata[value] = []
        continue
    if value == 'bemerkung':
        metadata['bemerkungen'].append({
            'titel': str(metadata_sheet.cell_value(row_num, 1)),
            'text': str(metadata_sheet.cell_value(row_num, 2)),
        })
        continue
    if value == 'attributelement':
        metadata['attributliste'].append({
            'technischerfeldname': str(metadata_sheet.cell_value(row_num, 1)),
            'sprechenderfeldname': str(metadata_sheet.cell_value(row_num, 2)),
            'feldbeschreibung': str(metadata_sheet.cell_value(row_num, 3)),
        })
        continue
    if value:
        metadata[value] = str(metadata_sheet.cell_value(row_num, 3))
        continue

# always override aktualisierungsdatum
metadata['aktualisierungsdatum'] = date.today().strftime('%d.%m.%Y')

fields = [
    'titel',
    'beschreibung',
    'kategorie',
    'rechtsgrundlage',
    'raeumliche_beziehung',
    'lieferant',
    'quelle',
    'zeitraum',
    'datenqualitaet',
    'erstmalige_veroeffentlichung',
    'aktualisierungsdatum',
    'datentyp',
    'aktualisierungsintervall',
    'schlagworte',
    'aktuelle_version',
    'lizenz',
    'bemerkungen',
    'attributliste',
]


root = ET.Element('datensammlung')
dataset = ET.SubElement(root, 'datensatz')


for field in fields:
    if field not in metadata:
        raise MetadataFieldMissingError(field)
    
    item = ET.SubElement(dataset, field)
    
    if field == 'bemerkungen':
        for d in metadata[field]:
            remark = ET.SubElement(item, 'bemerkung')
            for key, value in d.items():
                ET.SubElement(remark, key).text = value
        continue
    
    if field == 'attributliste':
        for d in metadata[field]:
            attribute = ET.SubElement(item, 'attributelement')
            attribute.set('technischerfeldname', d['technischerfeldname'])
            ET.SubElement(attribute, 'sprechenderfeldname').text = d['sprechenderfeldname']
            ET.SubElement(attribute, 'feldbeschreibung').text = d['feldbeschreibung']
        continue
    
    item.text = metadata[field]

meta_xml = ET.tostring(root, encoding="unicode")
outfile = arguments['--outfile']
if outfile:
    meta_path = outfile
else:
    meta_path = os.path.join(__location__, 'meta.xml')

with codecs.open(meta_path, 'w', 'utf-8-sig') as meta_file:
    meta_file.write(u"<?xml version='1.0' encoding='utf-8'?>")
    meta_file.write(meta_xml)
