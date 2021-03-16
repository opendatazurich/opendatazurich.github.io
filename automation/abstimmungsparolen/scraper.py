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


def find_parent(elem, tag_name):
    for parent in elem.parents:
            headers = parent.find(tag_name)
            if not headers:
                continue
            return headers
    return None


def find_vote_text(elem, tag_name, ignore):
    if not re.search(ignore, elem.text):
        return elem
    
    results = elem.find_all_previous(tag_name)
    for res in results:
        if not re.search(ignore, res.text):
            return res


def insert_or_update(parole, conn):
    try:
        print(f"Try to insert vote parole: {parole['vote_title']}, {parole['party']}: {parole['parole']}")
        c = conn.cursor()
        c.execute(
            '''
            INSERT INTO data (
                datum,
                titel,
                abstimmungstext,
                partei,
                parole
            )
            VALUES
            (?,?,?,?,?)
            ''',
            [
                parole['vote_date'],
                parole['vote_title'],
                parole['vote_text'],     
                parole['party'],
                parole['parole'],
            ]
        )
    except sqlite3.IntegrityError:
        try:
            print("Already there, updating instead")
            print(parole)
            c.execute(
                '''
                UPDATE data SET parole = ? WHERE datum = ? AND titel = ? AND partei = ?
                ''',
                [
                    parole['parole'],
                    parole['vote_date'],
                    parole['vote_title'],   
                    parole['party'],
                ]
            )
        except sqlite3.Error as e:
            print("Error: an error occured in sqlite3: ", e.args[0], file=sys.stderr)
            conn.rollback()
            raise
    finally:
        conn.commit()


def parse_vote_date(str):
    try:
        vote_datetime = dateparser.parse(
            str,
            languages=['de']
        )
        vote_date = vote_datetime.date().isoformat()
        print("Vote date: %s" % vote_date)
    except (AttributeError, ValueError):
        print("Couldn't parse date: %s" % str)
        vote_date = str
    return vote_date


def parse_parole_page(content):
    soup = BeautifulSoup(content, 'html.parser')

    lead = soup.select_one('p.lead')
    vote_text = re.search(r'(Vorlage \w+:)?(.*)', lead.text.strip())[2].strip()

    table = soup.find('table')
    paroles = []
    for row in table.find_all('tr'):
        party = row.find('th')
        parole = row.find('td')
        
        if party and parole:
            party_text = party.text.strip()
            parole_text = parole.text.strip()
            if party_text.lower() == 'glp':
                party_text = party_text.lower()
            
            print(f"{party_text}: {parole_text}")
            
            parole = {
                'vote_text': vote_text,
                'party': party_text,
                'parole': parole_text,
            }
            paroles.append(parole)
    return paroles


def parse_vote_page(vote_url, conn):
        vote_page = requests.get(vote_url)
        soup = BeautifulSoup(vote_page.content, 'html.parser')
        city_vote = soup.find_all(string=re.compile(r'Gemeindeabstimmung|kommunal'))
        if not city_vote:
            print("No communal vote")
            return

        header_text = soup.select_one('h1.page_title').text.strip()
        vote_date_str = re.search(r'([^\:]+):?.*', header_text)[1]
        if not vote_date_str:
            print("Could not parse vote date")
            return
        vote_date = parse_vote_date(vote_date_str)

        votes = soup.select('li.var_active li.var_has_subitems')
        for vote in votes:
            single_url = urljoin(vote_url, vote.find('a')['data-multilevelnav-id'])
            vote_title = re.search(r'(Vorlage \w+:)?(.*)', vote.text.strip())[2].strip()
            single_vote_page = requests.get(single_url)
            soup = BeautifulSoup(single_vote_page.content, 'html.parser')

            voting_parole_link = soup.find("a", string=re.compile(".*(p|P)arole.*"))
            if not voting_parole_link:
                print("No voting parole link found")
                return
            parole_url = urljoin(vote_url, voting_parole_link['href'])
            parole_page = requests.get(parole_url)
            
            paroles = parse_parole_page(parole_page.content)
            for parole in paroles:
                parole['vote_title'] = vote_title
                parole['vote_date'] = vote_date
                insert_or_update(parole, conn)


try:
    DATABASE_NAME = os.path.join(__location__, 'data.sqlite')
    conn = sqlite3.connect(DATABASE_NAME)


    # city of zurich - start url
    start_url = 'https://www.stadt-zuerich.ch/portal/de/index/politik_u_recht/abstimmungen_u_wahlen.html'

    # check paroles of current votes
    page = requests.get(start_url)
    soup = BeautifulSoup(page.content, 'html.parser')
    box = soup.find(string=re.compile(r'.*Vorlage.*'))

    vote_href = box.find_parent('a')['href']
    vote_url = urljoin(start_url, vote_href)
    parse_vote_page(vote_url, conn)

    # parse page from vote archive
    #url = 'https://www.stadt-zuerich.ch/portal/de/index/politik_u_recht/abstimmungen_u_wahlen/archiv_abstimmungen/vergangene_termine/201129.html'
    #parse_vote_page(url, conn)

    conn.commit()
except Exception as e:
    print("Error: %s" % e)
    print(traceback.format_exc())
    raise
finally:
    conn.close()
