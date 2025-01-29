# -*- coding: utf-8 -*-

import download as dl
import requests
from bs4 import BeautifulSoup
import sqlite3
import re
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


def insert_or_update(data, conn):
    try:
        print(f"Try to insert voter participation: {data['abst_datum']}, {data['akt_datum']}: {data['stimmbeteiligung']}")
        c = conn.cursor()
        c.execute(
            '''
            INSERT INTO data (
                Abstimmungs_Datum,
                Stimmbeteiligung_Prozent,
                Aktualisierungs_Datum
            )
            VALUES
            (?,?,?)
            ''',
            [
                data['abst_datum'],
                data['stimmbeteiligung'],
                data['akt_datum'],
            ]
        )
    except sqlite3.IntegrityError:
        try:
            print("Already there, updating instead")
            print(data)
            c.execute(
                '''
                UPDATE data SET Stimmbeteiligung_Prozent = ? WHERE Abstimmungs_Datum = ? AND Aktualisierungs_Datum = ?
                ''',
                [
                    data['stimmbeteiligung'],
                    data['abst_datum'],
                    data['akt_datum'],
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


    # city of zurich - url of voter participation
    # old website
    #url = 'https://www.stadt-zuerich.ch/portal/de/index/politik_u_recht/abstimmungen_u_wahlen/aktuell/stand-stimmbeteiligung.html'
    current_year = datetime.now().year
    url = f'https://www.stadt-zuerich.ch/de/aktuell/news/{current_year}/stimmbeteiligung.html'

    # parse page
    try:
        content = dl.download_content(url)
    except requests.exceptions.HTTPError as e:
        # swallow bad HTTP status codes
        if e.response.status_code != requests.codes.ok:
            print(f"Error when requesting url {url}: {e.response.status_code}", file=sys.stderr)
            sys.exit(0)
        else:
            raise
   
    soup = BeautifulSoup(content, 'html.parser')
    # get Urnengang info
    description_content = soup.select_one('stzh-text')
    match = re.search(r'Urnengang vom (.+):.*?Stimmbeteiligung.*beträgt.*?(\d+,?\d?)\s*Prozent', description_content.text.strip())
    # get date info
    date_info = soup.select_one('stzh-pagetitle')

    data = {
        'abst_datum': dateparser.parse(match[1], languages=['de']).date().isoformat(),
        'stimmbeteiligung': float(match[2].replace(',', '.')),
        'akt_datum': dateparser.parse(date_info['dateline'], languages=['de']).date().isoformat(),
    }
    insert_or_update(data, conn)

    conn.commit()
except Exception as e:
    print("Error: %s" % e)
    print(traceback.format_exc())
    raise
finally:
    conn.close()
