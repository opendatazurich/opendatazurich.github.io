# Import Packages
import requests
import pandas as pd
import numpy as np
import json
import re
from flatten_json import flatten

headers = {'Accept': 'application/json'}
SSL_VERIFY = True


# für Funktionen, die in mehreren Skripten gebraucht werden können
def get_request(url, headers, verify):
    """
    GET Request from url and return data as json
    """
    r = requests.get(url, headers=headers, verify=verify)
    data = r.json()

    return data

def make_url_list(url, headers, verify):
    """
    Erstellt Liste mit URLs, die dann abgefragt werden könnten
    """
    data = get_request(url, headers, verify)
    daten = pd.json_normalize(data, record_path=["result", "resources"])
    url_list = daten["url"]
    return url_list

def rename_columns(panda_data_frame):
    """
    Renaming columns of a panda data.frame.
    Existing column names are turned into new one given only the string after the last dot (.)
    If there is no dot in an existing column name, new column name equals existing column name.
    """
    col_old = panda_data_frame.columns.tolist()
    r = re.compile("([^\\.]+$)")
    col_new = [r.search(x).group() for x in col_old]
    df_col_dict = dict(map(lambda i,j : (i,j) , col_old,col_new))
    panda_data_frame_new = panda_data_frame.rename(columns = df_col_dict)
    return panda_data_frame_new

def cleaning_names(list_of_names):
    """
    Cleaning names (org column names)
    Existing  names are turned into new one given only the string after the last dot (.)
    If there is no dot in an existing name, new  name equals existing column name.
    returns a dictionary with existing names as keys and cleaned names as values
    """
    r = re.compile("([^\\.]+$)")
    col_new = [r.search(x).group() for x in col_old]
    df_col_dict = dict(map(lambda i,j : (i,j) , col_old,col_new))
    return df_col_dict

def zaehlkreis_daten(df, ch_single, zaehlkreis_alle):
        """
        Sucht Zählkreisdaten aus df heraus (dafür muss die Spalte "zaehlkreise" vorhanden sein).
        Output ist zaehlkreis_alle
        """
        df_zk = df[df['zaehlkreise'].notna()]

        for i in list(df_zk["zaehlkreise"].keys()):
            zk = df['zaehlkreise'][i]
            zaehlkreise_norm = pd.json_normalize(zk)
            zaehlkreise_norm['i'] = i
            zaehlkreise_norm['schweiz.vorlagen.vorlagenId'] = df['schweiz.vorlagen.vorlagenId'][i]
            zaehlkreise_norm['abstimmtag'] = df['abstimmtag'][i]
            #print(zaehlkreise_norm)          
            # join stände vorlage zaehlkreis-resultate
            join_zk = pd.merge(ch_single, zaehlkreise_norm, how='inner', on = ["schweiz.vorlagen.vorlagenId", "abstimmtag"])
            zaehlkreis_alle = pd.concat([zaehlkreis_alle, join_zk], ignore_index=True, sort=False)

        return zaehlkreis_alle

def base_absitmmung_url():
    """
    Defining base urls from where data can get scraped
    """
    urls = {'Eidgenössisch':'https://ckan.opendata.swiss/api/3/action/package_show?id=echtzeitdaten-am-abstimmungstag-zu-eidgenoessischen-abstimmungsvorlagen',
            'Kanton Zürich':'https://ckan.opendata.swiss/api/3/action/package_show?id=echtzeitdaten-am-abstimmungstag-zu-kantonalen-abstimmungsvorlagen',
            'Stadt Zürich':'https://ckan.opendata.swiss/api/3/action/package_show?id=echtzeitdaten-am-abstimmungstag-des-kantons-zurich-kommunale-und-regionale-vorlagen'}

    return urls


if __name__ == "__main__":
    # zum Testen des Moduls
    headers = {'Accept': 'application/json'}
    SSL_VERIFY = True
    url = 'https://ckan.opendata.swiss/api/3/action/package_show?id=echtzeitdaten-am-abstimmungstag-zu-eidgenoessischen-abstimmungsvorlagen'
    print(make_url_list(url, headers, SSL_VERIFY))

    # zähkreisdaten
    url_data = 'https://dam-api.bfs.admin.ch/hub/api/dam/assets/7686380/master'
    data = get_request(url, headers, SSL_VERIFY)
    ch_single = pd.DataFrame({
        'text': ['Volksinitiative «Nationalbankgewinne für die AHV»', 'Bundesgesetz über die Ausländerinnen und Auslä...','Änderung des Asylgesetzes'],
        'abstimmtag': [20060924,20060924,20060924],
        'schweiz.vorlagen.vorlagenId': [5230, 5240, 5250],
    })
    df = pd.json_normalize(data, record_path=["schweiz", "vorlagen", "kantone"], meta=[["abstimmtag"],["schweiz", "vorlagen", "vorlagenId"]] , errors='ignore')
    zaehlkreis_alle = pd.DataFrame()
    print(zaehlkreis_daten(df, ch_single, zaehlkreis_alle))
