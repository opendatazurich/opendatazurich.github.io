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

try:
    BASE_URL = os.getenv('CKAN_BASE_URL')
    API_KEY = os.getenv('CKAN_API_KEY')
    SLACK_CHANNEL_ID = os.getenv('SLACK_CHANNEL_ID')
    ckan = RemoteCKAN(BASE_URL, apikey=API_KEY)

    # get list + status of all harvesters
    harvesters = ckan.call_action('harvest_source_list')

    zurich_tz = pytz.timezone('Europe/Zurich')

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
                start =  datetime.datetime.strptime(start_str, '%Y-%m-%d %H:%M:%S.%f')
                local_start = pytz.utc.localize(start).astimezone(zurich_tz)
                start_datetime = local_start.strftime('%d.%m.%Y %H:%M')
                # skip if last harvest job is older than 24h
                since_last_run = (datetime.datetime.now() - start).total_seconds()
                if since_last_run > (24*60*60):
                    continue
            else:
                start_datetime = ''

            end_str = source_info['status']['last_job']['finished']
            if end_str:
                end =  datetime.datetime.strptime(end_str, '%Y-%m-%d %H:%M:%S.%f')
                local_end = pytz.utc.localize(end).astimezone(zurich_tz)
                end_datetime = local_end.strftime('%d.%m.%Y %H:%M')
            else:
                end_datetime = ''

            if end and start:
                elapsed_time = end - start
                minutes, seconds = divmod(elapsed_time.total_seconds(), 60)
                duration = f'{minutes}min {math.floor(seconds)}s'
            else:
                duration = 'unbekannt'

            if last_job_stats['deleted'] > 0:
                color = 'danger'
            elif last_job_stats['added'] > 0:
                color = 'warning'
            else:
                color = 'good'

                
            attachment = {
                'fallback': source_info['title'],
                'color': color,
                'title': source_info['title'],
                'title_link': f"https://data.stadt-zuerich.ch/harvest/{name}/job/{job_id}",
                'text': f':runner: {start_datetime} :checkered_flag: {end_datetime} ({duration})',
                'fields': [
                    {
                        "title": "Neu",
                        "value": last_job_stats['added'],
                        "short": True,
                    },
                    {
                        "title": "Akutalisiert",
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
