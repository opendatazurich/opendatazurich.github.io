# -*- coding: utf-8 -*-

import requests
from bs4 import BeautifulSoup
import sqlite3
import re
from urllib.parse import urljoin
import dateparser
import sys
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


def parse_parole_page(content):
    soup = BeautifulSoup(content, 'html.parser')
    
    tables = soup.find_all('table')
    ignore = re.compile("(.*Parteiparolen.*)|(.*Ergänzende Informationen.*)")
    vote_nr = re.compile('(Vorlage \w+:)|(\w+\.)')
    
    votes = []
    for t in tables:
        # find parent header
        header = find_vote_text(find_parent(t, 'h2'), 'h2', ignore)
        vote_title = header.text.strip()
        
        header_div = header.parent.parent
        vote_text = ''
        if header_div:
            vote_text = header_div.find('p')
            if vote_text:
                vote_text = vote_text.text.strip()
            else:
                vote_text = vote_nr.sub('', vote_title).strip()
        
        print("")
        print(vote_title)
        print(vote_text)
        
        paroles = []
        for row in t.find_all('tr'):
            party = row.find('th')
            parole = row.find('td')
            
            if party and parole:
                party_text = party.text.strip()
                parole_text = parole.text.strip()
                if party_text.lower() == 'glp':
                    party_text = party_text.lower()
                
                print("%s: %s" % (party_text, parole_text))
                
                parole = {
                    'party': party_text,
                    'parole': parole_text
                }
                paroles.append(parole)
        
        vote = {
            'vote_text': vote_text,
            'vote_title': vote_title,
            'paroles': paroles,
        }
        votes.append(vote)
        
    return votes

def parse_dates_page(date_page_url, conn):
    date_page = requests.get(date_page_url)
    soup = BeautifulSoup(date_page.content, 'html.parser')
    vote_links = soup.select('.mainparsys ul.linklist a.var_icon_arrow_right')
    
    c = conn.cursor()
    for vote_link in vote_links:
        vote_date_str = vote_link.text.strip()
        print("")
        print("")
        print(vote_date_str)
        
        try:
            vote_datetime = dateparser.parse(
                vote_date_str,
                languages=['de']
            )
            vote_date = vote_datetime.date().isoformat()
            print("Vote date: %s" % vote_date)
        except (AttributeError, ValueError):
            print("Couldn't parse date: %s" % vote_date_str)
            vote_date = vote_date_str
        
        vote_url = urljoin(date_page_url, vote_link['href'])
        vote_page = requests.get(vote_url)
        soup = BeautifulSoup(vote_page.content, 'html.parser')
        city_vote = soup.find_all(string="Gemeindeabstimmung")
        if not city_vote:
            continue
        voting_parole_link = soup.find("a", string=re.compile(".*(p|P)arole.*"))
        if not voting_parole_link:
            print("No voting parole link found")
            continue
        parole_url = urljoin(vote_url, voting_parole_link['href'])
        parole_page = requests.get(parole_url)
        
        votes = parse_parole_page(parole_page.content)
        for vote in votes:
            for parole in vote['paroles']:
                try:
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
                            vote_date,
                            vote['vote_title'],
                            vote['vote_text'],     
                            parole['party'],
                            parole['parole'],
                        ]
                    )
                except sqlite3.IntegrityError:
                    try:
                        c.execute(
                            '''
                            UPDATE data SET parole = ? WHERE datum = ? AND titel = ? AND partei = ?;'
                            ''',
                            [
                                parole['parole'],
                                vote_date,
                                vote['vote_title'],   
                                parole['party'],
                                ,
                            ]
                        )
                    except sqlite3.Error as e:
                        print("Error: an error occured in sqlite3: ", e.args[0], file=sys.stderr)
                        conn.rollback()


try:
    DATABASE_NAME = os.path.join(__location__, 'data.sqlite')
    conn = sqlite3.connect(DATABASE_NAME)


    # city of zurich - start url
    start_url = 'https://www.stadt-zuerich.ch/portal/de/index/politik_u_recht/abstimmungen_u_wahlen.html'

    # check paroles of previous and next dates
    page = requests.get(start_url)
    soup = BeautifulSoup(page.content, 'html.parser')

    # Update July 2019: there is no longer a page for the next votes
    # next_dates_link = soup.find_all("a", href=re.compile("[^#]+.*"), string=re.compile(".*Nächste Termine.*"))
    # next_url = urljoin(start_url, next_dates_link[0]['href'])

    prev_dates_link = soup.find_all("a", href=re.compile("[^#]+.*"), string=re.compile(".*Vergangene Termine.*"))
    prev_url = urljoin(start_url, prev_dates_link[0]['href'])


    # parse_dates_page(next_url, conn)
    parse_dates_page(prev_url, conn)
    conn.commit()
except Exception as e:
    print("Error: %s" % e)
    print(traceback.format_exc())
    raise
finally:
    conn.close()