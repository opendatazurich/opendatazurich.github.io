# -*- coding: utf-8 -*-

import requests
from bs4 import BeautifulSoup
import sqlite3
import re
from urllib.parse import urljoin
import dateparser
import sys
import os
import traceback
from datetime import datetime


__location__ = os.path.realpath(
    os.path.join(
        os.getcwd(),
        os.path.dirname(__file__)
    )
)

def parse_year_table(year, label):
    rows = year.parent.select('table.contenttable tr')
    row_values = []
    for row in rows:
        row_values.append([x.text.strip() for x in row.find_all('td')])

    table_labels = row_values[0]
    table_values = row_values[1:]

    exp_labels = [
        'Station',
        'Jan',
        'Feb',
        'Mär',
        'Apr',
        'Mai',
        'Jun',
        'Jul',
        'Aug',
        'Sep',
        'Okt',
        'Nov',
        'Dez',
        'Total',
    ]
    for i, exp_label in enumerate(exp_labels):
        assert table_labels[i] == exp_label, f"Labels do not match {table_labels[i]} != {exp_label}"

   
    values = []
    for table_value in table_values:
        station_values = {
            'jahr': label,
            'station': table_value[0],
            'monat': dict(zip(range(1,13), table_value[1:12])),
            'aktualisierungsdatum': datetime.now().isoformat(timespec='seconds')
        }
        values.append(station_values)

    return values


def insert_or_update(values, conn):
    for month, value in values['monat'].items():
        try:
            print(f"Try to insert value: {values['jahr']}, {values['station']}: {values['monat']}")
            c = conn.cursor()
            c.execute(
                '''
                INSERT INTO data (
                    jahr,
                    monat,
                    station,
                    sonnenschein_h,
                    aktualisierungsdatum
                )
                VALUES
                (?,?,?,?,?)
                ''',
                [
                    values['jahr'],
                    month,
                    values['station'],     
                    value,
                    values['aktualisierungsdatum'],
                ]
            )
        except sqlite3.IntegrityError:
            try:
                print("Already there, updating instead")
                c.execute(
                    '''
                    UPDATE data SET sonnenschein_h = ?, aktualisierungsdatum = ? WHERE jahr = ? AND monat = ? AND station = ?
                    ''',
                    [
                        value,
                        values['aktualisierungsdatum'],
                        values['jahr'],
                        month,   
                        values['station'],
                    ]
                )
            except sqlite3.Error as e:
                print("Error: an error occured in sqlite3: ", e.args[0], file=sys.stderr)
                conn.rollback()
                raise
        finally:
            conn.commit()



try:
    DATABASE_NAME = os.path.join(__location__, 'data.sqlite')
    conn = sqlite3.connect(DATABASE_NAME)


    # HEV
    start_url = 'https://www.hev-schweiz.ch/vermieten/nebenkostenabrechnungen/sonnenscheindauer/'

    # check values of current page
    page = requests.get(start_url)
    soup = BeautifulSoup(page.content, 'html.parser')

    # check all years
    years = soup.select('div.accordion_box div.csc-header')

    for year in years:
        title = year.find('h2')
        if not title:
            continue
        year_text = title.text.strip().replace('Sonnenscheindauer ', '')
        values = parse_year_table(year, year_text)
        for value in values:
            insert_or_update(value, conn)


    conn.commit()
except Exception as e:
    print("Error: %s" % e)
    print(traceback.format_exc())
    raise
finally:
    conn.close()
