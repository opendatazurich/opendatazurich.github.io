# -*- coding: utf-8 -*-
import os
import sys
import time
import datetime
import traceback
import pytz
import math
from ckanapi import RemoteCKAN, NotFound
from slack import WebClient
from slack.errors import SlackApiError
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

slack_token = os.environ["SLACK_API_TOKEN"]
client = WebClient(token=slack_token)



def convert_to_localtime(str):
    zurich_tz = pytz.timezone('Europe/Zurich')
    dateobj =  datetime.datetime.strptime(str, '%Y-%m-%d %H:%M:%S.%f')
    local_date = pytz.utc.localize(dateobj).astimezone(zurich_tz)
    local_datetime = local_date.strftime('%d.%m.%Y %H:%M')
    return (dateobj, local_date, local_datetime)

try:
    BASE_URL = os.getenv('CKAN_BASE_URL')
    API_KEY = os.getenv('CKAN_API_KEY')
    SLACK_CHANNEL_ID = os.getenv('SLACK_CHANNEL_ID')
    ckan = RemoteCKAN(BASE_URL, apikey=API_KEY)

    # get list + status of all harvesters
    harvesters = ckan.call_action('harvest_source_list')

    

    for harvester in harvesters:
        try:
            if not harvester['active']:
                continue

            source_info = ckan.call_action('harvest_source_show', {'id': harvester['id']})
            last_job_stats = source_info['status']['last_job']['stats']
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
                duration = f'{minutes}min {math.floor(seconds)}s'
            else:
                duration = 'unbekannt'
            
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
                    continue

            if last_job_stats['deleted'] > 0 or last_job_stats['errored'] > 0:
                color = 'danger'
                status = ':x:'
            elif last_job_stats['added'] > 0 or runs_too_long:
                color = 'warning'
                status = ':warning:'
            else:
                color = 'good'
                status = ':runner:'
                
            
            # generate links for new/updated datasets
            links = ""
            if start and end:
                created_start = start.strftime('%Y-%m-%dT%H:%M:%SZ')
                created_end = end.strftime('%Y-%m-%dT%H:%M:%SZ')
                new_url = f"https://data.stadt-zuerich.ch/dataset?q=harvest_source_id%3A{harvester['id']}+AND+metadata_created%3A%5B{created_start}+TO+{created_end}%5D"
                new_link = f"*<{new_url}|Neue Datensätze anzeigen>*"
                update_url = f"https://data.stadt-zuerich.ch/dataset?q=harvest_source_id%3A{harvester['id']}+AND+metadata_modified%3A%5B{created_start}+TO+{created_end}%5D"
                update_link = f"*<{update_url}|Aktualisierte Datensätze anzeigen>*"
                links = f"\n\n:mag: {new_link}\n:mag: {update_link}"
                
            attachment = {
                'mrkdwn_in': ['text'],
                'fallback': source_info['title'],
                'color': color,
                'title': source_info['title'],
                'title_link': f"https://data.stadt-zuerich.ch/harvest/{name}/job/{job_id}",
                'text': f'{status} {start_datetime} :checkered_flag: {end_datetime} ({duration}){links}',
                'fields': [
                    {
                        "title": "Neu",
                        "value": last_job_stats['added'],
                        "short": True,
                    },
                    {
                        "title": "Aktualisiert",
                        "value": last_job_stats['updated'],
                        "short": True,
                    },
                    {
                        "title": "Gelöscht",
                        "value": last_job_stats['deleted'],
                        "short": True,
                    },
                    {
                        "title": "Fehler",
                        "value": last_job_stats['errored'],
                        "short": True,
                    },
                 ],
                'footer': f'<https://data.stadt-zuerich.ch/harvest/admin/{name}|Harvester Administration>',
                'footer_icon': 'https://data.stadt-zuerich.ch/base/images/ckan.ico',
                'ts': int(time.time()),
            }

            response = client.chat_postMessage(
                channel=SLACK_CHANNEL_ID,
                attachments=[attachment]
            )
        except SlackApiError as e:
            print("SlackApiError: %s" % e.response['error'], file=sys.stderr)
            print(traceback.format_exc(), file=sys.stderr)
            sys.exit(1)
        except Exception as e:
            print(f"Failed for harvester: {harvester} with error: {e}", file=sys.stderr)
            raise
except Exception as e:
    print(f"Error: {e}", file=sys.stderr)
    print(traceback.format_exc(), file=sys.stderr)
    sys.exit(1)
