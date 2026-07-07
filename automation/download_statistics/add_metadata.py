
# Add Metadata
# 
# Datopian liefert eine Tabelle mit Aufrufen aus ihren logs. Diese enthalten diverse Metadaten. 
# Sie sind aber nicht vollständig. Deswegen sollen fehlende Metadaten ergänzt werden mit Informationen, die in den Metadaten von CKAN vorhanden sind.
# 
# Ziel ist, dass vor allem die Spalten `dataset_name` und `resource_name` möglichst immer befüllt sind.
# 
# Einschränkungen:
# - Die Metadaten von CKAN enthalten nur den aktuellen Stand. Werden z.B. Ressourcen gelöscht und ersetzt können vielleicht keine Metadaten mehr dazu gefunden werden.
# - Die Logs enthalten auch ungültige Anfragen, z.B. für Datensätze, die es nicht gibt, oder mit vertippern. Hier können keine Metadaten zugeordnet werden
# 
# Fehlende Metadaten bleiben erhalten, werden aber mit "UNKNOWN" gekennzeichnet.


import os
import io
import logging
import json

from dotenv import load_dotenv
from ckanapi import RemoteCKAN

import pandas as pd
import requests


# setup logger
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

logger = logging.getLogger(__name__)



# functions

def get_ckan_metadata(ckan_url):
    """
    Get metadata from CKAN as JSON and convert to pandas dataframe.
    
    :param ckan_url: url for ckan metadata json
    :return: df with metadata
    :rtype: pd.DataFrame
    """
    logger.info(f"Getting CKAN metadata from {ckan_url}")
    r = requests.get(ckan_url)
    ckan = pd.DataFrame(json.loads(r.content)['result'])

    return ckan



# Funktion um Metadaten von Dataset-Ebene auf Ressourcen-Ebene zu explodieren.
def dataset_to_resource(all_packages, prefix_resource_cols, resource_cols_to_keep):
    """
    Takes pandas df with all datasets (one row for each dataset).
    Column "resources" must contain json info for each resource like:
    [{'cache_last_updated': None, 'cache_url': None},...]
    Json fields in resource get a prefix: prefix_resource_cols
    This function explodes the df, so that each row in the output represents one resource.
    """
    # explode every resource in one row
    all_packages_exploded = all_packages.explode('resources')
    # json to columns and only keep the selected
    resource_cols = pd.json_normalize(all_packages_exploded['resources'])[resource_cols_to_keep]
    # add prefix, to avoid already existing columns
    resource_cols = resource_cols.add_prefix(prefix_resource_cols)
    # merge data from package/dataset
    merged = resource_cols.merge(all_packages, how='left', left_on=prefix_resource_cols+"package_id",right_on='id')

    # reset index, because later functions will need unique indices
    merged = merged.reset_index(drop=True)

    merged = merged.drop(columns=['resources'])

    return merged



def get_historical_data(year, dataset_name, base_url, api_key):
    """
    Download parquet with historical data from OGD catalogue. Checks if there is a ressource for the current year.
        Needs
        - ckan connection
        - year
        - dataset_name
    return pandas df
    """
    ckan = RemoteCKAN(base_url, apikey=api_key)
    dataset = ckan.action.package_show(id=dataset_name)
    resources = dataset["resources"]
    # check, if we already have a parquet file for the current year
    for resource in resources:
        if f"{year}.parquet" in resource["filename"]:
            resource_id = resource["id"]

    download_url = f"{base_url}/dataset/{dataset_name}/resource/{resource_id}/download"
    logger.info(f"Download URL: {download_url}")

    # Versuche Datei herunterzuladen
    headers = {"Authorization": api_key}
    response = requests.get(download_url, headers=headers)

    if response.status_code == 200:
        file_like = io.BytesIO(response.content)
        df = pd.read_parquet(file_like)
        logger.info("Datei geladen")
    else:
        logger.error(f"Fehler beim Download: {response.status_code} - {response.text}")


    return df



