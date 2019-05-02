# -*- coding: utf-8 -*-

import requests
from pprint import pprint
import os

# check HTTP_PROXY env-variable
print(os.environ)

proxies = {
  "http": "xxx",
  "https": "xxx",
}

# get all API parameters
headers = {'Accept': 'application/json'}
#r = requests.get('http://www.gemeinderat-zuerich.ch/api/Mitglieder/parameter', headers=headers)
r = requests.get('http://www.gemeinderat-zuerich.ch/api/Mitglieder/parameter', headers=headers, proxies=proxies)



pprint(r.content)
params = r.json()

# get the parteiId of the party "FDP"
parties = params['Parteien']
pprint(parties)
parteiId = [elem for elem in parties.items() if elem['Name'] == 'FDP'][0]['Id']

pprint(parteiId)