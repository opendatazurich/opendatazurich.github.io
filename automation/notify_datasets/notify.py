# -*- coding: utf-8 -*-
import os
import sys
import datetime
import traceback
import pytz
import math
import requests
import pandas as pd
from ckanapi import RemoteCKAN, NotFound
import teams_webhook
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())


MSTEAMS_WEBHOOK = os.getenv('MSTEAMS_WEBHOOK')


def convert_to_localtime(str):
    zurich_tz = pytz.timezone('Europe/Zurich')
    dateobj =  datetime.datetime.strptime(str, '%Y-%m-%d %H:%M:%S.%f')
    local_date = pytz.utc.localize(dateobj).astimezone(zurich_tz)
    local_datetime = local_date.strftime('%d.%m.%Y %H:%M')
    return (dateobj, local_date, local_datetime)


def send_telegram_message(token, chat_id, message):
    params = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": 'HTML',
    }
    headers = {'Content-Type': 'application/json'}
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    r = requests.post(url, json=params, headers=headers)
    print(f"Telegram response: {r.content}", file=sys.stderr)
    r.raise_for_status()

def send_teams_message(webhook, message, title=None):
    myTeamsMessage = teams_webhook.ConnectorCard(webhook)
    if title:
        myTeamsMessage.title(title)
    myTeamsMessage.text(message)
    myTeamsMessage.send()

def to_markdown(df):
    """
    Format pandas df as markdown
    """
    # Create a new DataFrame with just the markdown title strings
    df2 = pd.DataFrame([['---',]*len(df.columns)], columns=df.columns)

    #Create a new concatenated DataFrame
    df3 = pd.concat([df2, df])
    # return | separatet csv aka markdown
    return df3.to_csv(sep='|', index=False)


try:
    BASE_URL = os.getenv('CKAN_BASE_URL')
    API_KEY = os.getenv('CKAN_API_KEY')
    ckan = RemoteCKAN(BASE_URL, apikey=API_KEY)

    # get list + status of all harvesters
    harvesters = ckan.call_action('harvest_source_list')

    data_dict = {} # empty dict to gather info from distinct harvester runs
    for harvester in harvesters:        
        try:
            if not harvester['active']:
                continue
            try:
                source_info = ckan.call_action('harvest_source_show', {'id': harvester['id']})

                last_job_stats = source_info['status']['last_job']['stats']
                print("name:",source_info['name'])
                print("last_job_stats",last_job_stats)
                print(f"https://ckan-prod.zurich.datopian.com/harvest/{source_info['name']}/job/{source_info['status']['last_job']['id']}")
            except (NotFound, TypeError):
                print("there is no last_job or harvester NotFound")
                continue # there is no "last_job" or harvester NotFound
            
            # gather info for last run and format dates
            name = source_info['name']
            job_id = source_info['status']['last_job']['id']

            start_str = source_info['status']['last_job']['gather_started']
            if start_str:
                start, start_local, start_datetime = convert_to_localtime(start_str)
            else:
                start = None
                start_local = None
                start_datetime = ''

            end_str = source_info['status']['last_job']['finished']
            if end_str:
                end, end_local, end_datetime =  convert_to_localtime(end_str)
            else:
                end = None
                end_local = None
                end_datetime = ''

            if end and start:
                elapsed_time = end - start
                minutes, seconds = divmod(elapsed_time.total_seconds(), 60)
                duration = f'{int(minutes):02}:{math.floor(seconds):02} min'

                created_start = start.strftime('%Y-%m-%dT%H:%M:%SZ')
                created_end = end.strftime('%Y-%m-%dT23:59:59Z') # always use end of day as end
            else:
                duration = 'unbekannt'
                # dummy text for url if time not available
                created_start = "XXX"
                created_end = "XXX"
            
            # skip if last harvest job is older than 24h
            # but raise as error if there is no end time
            # as this could indicate, that the harvest job got stuck
            runs_too_long = False
            created, created_local, _ = convert_to_localtime(source_info['status']['last_job']['created'])
            if created:
                since_last_run = (datetime.datetime.now() - created).total_seconds()
                if since_last_run > (24*60*60) and not end:
                    runs_too_long = True
                    duration = ">=24h!"
                elif since_last_run > (24*60*60) and end:
                    print("skip because too old")
                    continue

            # set status
            if last_job_stats['deleted'] > 0 or last_job_stats['errored'] > 0:
                status = '🔴'
            elif last_job_stats['added'] > 0 or runs_too_long:
                status = '🟡'
            else:
                status = '🟢'

            # add harvester run info to dict
            data_dict[name] = {
                'harvester titel': f'[{source_info["title"]}](https://ckan-prod.zurich.datopian.com/harvest/{name}/job/{job_id})',
                'status': status,
                'start': start_datetime,
                'ende': end_datetime,
                'dauer': duration,
                # 'harvester_url': f'https://ckan-prod.zurich.datopian.com/harvest/{name}/job/{job_id}',
                'anzahl neu': last_job_stats['added'],
                'url neue': f"[zeige neue](https://data.stadt-zuerich.ch/dataset?q=harvest_source_id%3A{harvester['id']}+AND+metadata_created%3A%5B{created_start}+TO+{created_end}%5D)",
                'anzahl aktualisiert': last_job_stats['updated'],
                'url aktualisierte': f"[zeige aktual.](https://data.stadt-zuerich.ch/dataset?q=harvest_source_id%3A{harvester['id']}+AND+metadata_modified%3A%5B{created_start}+TO+{created_end}%5D)",
                'anzahl gelöscht': last_job_stats['deleted'],
                'anzahl fehler': last_job_stats['errored'],
            }
        except Exception as e:
            print(f"Failed for harvester {harvester} with error: {e}", file=sys.stderr)
            raise

    # make df from dict and send to teams
    df = pd.DataFrame(data_dict).T
    print(df)
    send_teams_message(MSTEAMS_WEBHOOK, to_markdown(df), title="Harvester Info letzter run")

except Exception as e:
    print(f"Error: {e}", file=sys.stderr)
    print(traceback.format_exc(), file=sys.stderr)
    sys.exit(1)
