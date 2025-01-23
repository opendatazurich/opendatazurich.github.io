import requests
import pandas as pd
import re
headers = {'Accept': 'application/json'}
SSL_VERIFY = True


headers = {'Accept': 'application/json'}
SSL_VERIFY = True

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

    # zaehlkreise_df["geoLevelnummer"] = zaehlkreise_df["geoLevelnummer"].astype('int64')
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
    Defining dicitonary with columns from json as keys and output columns as values for mapping with historical data. 
    Contains all columns in correct order.
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
               "StaendeNein":"StaendeNein",
                #"url":"url"
    }

    return rename_dict

def get_rename_dict_output_table(): 
    """
    Defining dicitonary with columns from historical data as keys and output columns as values. 
    Contains all columns in correct order.
    """
    rename_dict = {"Abstimmungs_Datum":"Abstimmungs_Datum",
               "Nr_Politische_Ebene":"Nr_Politische_Ebene",
               "Name_Politische_Ebene":"Name_Politische_Ebene",
               "Abstimmungs_Text":"Abstimmungs_Text",
               "Nr_Resultat_Gebiet":"Nr_Resultat_Gebiet",
               "Name_Resultat_Gebiet":"Name_Resultat_Gebiet",
               "Nr_Wahlkreis_StZH":"Nr_Wahlkreis_StZH",
               "Name_Wahlkreis_StZH":"Name_Wahlkreis_StZH",
               "Stimmberechtigt":"Stimmberechtigt",
               "Ja":"Ja_Absolut",
               "Nein":"Nein_Absolut",
               "Stimmbeteiligung (%)":"Stimmbeteiligung_Prozent",
               "Ja (%)":"Ja_Prozent",
               "Nein (%)":"Nein_Prozent",
               "StaendeJa":"Staende_Ja",
               "StaendeNein":"Staende_Nein",
                #"url":"url"
    }

    return rename_dict

def base_absitmmung_url():
    """
    Defining base urls from where data can get fetched
    """
    urls = {'Eidgenössisch':'https://ckan.opendata.swiss/api/3/action/package_show?id=echtzeitdaten-am-abstimmungstag-zu-eidgenoessischen-abstimmungsvorlagen',
            'Kanton Zürich':'https://ckan.opendata.swiss/api/3/action/package_show?id=echtzeitdaten-am-abstimmungstag-zu-kantonalen-abstimmungsvorlagen',
            'Stadt Zürich':'https://ckan.opendata.swiss/api/3/action/package_show?id=echtzeitdaten-am-abstimmungstag-des-kantons-zurich-kommunale-und-regionale-vorlagen'}

    return urls


def columns_to_drop():
    """
    Defining list with column names to drop after fetching results
    """
    return ['abstimmtag', 'annahmekriteriumTyp', 'annahmekriteriumTypId', 'bezirke', 'gemeinden', 'geoLevelLevel', 'geoLevelParentnummer', 'geoLevelname', 'geschaeftsArt', 'geschaeftsArtId', 'geschaeftsSubTyp', 'geschaeftsSubTypId', 'geschaeftsTyp', 'geschaeftsTypId', 'hauptvorlagenId', 'kantone', 'nochKeineInformation', 'notfalltext', 'provisorisch', 'reihenfolgeAnzeige', 'reserveInfoText', 'timestamp', 'vorlageAngenommen', 'vorlageAngenommenGesamtbetrachtung', 'vorlageBeendet', 'vorlagenArtId', 'vorlagenTitel', 'zaehlkreise']

# , 'geoLevelnummer'
