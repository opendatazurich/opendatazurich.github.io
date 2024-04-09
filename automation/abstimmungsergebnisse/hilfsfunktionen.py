# Import Packages
import requests
import pandas as pd
import numpy as np
import json
import re
import pandas as pd

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


def get_de(list_with_dict):
    """
    Return all strings in a list of dictionaries where an entry's key 'langKey' equals the value 'de'
    """
    vorlagenTitel = [entry['text'] for entry in list_with_dict if entry['langKey'] == 'de'][0]
    return vorlagenTitel

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


def float_to_mixed_number(float_num):
    """
    Converting a fractional part of a float number (only .5 values) in a mixed number in text format
    """
    integer_part = int(float_num)
    fractional_part = float_num - integer_part

    if fractional_part != 0:
        denominator = 1/fractional_part
        denominator = int(denominator)
        mixed_number = f"{integer_part} {1}/{denominator}"
    else:
        mixed_number = str(integer_part)

    return(mixed_number)


def clean_names(list_of_names):
    """
    Cleaning names (org column names)
    Existing  names are turned into new one given only the string after the last dot (.)
    If there is no dot in an existing name, new  name equals existing column name.
    returns a dictionary with existing names as keys and cleaned names as values
    """
    r = re.compile("([^\\.]+$)")
    dict_old_new = {x:r.search(x).group() for x in list_of_names}
    return dict_old_new

def get_zaehlkreise_translation():
    """
    Defining DataFrame which translates geoLevelnummer into Wahlkreise number and text
    """
    zaehlkreise_df = pd.DataFrame({"geoLevelnummer":[10261, 20261, 30261, 40261, 50261, 60261, 70261, 80261, 90261],
                               "Nr_Wahlkreis_StZH":[2,3,4,5,6,7,8,9,10],
                               "Name_Wahlkreis_StZH":['Kreis 1+2','Kreis 3','Kreis 4+5','Kreis 6','Kreis 7+8','Kreis 9','Kreis 10','Kreis 11','Kreis 12']})

    zaehlkreise_df["geoLevelnummer"] = zaehlkreise_df["geoLevelnummer"].astype(str)
    return zaehlkreise_df


def get_ebene_gebiet_dict():
    """
    Defining ditionary with ebene/gebiet information
    """
    gebiet_dict = {1:'Eidgenossenschaft', 2:'Kanton Zürich', 3:'Stadt Zürich'}
    return gebiet_dict

def add_columns_resultat_gebiet(pandas_data_frame, nr_resultat_gebiet):
    """
    Adding two columns to a pandas data frame based on one input parameter (nr_result_gebiet)
    """
    pandas_data_frame['Nr_Resultat_Gebiet'] = nr_resultat_gebiet
    pandas_data_frame['Name_Resultat_Gebiet'] = get_ebene_gebiet_dict()[nr_resultat_gebiet]

    return pandas_data_frame

def add_columns_politische_ebene(pandas_data_frame, nr_politische_ebene):
    """
    Adding two columns to a pandas data frame based on one input parameter (nr_politische_ebene)
    """
    pandas_data_frame['Nr_Politische_Ebene'] = nr_politische_ebene
    pandas_data_frame['Name_Politische_Ebene'] = get_ebene_gebiet_dict()[nr_politische_ebene]

    return pandas_data_frame


def get_rename_dict():
    """
    Defining dicitonary with columns from json as keys and output columns as values. Contains all columns in correct order.
    """
    rename_dict = {"abstimmtag":"Abstimmungs_Datum",
               "Nr_Politische_Ebene":"Nr_Politische_Ebene",
               "Name_Politische_Ebene":"Name_Politische_Ebene",
               "vorlagenTitel":"Abstimmungs_Text",
               "Nr_Resultat_Gebiet":"Nr_Resultat_Gebiet",
               "Name_Resultat_Gebiet":"Name_Resultat_Gebiet",
               "Nr_Wahlkreis_StZH":"Nr_Wahlkreis_StZH",
               "Name_Wahlkreis_StZH":"Name_Wahlkreis_StZH",
               "anzahlStimmberechtigte":"Stimmberechtigt",
               "jaStimmenAbsolut":"Ja",
               "neinStimmenAbsolut":"Nein",
               "stimmbeteiligungInProzent":"Stimmbeteiligung (%)",
               "jaStimmenInProzent":"Ja (%)",
               "neinStimmenInProzent":"Nein (%)",
               "StaendeJa":"StaendeJa",
               "StaendeNein":"StaendeNein"}

    return rename_dict

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
