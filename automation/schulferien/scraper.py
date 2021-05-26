#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urljoin
import sys
import os
import traceback
import download as dl


__location__ = os.path.realpath(
    os.path.join(
        os.getcwd(),
        os.path.dirname(__file__)
    )
)


def get_ics_download_url(url):
    content = dl.download_content(url)
    soup = BeautifulSoup(content, 'html.parser')
    download = soup.find('a', title=re.compile(r".*Import.*"))
    if not download:
        return None
    download_url = urljoin(url, download['href'])
    return download_url


try:
    # city of zurich - start url
    start_url = 'https://www.stadt-zuerich.ch/ssd/de/index/volksschule/schulferien.html'

    # page for each year
    content = dl.download_content(start_url)
    soup = BeautifulSoup(content, 'html.parser')
    nav = soup.find('li', {'class': 'var_wrapping_node var_active'})
    pages = nav.find_all('a', string=re.compile(r'^\d{4}/\d{2}$'))

    for page in pages:
        year_href = page.get('href')
        year_url = urljoin(start_url, year_href)
        download_url = get_ics_download_url(year_url)
        filename = os.path.basename(download_url)
        file_path = os.path.join(__location__, filename)
        dl.download_file(download_url, file_path)
        print(f"Download URL: {download_url}")

except Exception as e:
    print("Error: %s" % e)
    print(traceback.format_exc())
    raise