def extract_resource_id_from_datastore_sql(datopian):
    """
    Sonderbehandlung datastore_search_sql
    Hier kann man der URL ein SQL mitgeben. Dabei muss nach dem `FROM` die resource_id kommen. 
    In den meisten Fällen wird die ID schon korrekt von Datopian extrahiert. 
    Es gibt aber ein paar Spezialfälle, die wir hier noch abholen.


    pattern = r'(?i)from(?:%20|[+])%22([0-9a-f-]{36})%22'
    - (?i) → case-insensitive (FROM, from, From, ...)
    - from → sucht das FROM-Keyword
    - (?:%20|[+]) → Leerzeichen als %20 oder +
    - %22 → URL-codiertes Anführungszeichen (")
    - ([0-9a-f-]{36}) → UUID wird als Capture Group extrahiert
    - %22 → schliessendes Anführungszeichen
    """

    logger.info("Extrahiere resource_id von datastore_search_sql")

    pattern = r"(?i)from(?:%20|[+])%22([0-9a-f-]{36})%22"

    # Neue Spalte mit extrahierter ID
    datopian['extracted_resource_id'] = datopian['url'].str.extract(pattern)


    number_resource_id_new = datopian[
        (datopian['extracted_resource_id'].notna()) & 
        (datopian["resource_id"].isna())
    ].shape[0]
    logger.info(f"Anzahl Datensätze wo vorher kein resource_id, jetzt aber schon: {number_resource_id_new}")


    # auffüllen der Spalte, falls leer
    datopian['resource_id'] = datopian['resource_id'].combine_first(datopian['extracted_resource_id'])

    return datopian


def matching_via_resource_id(datopian: pd.DataFrame, ckan_exploded: pd.DataFrame):
    """
    Matching über resource_id
    
    Idee: Teilweise ist die Resource_id schon vorhanden und kann deswegen mit der resource_id von den CKAN Metadaten verknüpft werden. 
    Dadurch können wir diese Fälle nutzen um später, evtl. fehlende andere Metadaten (dataset_name, resource_name) hinzuzufügen.

    :return: merge_resource_id
    """

    logger.info("Join Metadaten über resource_id")

    # join über resource_id, evtl. doppelte Spalten werden mit Suffix gekennzeichnet
    merge_resource_id = datopian.merge(
        ckan_exploded, 
        how='left', 
        left_on='resource_id', 
        right_on='ckan_resource_id', 
        suffixes=('', '_over_resource_id')
    )

    # Quick Check für Fehler bei Merge (kein output, wenn alles ok)
    if merge_resource_id.shape[0] != datopian.shape[0]:
        logger.info("Anzahl hat sich durch merge verändert!")
        logger.info(f"Original {datopian.shape[0]}")
        logger.info(f"Neu {merge_resource_id.shape[0]}")


    number_dataset_name_new = merge_resource_id[
        (merge_resource_id["dataset_name"].isna()) &
        (merge_resource_id["name"].notna())
    ].shape[0]
    logger.info(f"Anzahl Datensätze wo vorher kein dataset_name, jetzt aber schon: {number_dataset_name_new}")

    return merge_resource_id


def matching_via_resource_name(merge_resource_id: pd.DataFrame, ckan_exploded: pd.DataFrame, datopian: pd.DataFrame):
    """
    Matching über resource_name 
    Teilweise ist ein resource_name vorhanden, aber kein dataset_name. Deswegen matchen wir über den resource_name und können dann hoffentlich damit einie dataset_name auffüllen.
    
    Probleme: 
    - Einige resource_names enthalten Artefakte am Ende des Dateinamens. Diese werden weggespalten: `ugz_ogd_meteo_h1_2020.csv%5C`
    - Resource names sind nicht unique. Deswegen kann nur mit denen gematched werden, die unique sind.

    :return: merge_resource_name
    """

    logger.info("Join Metadaten über resource_name")

    # entferne "%5C" String am Ende
    merge_resource_id["resource_name_stripped"] = merge_resource_id["resource_name"].str.rstrip("%5C")


    # finde eindeutige resource names
    value_counts = ckan_exploded['ckan_resource_name'].value_counts() 
    # Filtere auf Werte, die nur einmal vorkommen
    unique_names = value_counts[value_counts == 1].index
    ckan_exploded_unique_names = ckan_exploded[ckan_exploded['ckan_resource_name'].isin(unique_names)]


    # join über (bereinigten) resource_name, evtl. doppelte Spalten werden mit Suffix gekennzeichnet
    merge_resource_name = merge_resource_id.merge(
        ckan_exploded_unique_names, 
        how='left', 
        left_on='resource_name_stripped', 
        right_on='ckan_resource_name', 
        suffixes=('', '_over_resource_name'))


    # Quick Check für Fehler bei Merge (kein output, wenn alles ok)
    if merge_resource_name.shape[0] != datopian.shape[0]:
        logger.info("Anzahl hat sich durch merge verändert!")
        logger.info(f"Original {datopian.shape[0]}")
        logger.info(f"Neu {merge_resource_name.shape[0]}")

    number_dataset_name_over_resource_name_new = merge_resource_name[
        (merge_resource_name["dataset_name"].isna()) &
        (merge_resource_name["name_over_resource_name"].notna())
    ].shape[0]
    logger.info(f"Anzahl Datensätze wo vorher kein dataset_name, jetzt aber schon: {number_dataset_name_over_resource_name_new}")

    return merge_resource_name

