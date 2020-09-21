# -*- coding: utf-8 -*-

"""Convert meta.xml to a python dict

Usage:
  read_meta_xml.py [--file <path-to-file>] [--json]
  read_meta_xml.py (-h | --help)
  read_meta_xml.py --version

Options:
  -h, --help                  Show this screen.
  --version                   Show version.
  -f, --file <path-to-file>   Path to the XML file [default: meta.xml].
  --json                      Output the xml file as JSON

"""

from docopt import docopt
import os
import xmlparse
from datetime import date
import json
from pprint import pprint



def read_meta_xml(path):

    dataset_node = None
    xmlparser = xmlparse.XMLParser()
    with open(path, 'r') as f:
        meta_xml = xmlparser.parse(f.read())
        dataset_node = meta_xml.find('datensatz')

    if not dataset_node:
        return None

    return {
        'titel': dataset_node.find('titel').text,
        'beschreibung': dataset_node.find('beschreibung').text,
        'rechtsgrundlage': dataset_node.find('rechtsgrundlage').text,
        'raeumliche_beziehung': dataset_node.find('raeumliche_beziehung').text,
        'lieferant': dataset_node.find('lieferant').text,
        'quelle': dataset_node.find('quelle').text,
        'zeitraum': dataset_node.find('zeitraum').text,
        'datenqualitaet': dataset_node.find('datenqualitaet').text,
        'erstmalige_veroeffentlichung': dataset_node.find('erstmalige_veroeffentlichung').text,
        'aktualisierungsdatum': dataset_node.find('aktualisierungsdatum').text or date.today().strftime('%d.%m.%Y'),
        'aktuelle_version': dataset_node.find('aktuelle_version').text,
        'lizenz': dataset_node.find('lizenz').text or 'cc-zero',
        'datentyp': dataset_node.find('datentyp').text,
        'maintainer': 'Open Data Zürich',
        'maintainer_email': 'opendata@zuerich.ch',
        'bemerkungen': convert_comments(dataset_node),
        'kategorie': list_from_commas(dataset_node, 'kategorie'),
        'aktualisierungsintervall': convert_interval(dataset_node),
        'schlagworte': list_from_commas(dataset_node, 'schlagworte'),
        'attributliste': convert_attributes(dataset_node),
    }

def convert_comments(node):
    comment_nodes = node.find('bemerkungen')
    if comment_nodes is None:
        return None

    comments = []
    for comment_node in comment_nodes:
        comment = {}
        comment['title'] = comment_node.find('titel').text
        comment['text'] = comment_node.find('text').text
        
        comment['link'] = {}
        link = comment_node.find('link')
        if link is not None:
            comment['link']['label'] = link.find('label').text
            comment['link']['url'] = link.find('url').text
        comments.append(comment)
    return comments

def list_from_commas(node, field):
    categories = node.find(field).text
    return categories.split(', ')

def convert_interval(node):
    interval = (
        node.find('aktualisierungsintervall').text
        .replace(u'ä', u'ae')
        .replace(u'ö', u'oe')
        .replace(u'ü', u'ue')
    )
    return interval

def convert_attributes(node):
    attribut_list = node.find('attributliste')
    attributes = []
    for attribut in attribut_list:
        tech_name = attribut.get('technischerfeldname')
        speak_name = attribut.find('sprechenderfeldname').text

        if tech_name:
            attribute_name = '%s (technisch: %s)' % (speak_name, tech_name)
        else:
            attribute_name = speak_name

        attributes.append(
            (
                attribute_name,
                attribut.find('feldbeschreibung').text
            )
        )
    return attributes

if __name__ == "__main__":
    arguments = docopt(__doc__, version='read_meta_xml 1.0')

    d = read_meta_xml(arguments['--file'])
    if arguments['--json']:
        print(json.dumps(d, indent=4, sort_keys=True))
    else:
        pprint(d)
