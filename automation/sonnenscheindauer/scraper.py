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


__location__ = os.path.realpath(
    os.path.join(
        os.getcwd(),
        os.path.dirname(__file__)
    )
)


def insert_or_update(values, conn):
    try:
        print(f"Try to insert value: {values['jahr']}/{values['monat']}, {values['ort']}: {values['sonnenscheindauer_stunden']}")
        c = conn.cursor()
        c.execute(
            '''
            INSERT INTO data (
                jahr,
                monat,
                ort,
                sonnenscheindauer_stunden,
                aktualisierungsdatum
            )
            VALUES
            (?,?,?,?,?)
            ''',
            [
                parole['jahr'],
                parole['monat'],
                parole['ort'],     
                parole['sonnenscheindauer_stunden'],
                parole['aktualisierungsdatum'],
            ]
        )
    except sqlite3.IntegrityError:
        try:
            print("Already there, updating instead")
            print(parole)
            c.execute(
                '''
                UPDATE data SET sonnenscheindauer_stunden = ? WHERE jahr = ? AND monat = ? AND ort = ?
                ''',
                [
                    parole['sonnenscheindauer_stunden'],
                    parole['jahr'],
                    parole['monat'],   
                    parole['ort'],
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

    # parse single year table


    conn.commit()
except Exception as e:
    print("Error: %s" % e)
    print(traceback.format_exc())
    raise
finally:
    conn.close()