def populate_dataset_name(merge_resource_name: pd.DataFrame):
    """
    Auffüllen von dataset_name, nach fester Hierarchie.

    :return: merge_resource_name
    """
    logger.info("Auffüllen Spalte dataset_name")

    merge_resource_name['coalesce_dataset_name'] = (
        # nimm zuerst vorhandenen dataset name
        merge_resource_name['dataset_name']
        # falls, leer nimm Eintrag von matching über resource_id
        .combine_first(merge_resource_name['name'])
        # falls, leer nimm Eintrag von matching über resource_name
        .combine_first(merge_resource_name['name_over_resource_name'])
    )

    # ersetze alte Spalte durch neue erweiterte Spalte
    merge_resource_name['dataset_name'] = merge_resource_name['coalesce_dataset_name']

    return merge_resource_name


def populate_resource_name(merge_resource_name: pd.DataFrame):
    """
    Auffüllen von resource_name in neuer Spalte, nach fester Hierarchie.

    :return: merge_resource_name
    """
    logger.info("Auffüllen Spalte resource_name")

    merge_resource_name['coalesce_resource_name'] = (
        # nimm zuerst vorhandenen resource name
        merge_resource_name['resource_name']
        # falls, leer nimm Eintrag von matching über resource_id
        .combine_first(merge_resource_name['ckan_resource_name'])
        # falls, leer nimm Eintrag von matching über resource_name
        .combine_first(merge_resource_name['ckan_resource_name_over_resource_name'])
    )

    # ersetze alte Spalte durch neue erweiterte Spalte
    merge_resource_name['resource_name'] = merge_resource_name['coalesce_resource_name']

    return merge_resource_name

def populate_resource_id(merge_resource_name: pd.DataFrame):
    """
    Auffüllen von Resource_id

    :return: merge_resource_name
    """
    logger.info("Auffüllen Spalte resource_id")

    merge_resource_name['coalesce_resource_id'] = (
        # nimm zuerst vorhandenen resource id
        merge_resource_name['resource_id']
        # falls, leer nimm Eintrag von matching über resource_id
        .combine_first(merge_resource_name['ckan_resource_id'])
        # falls, leer nimm Eintrag von matching über resource_name
        .combine_first(merge_resource_name['ckan_resource_id_over_resource_name'])
    )


    # ersetze alte Spalte durch neue erweiterte Spalte
    merge_resource_name['resource_id'] = merge_resource_name['coalesce_resource_id']

    return merge_resource_name


def stats_before_after(before: pd.DataFrame, after: pd.DataFrame):
    """
    Statistiken für Vorher-Nachher-Vergleich
    
    :param before: dataset before adding metadata
    :type before: pd.DataFrame
    :param after: dataset after adding metadata
    :type after: pd.DataFrame
    """

    # Wie viele fehlende Fälle haben wir für die relevanten Spalten?
    missing_before = before[['dataset_name','resource_name','resource_id']].isna().sum()

    # Vergleich vorher-nachher
    missing_after = after[['dataset_name','resource_name','resource_id']].isna().sum()

    combine_for_plot = pd.concat([missing_before, missing_after], axis=1).rename(columns={0: "missing_before", 1:"missing_after"})
    logger.info(f"Anzahl Datensätze in Originaldatei: {before.shape[0]}")
    logger.info(f"Anzahl Datensätze nachher: {after.shape[0]}")
    logger.info(f"Vergleich Vorher-Nachher:\n{combine_for_plot}")

