# -*- coding: utf-8 -*-
"""Convert a metadata xls file to a meta.xml

Usage:
  xls_to_meta_xml.py --file <path-to-file> [--outfile <path-to-file> --tag <pipeline-tag>]
  xls_to_meta_xml.py (-h | --help)
  xls_to_meta_xml.py --version

Options:
  -h, --help                   Show this screen.
  --version                    Show version.
  -f, --file <path-to-file>    Path to the xls file.
  -o, --outfile <path-to-file> Path to the output XML file [default: meta.xml].
  -t, --tag <pipeline-tag>     Optional: Name of the tag you want to add (gitlab or github)

"""

from docopt import docopt
import openpyxl
import xml.etree.ElementTree as ET
import codecs
import os
from datetime import date, datetime

arguments = docopt(__doc__, version='XLS to meta.xml 1.0')

__location__ = os.path.realpath(
    os.path.join(
        os.getcwd(),
        os.path.dirname(__file__)
    )
)

path = arguments['--file']
meta_xls = openpyxl.load_workbook(path)
ws = meta_xls['metadata']


class MetadataFieldMissingError(Exception):
    pass


# iterate over rows
metadata = {}
for row in ws.iter_rows():
    value = str(row[0].value) if row[0].value is not None else ''
    content = str(row[3].value) if row[3].value is not None else ''
    if value in ['bemerkungen', 'attributliste']:
        metadata[value] = []
        continue
    if value == 'bemerkung' and row[1].value and row[2].value: # nur wenn in Spalten B und C etwas steht
        metadata['bemerkungen'].append({
            'titel': str(row[1].value) if row[1].value is not None else '',
            'text': str(row[2].value) if row[2].value is not None else '',
        })
        continue
    if value == 'attributelement' and row[1].value and row[2].value and row[3].value: # nur wenn in Spalten B, C und D etwas steht
        metadata['attributliste'].append({
            'technischerfeldname': str(row[1].value) if row[1].value is not None else '',
            'sprechenderfeldname': str(row[2].value) if row[2].value is not None else '',
            'feldbeschreibung': str(row[3].value) if row[3].value is not None else '',
        })
        continue
    if value and isinstance(row[3].value, datetime):
        metadata[value] = row[3].value.strftime('%d.%m.%Y')
        continue
    if value and content:
        metadata[value] = content
        continue

# always override aktualisierungsdatum
metadata['aktualisierungsdatum'] = date.today().strftime('%d.%m.%Y')

# add a tag if given as argument
pipeline_tag = arguments['--tag']
if pipeline_tag:
    metadata["schlagworte"] = str(metadata["schlagworte"])+", "+pipeline_tag
    print(pipeline_tag, "als tag hinzugefügt")


# --- Normalisierung: kategorie -> wandle die Standardwerte der Harvester um zu lowercase + Umlaute ausgeschrieben ---
kat = (metadata.get('kategorie') or '').strip()
print("Input Kategorie(n): ", kat)
if kat:
    # lowercase
    kat_norm = kat.lower()
    # Umlaute/ß ersetzen
    for src, dst in {
        'ä': 'ae', 'ö': 'oe', 'ü': 'ue',
        'ß': 'ss',
        'Ä': 'Ae', 'Ö': 'Oe', 'Ü': 'Ue',
    }.items():
        kat_norm = kat_norm.replace(src, dst)
    # Mehrfach-Whitespace zu einfachem Space
    kat_norm = " ".join(kat_norm.split())
    metadata['kategorie'] = kat_norm
else:
    # Falls leer, explizit auf '' setzen, damit kein 'None' o.ä. entsteht
    metadata['kategorie'] = ''
      
print("Output Kategorie(n): ", metadata['kategorie'])

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


# Define optional fields
optional_fields = ['rechtsgrundlage', 'datentyp', 'aktuelle_version', 'datenqualitaet']
print("optional_fields: ", optional_fields)

root = ET.Element('datensammlung')
dataset = ET.SubElement(root, 'datensatz')


for field in fields:
    if field not in metadata:
        if field in optional_fields:
            print(f"Warnung: Optionales Feld '{field}' fehlt in den Metadaten.")
            if field == 'rechtsgrundlage':
                metadata[field] = ' ' # to prevent marking as "undefined" -> check with Liip, why
            else:
                metadata[field] = ''  # Set an empty string as default value
        else:
            raise MetadataFieldMissingError(field)

    item = ET.SubElement(dataset, field)
    # special treatment for Bemerkungen
    if field == 'bemerkungen':
        for d in metadata[field]:
            remark = ET.SubElement(item, 'bemerkung')
            for key, value in d.items():
                ET.SubElement(remark, key).text = value
        continue
    # special treatment for Attribute
    if field == 'attributliste':
        for d in metadata[field]:
            attribute = ET.SubElement(item, 'attributelement')
            attribute.set('technischerfeldname', d['technischerfeldname'])
            ET.SubElement(attribute, 'sprechenderfeldname').text = d['sprechenderfeldname']
            ET.SubElement(attribute, 'feldbeschreibung').text = d['feldbeschreibung']
        continue
    # all other fields on first level without deeper levels, like titel, beschreibung
    item.text = metadata.get(field, '')

meta_xml = ET.tostring(root, encoding="unicode")
outfile = arguments['--outfile']
if outfile:
    meta_path = outfile
else:
    meta_path = os.path.join(__location__, 'meta.xml')

with codecs.open(meta_path, 'w', 'utf-8-sig') as meta_file:
    meta_file.write(u"<?xml version='1.0' encoding='utf-8'?>")
    meta_file.write(meta_xml)

print(f"XML-Datei wurde erfolgreich erstellt: {meta_path}")
