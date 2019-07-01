# -*- coding: utf-8 -*-

import requests
from pprint import pprint
import pandas as pd


SSL_VERIFY = True
# evtl. SSL_VERIFY auf False setzen wenn die Verbindung zu https://www.zuerich.com nicht klappt (z.B. wegen Proxy)
# Um die SSL Verifikation auszustellen, bitte die nächste Zeile einkommentieren ("#" entfernen)
SSL_VERIFY = False
if not SSL_VERIFY:
    import urllib3
    urllib3.disable_warnings()
    
    
def generate_csv_download(endpoint, name):
    print(f'Get data from {endpoint}')
    headers = {'Accept': 'application/json'}
    r = requests.get(endpoint, headers=headers, verify=SSL_VERIFY)
    data = r.json()
    df = pd.DataFrame(data)
    df.to_csv(f'data_{name}.csv', index=False)
    print(f'Saved CSV to data_{name}.csv')
    print('')


generate_csv_download('https://www.zuerich.com/en/data/gastronomy', 'gastro')
generate_csv_download('https://zuerich.com/en/data/attractions', 'attractions')
generate_csv_download('https://www.zuerich.com/de/data/place/shopping', 'shopping')
generate_csv_download('https://www.zuerich.com/de/data/accommodation', 'accommodation')
generate_csv_download('https://www.zuerich.com/de/data/place/culture/museums', 'museums')
generate_csv_download('https://www.zuerich.com/de/data/place/culture', 'culture')
generate_csv_download('https://www.zuerich.com/de/data/place/sport', 'sport')
generate_csv_download('https://www.zuerich.com/de/data/place/wellness', 'wellness')
generate_csv_download('https://www.zuerich.com/de/data/gastronomy/nightlife/clubs+%7C%7C+discos', 'clubs')
generate_csv_download('https://www.zuerich.com/de/data/gastronomy/nightlife/bars+%7C%7C+lounges', 'bars')