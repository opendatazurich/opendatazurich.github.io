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
end_date = 20240219                   # ENTER THE END DATE in YYYYMMDD FORMAT
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
    'username': os.getenv('ASE_USER'),         # ENTER THE USERNAME
    'password': os.getenv('ASE_PW'),           # ENTER THE PASSWORD
}


bearer = requests.request("POST", url, json=payload)
token = bearer.json()['accessToken']
headers = {"Authorization": "Bearer "+token}
#print(headers)

count = pd.DataFrame( columns = ['DateId', 'Granularity', 'LocationName', 'TimeId', 'InCount', 'OutCount'])
locations = pd.DataFrame( columns = ['Id', 'LocalName', 'Code', 'CodeAlt', 'GlobalName', 'PathId', 'GeoCoordinateId', 'Type'])

i = 0
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


# In[2]:


#Aufsplitten nach TVH Ost und TVH West für gewünschte locations:

#Filter
tvh_ost = ['vbz_ost_vbz', 'vbz_ost_sued','vbz_ost_nord','vbz_ost_sbb']
tvh_west = ['vbz_west_vbz', 'vbz_west_sued','vbz_west_nord','vbz_west_sbb']

locations = {
    "vbz": "Zugang VBZ", 
    "sued": "Zugang Süd", 
    "nord": "Zugang Nord", 
    "sbb": "Zugang SBB"
  
}

def filter_data(data,zugang_name, location_filter,locationMap):
    #Locations für Zugang filtern
    location_data = df_count[df_count['LocationName'].isin(location_filter)].copy()
    location_data.loc[:, 'Zugang'] = zugang_name

    #Location Name extrahieren und korrekte Bezeichnung setzen
    tmp = location_data['LocationName'].str.split('_', expand=True)
    location_data.loc['LocationName'] = tmp.replace({2: locations})[2]
    
    return location_data

 
df_ost = filter_data(df_count, 'TVH Ost',tvh_ost,locations)
df_west = filter_data(df_count, 'TVH West',tvh_west,locations)

df_ost.head(5)


# ### Daten aufbereiten in Tabelle

# In[3]:


# Keep only certain columns
columns_to_keep = ['DateId', 'Granularity', 'Zugang','LocationName','TimeId', 'InCount', 'OutCount']
df_ost = df_ost[columns_to_keep]
df_west = df_west[columns_to_keep]
df_ost.head(5)


# In[4]:


# Concatenate the two DataFrames
df_count_final = pd.concat([df_ost, df_west], ignore_index=True)
print(df_count_final)


# In[5]:


# Date und Time zusammen nehmen
# zuerst die eine O mit vier 0000 ersetzen, damit Mitternacht auch richtig dargestellt wird
# als String definieren
df_count_final['TimeId'] = df_count_final['TimeId'].astype(str)
# eine Null mit vier Nullen ersetzen (aber nur wenn eine Null, nicht wenn mehr als eine. 0 wird 0000 aber 1000 bleibt 1000)
df_count_final['TimeId'] = df_count_final['TimeId'].apply(lambda x: re.sub(r'\b0\b', '0000', x))
# eine Null hinuzfügen, wenn nur 3 Ziffern (200 wird 0200)
df_count_final['TimeId'] = df_count_final['TimeId'].apply(lambda x: '0' + x if isinstance(x, str) and len(x) == 3 and (pd.isna(x) or pd.notna(x)) else x)
df_count_final['TimeId'] = df_count_final['TimeId'].apply(lambda x: '00' + x if isinstance(x, str) and len(x) == 2 and (pd.isna(x) or pd.notna(x)) else x)
df_count_final['TimeId'] = df_count_final['TimeId'].apply(lambda x: '000' + x if isinstance(x, str) and len(x) == 1 and (pd.isna(x) or pd.notna(x)) else x)
print(df_count_final)


# In[8]:


# unique_values_time = df_count_final['TimeId'].unique()
# print(unique_values_time) # es gibt 24 Stunden plus NA


# In[7]:


rows_with_missing_values = df_count_final[df_count_final.isnull().any(axis=1)]
print(rows_with_missing_values)
# Drop NAs wenn kein Value bei Datum
df_count_final = df_count_final.dropna(subset=['DateId'])


# In[9]:


# Convert date and time columns to datetime objects
df_count_final['DateId'] = pd.to_datetime(df_count_final['DateId'], format='%Y%m%d')
df_count_final['TimeId'] = pd.to_datetime(df_count_final['TimeId'], format='%H%M').dt.time

# Create a new column with the combined datetime (string variable)
df_count_final['Timestamp'] = df_count_final['DateId'].astype(str) + 'T' + df_count_final['TimeId'].astype(str)
# sort the DataFrame
df_count_final= df_count_final.sort_values(by=['LocationName','Timestamp'], ascending=False)
# Display the updated DataFrame
print(df_count_final)


# In[10]:


# Rename columns
df_count_final = df_count_final.rename(columns={'InCount': 'In', 'OutCount': 'Out', 'LocationName': 'Name'})
# Reorder columns and keep only certain columns
columns_to_keep = ['In', 'Out', 'Timestamp', 'Name']  # Define the columns you want to keep and their desired order
df_count_final = df_count_final[columns_to_keep]
df_count_final.head(5)


# In[11]:


unique_values_locations = df_count_final['Name'].unique()
print(unique_values_locations)


# In[12]:


# Define the mapping of old values to new values
value_mapping = {'vbz_ost_nord': 'Ost-Nord total', 'vbz_ost_sbb': 'Ost-SBB total', 'vbz_ost_sued': 'Ost-Sued total', 
                 'vbz_ost_vbz': 'Ost-VBZ Total', 'vbz_west_nord': 'West-Nord total', 'vbz_west_sbb': 'West-SBB total',
                 'vbz_west_sued': 'West-Sued total', 'vbz_west_vbz': 'West-VBZ total'}

# Replace old values with new values in column 'Name'
df_count_final['Name'] = df_count_final['Name'].replace(value_mapping)


# In[13]:


df_count_final.head(10)


# In[22]:


# write df to csv
df_count_final.to_csv("C:/Frequenzen_Hardbruecke_2024.csv", index = False)

