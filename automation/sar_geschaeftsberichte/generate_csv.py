import sruthi
import csv
import sys
import traceback
from bs4 import BeautifulSoup
import requests
from random import randint
from time import sleep

records = sruthi.searchretrieve(
    'https://amsquery.stadt-zuerich.ch/SRU/',
    query="isad.reference = V.B.b.43.:1 AND isad.descriptionlevel = Dossier"
)

try:
    header = ['signatur', 'titel', 'jahr', 'link_query', 'dateiname', 'download_url']
    writer = csv.DictWriter(
        sys.stdout,
        header,
        delimiter=',',
        quotechar='"',
        lineterminator='\n',
        quoting=csv.QUOTE_MINIMAL
    )
    writer.writeheader()

    for record in records:
        sleep(randint(1,5))

        # get additional info from link
        r = requests.get(record['extra']['link'])
        soup = BeautifulSoup(r.text, 'html.parser')
        pdf_link = soup.find('td', {'class': 'veXDetailAttributLabel'}, string="Dateien:") \
                    .next_sibling \
                    .find('a')
        pdf_path = pdf_link['href'].replace("JavaScript:openDoc('", '').replace("');", "")

        row = {
           'signatur': record['reference'],
           'titel': record['title'],
           'jahr': record['date'],
           'link_query': record['extra']['link'],
           'dateiname': pdf_link.string, 
           'download_url': f"https://amsquery.stadt-zuerich.ch/{pdf_path}"
        }
        writer.writerow(row)
except Exception as e:
    print("Error: %s" % e, file=sys.stderr)
    print(traceback.format_exc(), file=sys.stderr)
    sys.exit(1)
finally:
    sys.stdout.flush()
