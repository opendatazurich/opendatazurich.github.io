# -*- coding: utf-8 -*-
import os
import sys
import re
import datetime
import traceback
import pytz
import math
import requests
from ckanapi import RemoteCKAN, NotFound
import teams_webhook
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

# TELEGRAM_TOKEN bekommt man beim erstellen eines neuen Bots
# Neuer Bot => Chatten mit BotFather auf Telegram
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_TO')
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


try:
    BASE_URL = os.getenv('CKAN_BASE_URL')
    API_KEY = os.getenv('CKAN_API_KEY')
    ckan = RemoteCKAN(BASE_URL, apikey=API_KEY)

    # get list + status of all harvesters
    harvesters = ckan.call_action('harvest_source_list')
    for harvester in harvesters:
        try:
            if not harvester['active']:
                continue
            try:
                source_info = ckan.call_action('harvest_source_show', {'id': harvester['id']})
                last_job_stats = source_info['status']['last_job']['stats']
            except (NotFound, TypeError):
                continue # there is no "last_job" or harvester NotFound
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
                status = '🔴'
            elif last_job_stats['added'] > 0 or runs_too_long:
                status = '🟡'
            else:
                status = '🟢'
                
            
            # generate links for new/updated datasets
            text = f"<b><a href='https://ckan-ogdzh.clients.liip.ch/harvest/{name}/job/{job_id}'>{source_info['title']}</a></b>"
            text += f'\n{status} {start_datetime}'
            text += f'\n🏁 {end_datetime}'
            text += f'\n⏱ {duration}'
            if start and end:
                created_start = start.strftime('%Y-%m-%dT%H:%M:%SZ')
                created_end = end.strftime('%Y-%m-%dT23:59:59Z') # always use end of day as end
                new_url = f"https://data.stadt-zuerich.ch/dataset?q=harvest_source_id%3A{harvester['id']}+AND+metadata_created%3A%5B{created_start}+TO+{created_end}%5D"
                new_link = f"<b><a href='{new_url}'>Neue Datensätze</a></b>"
                update_url = f"https://data.stadt-zuerich.ch/dataset?q=harvest_source_id%3A{harvester['id']}+AND+metadata_modified%3A%5B{created_start}+TO+{created_end}%5D"
                update_link = f"<b><a href='{update_url}'>Aktualisierte Datensätze</a></b>"
                text += f"\n\n🔍 {new_link}\n🔍 {update_link}"

            text += f"\n\n<b>Neu</b>: {last_job_stats['added']}"
            text += f"\n<b>Aktualisiert</b>: {last_job_stats['updated']}"
            text += f"\n<b>Gelöscht</b>: {last_job_stats['deleted']}"
            text += f"\n<b>Fehler</b>: {last_job_stats['errored']}"

            try:
                # send_telegram_message(TELEGRAM_TOKEN, TELEGRAM_CHAT_ID, text)
                send_teams_message(MSTEAMS_WEBHOOK, text, title=None)
            except requests.HTTPError as e:
                print(f"Error when sending message to telegram/teams for harvester {harvester}: {e}", file=sys.stderr)
                raise
        except Exception as e:
            print(f"Failed for harvester {harvester} with error: {e}", file=sys.stderr)
            raise
except Exception as e:
    print(f"Error: {e}", file=sys.stderr)
    print(traceback.format_exc(), file=sys.stderr)
    sys.exit(1)
