# -*- coding: utf-8 -*-

import pandas as pd
import os
import sys
import csv
import traceback
from datetime import datetime, timedelta
import requests
from dotenv import load_dotenv, find_dotenv
import re
load_dotenv(find_dotenv())

# api access
url = "https://zuerich.pas.ch/v2/api/Auth/login"
url2 = "https://zuerich.pas.ch/v2" # EDIT THIS TO PUT THE BASE URL

# credentials
payload = {
    'username': os.getenv('VBZ_SSZ_USER_N'),         # ENTER THE USERNAME
    'password': os.getenv('VBZ_SSZ_PASSWORD_N'),           # ENTER THE PASSWORD
}

# defining start- end date
today = datetime.today()
start_date = today - timedelta(days=3) # look 3 days back > if error occurs and fixed within 3 days, downtime data will be reincluded
start_date = start_date.strftime("%Y%m%d")
end_date = today + timedelta(days=1) # some date in the future > will include the latest data
end_date = end_date.strftime("%Y%m%d")

# defining granularity of data / select locations
granularity = "FiveMinutes"           # change granularity if needed (e.g. "Hour")
required_location_names = ["TVH Ost", "TVH West"] # Ost und West separat

try:

    ## getting data

    bearer = requests.request("POST", url, json=payload)
    token = bearer.json()['accessToken']
    headers = {"Authorization": "Bearer " + token}

    count = pd.DataFrame(columns=['DateId', 'Granularity', 'LocationName', 'TimeId', 'InCount', 'OutCount'])
    locations = pd.DataFrame(columns=['Id', 'LocalName', 'Code', 'CodeAlt', 'GlobalName', 'PathId', 'GeoCoordinateId', 'Type'])

    for location_name in required_location_names:

        final_df = pd.DataFrame(columns=['DateId', 'Granularity', 'LocationId', 'TimeId', 'InCount', 'OutCount'])
        # Fetch the locationid for the required location
        response = requests.get(url2 + "/api/location?$filter=LocalName eq '" + location_name + "'", headers=headers)
        location_json = response.json()['value']

        # Fetch the count for the required location. This will return us count data of all the sublocations, if the selected location is not a leaf node.
        count_url = url2 + "/api/count(" + location_json[0]['Id'] + ")" + "?$filter=DateId ge " + str(
            start_date) + " and DateId lt " + str(end_date) + " and Granularity eq '" + granularity + "'"
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
        locations["IsIncludedForParent"] = locations["IsIncludedForParent"].astype(bool)  # Explicitly cast to bool dtype to avoid the warning about future version

    df_count = pd.DataFrame.from_dict(count)

    ## data wrangling

    # Filter
    tvh_ost = ['vbz_ost_vbz', 'vbz_ost_sued','vbz_ost_nord','vbz_ost_sbb']
    tvh_west = ['vbz_west_vbz', 'vbz_west_sued','vbz_west_nord','vbz_west_sbb']

    locations = {
        "vbz": "Zugang VBZ",
        "sued": "Zugang Süd",
        "nord": "Zugang Nord",
        "sbb": "Zugang SBB"
    }

    # @LB replace for filter process
    location_data = df_count[df_count['LocationName'].isin(tvh_ost + tvh_west)].copy()
    # location_data.loc[:, 'Zugang'] = zugang_name # alle eintrage in LocationName die vbz_ost_* sin

    location_data['Zugang'] = location_data['LocationName']
    location_data['Zugang'] = location_data['Zugang'].str.replace('vbz_ost.*',r'TVH Ost',regex = True)
    location_data['Zugang'] = location_data['Zugang'].str.replace('vbz_west.*',r'TVH West',regex = True)

    # tmp = location_data['LocationName'].str.split('_', expand=True)
    # location_data['LocationName'] = tmp.replace({2: locations})[2]

    columns_to_keep = ['DateId', 'Granularity', 'Zugang','LocationName','TimeId', 'InCount', 'OutCount']
    location_data = location_data[columns_to_keep]
    df_count_final = location_data.copy()

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
    # print(df_count_final)


    # @LB drop rows with Null values in DateId
    rows_with_missing_values = df_count_final[df_count_final.isnull().any(axis=1)]
    # print(rows_with_missing_values)
    # Drop NAs wenn kein Value bei Datum
    df_count_final = df_count_final.dropna(subset=['DateId'])

    # Convert date and time columns to datetime objects
    df_count_final['DateId'] = pd.to_datetime(df_count_final['DateId'], format='%Y%m%d')
    df_count_final['TimeId'] = pd.to_datetime(df_count_final['TimeId'], format='%H%M').dt.time

    # Create a new column with the combined datetime (string variable)
    df_count_final['Timestamp'] = df_count_final['DateId'].astype(str) + 'T' + df_count_final['TimeId'].astype(str)
    # sort the DataFrame
    df_count_final= df_count_final.sort_values(by=['LocationName','Timestamp'], ascending=False)

    # Rename columns
    df_count_final = df_count_final.rename(columns={'InCount': 'In', 'OutCount': 'Out', 'LocationName': 'Name'})
    # Reorder columns and keep only certain columns
    columns_to_keep = ['In', 'Out', 'Timestamp', 'Name']  # Define the columns you want to keep and their desired order
    df_count_final = df_count_final[columns_to_keep]

    # unique_values_locations = df_count_final['Name'].unique()
    # print(unique_values_locations)

    # Define the mapping of old values to new values @LB Umlaute angepasst (aequivalent zu Vorjahresdaten)
    value_mapping = {'vbz_ost_nord': 'Ost-Nord total', 'vbz_ost_sbb': 'Ost-SBB total', 'vbz_ost_sued': 'Ost-Süd total',
                     'vbz_ost_vbz': 'Ost-VBZ Total', 'vbz_west_nord': 'West-Nord total', 'vbz_west_sbb': 'West-SBB total',
                     'vbz_west_sued': 'West-Süd total', 'vbz_west_vbz': 'West-VBZ total'}

    # Replace old values with new values in column 'Name'
    df_count_final['Name'] = df_count_final['Name'].replace(value_mapping,)

    # print(df_count_final.columns)
    # print('Fetching from API - check')
    # print(df_count_final['Name'].unique())
    # # print(df_count_final.head())

    # writing file out > trying to write it out the same way Odi did it
    field_names = ['In', 'Out', 'Timestamp', 'Name']
    writer = csv.DictWriter(sys.stdout, field_names, quoting=csv.QUOTE_NONNUMERIC)
    writer.writeheader()

    # df to dict
    dict_from_df = df.to_dict(orient='records')

    # looping an writing
    for obs in dict_from_df:
    writer.writerow({
        'In': obs['In'],
        'Out': obs['Out'],
        'Timestamp': obs['Timestamp'],
        'Name': loc['Name']
    })

    # print(df_count_final)
    # df_count_final.to_csv("sys.stdout", index = False)


except Exception as e:
    print("Error: %s" % e, file=sys.stderr)
    print(traceback.format_exc(), file=sys.stderr)
    sys.exit(1)
finally:
    sys.stdout.flush()
