#!/usr/bin/env python
# coding: utf-8

# ## Datenabfrage von REST API von ASE Daten Hardbrücke

# #### Einstellungen

# In[1]:


import requests
import pandas as pd
import numpy as np
import json
import re
from datetime import date, datetime, timedelta
import os

######################################################################
# USER INPUTS
######################################################################
start_date = 20240101                 # ENTER THE START DATE in YYYYMMDD FORMAT
end_date = 20240505                  # ENTER THE END DATE in YYYYMMDD FORMAT
granularity = "FiveMinutes"           # change granularity if needed (e.g. "Hour")
required_location_names = ["TVH Ost", "TVH West"] # Ost und West separat

# Alternativ dynamische Start- und Enddaten
# today = datetime.today()
# start_date = today - timedelta(days=14)
# start_date = start_date.strftime("%Y%m%d")
# end_date = today - timedelta(days=1)
# end_date = end_date.strftime("%Y%m%d")
######################################################################
# USER INPUTS
######################################################################
url = "https://zuerich.pas.ch/v2/api/Auth/login"
url2 = "https://zuerich.pas.ch/v2" # EDIT THIS TO PUT THE BASE URL

payload = {
    'username': os.getenv('VBZ_SSZ_USER_N'),         # ENTER THE USERNAME
    'password': os.getenv('VBZ_SSZ_PASSWORD_N'),           # ENTER THE PASSWORD
}

bearer = requests.request("POST", url, json=payload)
token = bearer.json()['accessToken']
headers = {"Authorization": "Bearer "+token}
#print(headers)

count = pd.DataFrame( columns = ['DateId', 'Granularity', 'LocationName', 'TimeId', 'InCount', 'OutCount'])
locations = pd.DataFrame( columns = ['Id', 'LocalName', 'Code', 'CodeAlt', 'GlobalName', 'PathId', 'GeoCoordinateId', 'Type'])

for location_name in required_location_names:

    final_df = pd.DataFrame( columns = ['DateId', 'Granularity', 'LocationId', 'TimeId', 'InCount', 'OutCount'])
    # Fetch the locationid for the required location
    response = requests.get(url2 + "/api/location?$filter=LocalName eq '" + location_name + "'", headers=headers)
    location_json = response.json()['value']

    # Fetch the count for the required location. This will return us count data of all the sublocations, if the selected location is not a leaf node.
    count_url = url2 + "/api/count(" + location_json[0]['Id'] + ")" + "?$filter=DateId ge " + str(start_date) + " and DateId lt " + str(end_date) + " and Granularity eq '" + granularity + "'"
    count_json = {'@odata.nextLink': count_url}

    while '@odata.nextLink' in count_json:
        # print('url: ' + count_json['@odata.nextLink'])
        count_url = count_json['@odata.nextLink']
        response = requests.get(count_url, headers=headers)

        count_json = response.json()
        values = count_json['value']

        df = pd.DataFrame.from_dict(values, orient='columns')
        final_df = pd.concat([final_df, df], ignore_index=True)
    count = pd.concat([count, final_df], ignore_index=True)
    locations = pd.concat([locations, pd.DataFrame.from_dict(location_json, orient='columns')], ignore_index=True)
    locations["IsIncludedForParent"]=locations["IsIncludedForParent"].astype(bool) # Explicitly cast to bool dtype to avoid the warning about future version

df_count = pd.DataFrame.from_dict(count)
df_count.head(5)

df_count.to_csv("vbz_frequenzen_2024_raw.csv")
