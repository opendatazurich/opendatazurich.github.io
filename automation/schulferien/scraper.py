#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import requests
from bs4 import BeautifulSoup
import sqlite3
import re
from urllib.parse import urljoin
import sys
import os
import traceback
import download as dl
import parse_ics


__location__ = os.path.realpath(
    os.path.join(
        os.getcwd(),
        os.path.dirname(__file__)
    )
)


def get_ics_download_url(url):
    content = dl.download_content(url)
    soup = BeautifulSoup(content, 'html.parser')
    #titles have different input over the years
    download = soup.find('a', title=re.compile(r".*Import|Termin.*"))
    if not download:
        return None
    download_url = urljoin(url, download['href'])
    return download_url

def insert_or_update(events, conn):
    try:
        for event in events:
            try:
                print(f"Try to insert holiday: {event['summary']}: {event['start_date']} - {event['end_date']}")
                c = conn.cursor()
                c.execute(
                    '''
                    INSERT INTO data (
                        start_date,
                        end_date,
                        summary,
                        created_date
                    )
                    VALUES
                    (?,?,?,?)
                    ''',
                    [
                        event['start_date'],
                        event['end_date'],
                        event['summary'],
                        event['created_date'],
                    ]
                )
            except sqlite3.IntegrityError:
                print("Already there, skipping entry")
                continue
            except sqlite3.Error as e:
                print("Error: an error occured in sqlite3: ", e.args[0], file=sys.stderr)
                conn.rollback()
                raise
    finally:
        conn.commit()


try:
    DATABASE_NAME = os.path.join(__location__, 'data.sqlite')
    conn = sqlite3.connect(DATABASE_NAME)

    # city of zurich - start url
    start_url = 'https://www.stadt-zuerich.ch/de/bildung/volksschule/schulferien.html'

    # page for each year
    content = dl.download_content(start_url)
    soup = BeautifulSoup(content, 'html.parser')
    # Finde alle <stzh-datalist-item> Tags mit einem href-Attribut
    ics_links = soup.find_all('stzh-datalist-item', href=True)
    # Extrahiere das href-Attribut (URL) jedes Links
    pages = [link['href'] for link in ics_links if link['href'].endswith('.ics')]

    for page in pages:
        year_href = page
        download_url = urljoin(start_url, year_href)
        filename = os.path.basename(download_url)
        file_path = os.path.join(__location__, filename)
        dl.download_file(download_url, file_path)
        print(f"Download URL: {download_url}")
        events = parse_ics.parse_file(file_path)
        insert_or_update(events, conn)

    conn.commit()
except Exception as e:
    print("Error: %s" % e)
    print(traceback.format_exc())
    raise
finally:
    conn.close()