def filter_data(merge_resource_name: pd.DataFrame):
    """
    Filter dataset (rows and columns) to final shape
    
    :param merge_resource_name: unfiltered dataset
    :type merge_resource_name: pd.DataFrame
    """

    logger.info("Filtere Datensatz")

    # Datensätze, die behalten werden. Übernommen werden nur, wenn: 
    # dataset_name vohanden UND (resource_name vorhanden ODER resource_id vorhanden)
    to_keep = merge_resource_name[
        (merge_resource_name["dataset_name"].notna()) &
        ((merge_resource_name["resource_name"].notna()) | (merge_resource_name["resource_id"].notna()))
    ]
    logger.info(f"Anzahl valide Datensätze: {to_keep.shape[0]}")

    # Datensätze, die verloren gehen:
    to_drop = merge_resource_name.drop(index=to_keep.index)
    logger.info(f"Anzahl Datensätze, die nicht übernommen werden (weil dataset_name, resource_name und resource_id unbekannt): {to_drop.shape[0]}")

    return (to_keep, to_drop)



def add_metadata(datopian: pd.DataFrame):
    """
    Main function. Adding metadata from ckan to recieved dataframe.

    
    :param datopian: df with downloads stats. Needs columns `dataset_name`, `resource_name`, `resource_id`
    :type datopian: pd.DataFrame

    :return: merge_resource_name (df with updated metadata)
    """


    logger.info("Start adding metadata")

    # # Hole CKAN Metadaten (auf dataset ebene)
    ckan_url = 'https://data.stadt-zuerich.ch/api/3/action/current_package_list_with_resources?limit=1000'
    ckan_meta = get_ckan_metadata(ckan_url)

    # Funktion um Metadaten von Dataset-Ebene auf Ressourcen-Ebene zu explodieren.
    ckan_exploded = dataset_to_resource(ckan_meta[['id','name','resources']], prefix_resource_cols='ckan_resource_', resource_cols_to_keep=['id','name','package_id'])


    # Extrahiere resource_id von vom datastore_search_sql
    datopian = extract_resource_id_from_datastore_sql(datopian)

    # matching über resource_id
    merge_resource_id = matching_via_resource_id(datopian, ckan_exploded)

    # matching über resource_name
    merge_resource_name = matching_via_resource_name(merge_resource_id, ckan_exploded, datopian)

    # Auffüllen Spalte dataset_name
    merge_resource_name = populate_dataset_name(merge_resource_name)

    # Auffüllen Spalte resource_name
    merge_resource_name = populate_resource_name(merge_resource_name)

    # Auffüllen Spalte resource_id
    merge_resource_name = populate_resource_id(merge_resource_name)

    # statistiken zum vergleichen
    stats_before_after(before=datopian, after=merge_resource_name)

    # filtere daten
    to_keep, to_drop = filter_data(merge_resource_name)

    return to_keep, to_drop





if __name__ == "__main__":

    load_dotenv(override=True)

    # # Lade Rohdaten für Downloads
    # Die Funktion holt die Daten aus dem privaten Datensatz von CKAN.

    BASE_URL = os.getenv('CKAN_BASE_URL')
    API_KEY = os.getenv('CKAN_API_KEY')
    YEAR = "2026"
    datopian = get_historical_data(year=YEAR, dataset_name="prd_ssz_ogd_katalog_downloads", base_url=BASE_URL, api_key=API_KEY)


    to_keep, to_drop = add_metadata(datopian)

    # schreibe dateien
    filename = f"ogd_katalog_downloads_{YEAR}"
    COLS_TO_EXPORT = ["date","dataset_name","resource_name","resource_id","distinct_ips","user_agent","url","datastore_search_sql_query","hit_count"]
    to_keep[COLS_TO_EXPORT].to_parquet(f"C:\\Temp\\prd_ssz_ogd_katalog_downloads\\{filename}_bereinigt.parquet")
    to_drop[COLS_TO_EXPORT].to_parquet(f"C:\\Temp\\prd_ssz_ogd_katalog_downloads\\{filename}_dropped.parquet")

    to_keep[COLS_TO_EXPORT].to_csv(f"C:\\Temp\\prd_ssz_ogd_katalog_downloads\\{filename}_bereinigt.csv")