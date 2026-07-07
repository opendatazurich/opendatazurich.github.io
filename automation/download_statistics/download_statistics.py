import os
import io
import sys
import logging
import pandas as pd
from datetime import datetime, timedelta
from dotenv import load_dotenv
from google.cloud import storage
from ckanapi import RemoteCKAN, NotFound, NotAuthorized
import requests

import add_metadata

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


# functions

def download_from_gcs(use_rolling_1_month_bool, bucket_name, download_folder=""):
    """
    Download file from Google Cloud Storage.
    Decides based on use_rolling_1_month_bool whether to fetch yesterday's file or the rolling 1-month file.

    :param use_rolling_1_month_bool: if True, download rolling 1-month file; otherwise download yesterday's file
    :param bucket_name: name of the GCS bucket
    :param download_folder: local folder to download the file to
    :return: path to the downloaded file
    :rtype: str
    """

    if use_rolling_1_month_bool:
        source_blob_name = "download_tracking_rolling_1_month.csv"
    else:
        # get yesterdays date
        yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y_%m_%d') # for daily triggering (override for manual date)
        logger.info(f"Gestriges Datum: {yesterday}")
        source_blob_name = f"download_tracking_{yesterday}.csv"

    # The path to which the file should be downloaded
    destination_file_name = os.path.join(download_folder, source_blob_name)

    storage_client = storage.Client()
    logger.info(f"Hole Bucket: {bucket_name}")
    bucket = storage_client.bucket(bucket_name)


    # Construct a client side representation of a blob.
    # Note `Bucket.blob` differs from `Bucket.get_blob` as it doesn't retrieve
    # any content from Google Cloud Storage. As we don't need additional data,
    # using `Bucket.blob` is preferred here.
    blob = bucket.blob(source_blob_name)
    logger.info(f"Lade {source_blob_name} herunter nach {destination_file_name}")
    blob.download_to_filename(destination_file_name)

    return destination_file_name


def load_current_file(filename):
    """
    Load CSV file into a dataframe.

    :param filename: path to the CSV file
    :return: dataframe with parsed date column
    :rtype: pd.DataFrame
    """
    df_new = pd.read_csv(filename, parse_dates=['date'])
    return df_new



def get_historical_data(year, dataset_name, base_url, api_key):
    """
    Download parquet with historical data from OGD catalogue.
    Checks if there is a resource for the current year.

    :param year: year to look for (e.g. "2026")
    :param dataset_name: CKAN dataset name
    :param base_url: CKAN base URL
    :param api_key: CKAN API key
    :return: dataframe with historical data
    :rtype: pd.DataFrame
    """
    ckan = RemoteCKAN(base_url, apikey=api_key)

    dataset = ckan.action.package_show(id=dataset_name)
    resources = dataset["resources"]
    # check, if we already have a parquet file for the current year
    for resource in resources:
        if f"{year}.parquet" in resource["filename"]:
            resource_id = resource["id"]
            break

    download_url = f"{base_url}/dataset/{dataset_name}/resource/{resource_id}/download"
    logger.info(f"Download-URL: {download_url}")

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

def concat_historical_and_current_data(df_all, df_new, year, cols_to_keep):
    """
    Merge current data into historical data.
    Removes any dates from the historical data that are also present in the new data to avoid duplicates.

    :param df_all: historical data
    :param df_new: new data to add
    :param year: only keep data from this year onwards
    :param cols_to_keep: list of columns to retain
    :return: merged and deduplicated dataframe
    :rtype: pd.DataFrame
    """

    # select columns
    df_all = df_all[cols_to_keep]
    df_new = df_new[cols_to_keep]

    # Hole die eindeutigen Datumswerte aus df
    dates_to_remove = df_new['date'].unique()
    logger.info(f"Entferne folgende Daten aus bestehenden Daten (falls vorhanden): {dates_to_remove}")

    # Entferne die Zeilen aus df_all, deren 'date' in dates_to_remove enthalten ist
    df_all_filtered = df_all[~df_all['date'].isin(dates_to_remove)]

    # concat dfs
    df_compl = pd.concat([df_all_filtered, df_new])
    # only use data from current year
    first_day_of_year = pd.Timestamp(year)
    df_compl = df_compl[df_compl["date"]>=first_day_of_year]
    # drop duplicaes
    df_compl = df_compl.drop_duplicates()
    # sort
    df_compl = df_compl.sort_values(by=list(df_compl))

    logger.info(f"Neuer Datensatz enthält Daten von {df_compl['date'].min()} bis {df_compl['date'].max()}")

    return df_compl

def save_updated_data_to_file(df, upload_filename, year, dropped):
    """
    Save dataframe to CSV and parquet.
    Also saves dropped rows as a parquet artifact for debugging.

    :param df: main dataframe to save
    :param upload_filename: base filename (year will be appended)
    :param year: year suffix for the filename
    :param dropped: rows that were dropped, saved as a separate parquet for debugging
    """
    upload_filename_year = upload_filename + "_" + year
    logger.info(f"Schreibe Parquet und CSV nach: {upload_filename_year}")
    df.to_parquet(f"{upload_filename_year}.parquet")
    df.to_csv(f"{upload_filename_year}.csv", index=False)
    # save this as artifact for debugging
    dropped.to_parquet(f"{upload_filename_year}_dropped.parquet")

if __name__ == "__main__":

    COLS_TO_EXPORT = ["date","dataset_name","resource_name","resource_id","distinct_ips","user_agent","url","datastore_search_sql_query","hit_count"]

    # arguments
    year = sys.argv[1]
    logger.info(f"Jahr: {year}")

    # only for local testing
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "C:\\Users\\sszgua\\Python\\jupyter\\ogd\\webstatistiken\\google-download-tracking-sa.json" #"ogd/webstatistiken/google-download-tracking-sa.json"


    load_dotenv(override=True)
    # for distinction: use file from yesterday, oder complete last month
    # needs an input for the github workflow (default false)

    USE_ROLLING_1_MONTH = os.getenv("USE_ROLLING_1_MONTH")
    logger.info(f"USE_ROLLING_1_MONTH: {USE_ROLLING_1_MONTH}")
    # convert string to bool
    use_rolling_1_month_bool = bool(USE_ROLLING_1_MONTH.lower() == "true")

    # bucket name from google cloud
    bucket_name = "ssz-download-tracking"

    #connect to ckan
    BASE_URL = os.getenv('CKAN_BASE_URL')
    API_KEY = os.getenv('CKAN_API_KEY')
    df_all = get_historical_data(year=year, dataset_name = "prd_ssz_ogd_katalog_downloads", base_url=BASE_URL, api_key=API_KEY)
    destination_file_name = download_from_gcs(use_rolling_1_month_bool, bucket_name)
    df_new = load_current_file(destination_file_name)
    logger.info(f"\n{df_new}")


    # add additional metadata here
    to_keep, to_drop = add_metadata.add_metadata(df_new)

    df_compl = concat_historical_and_current_data(
        df_all, 
        to_keep, 
        year,
        COLS_TO_EXPORT
    )

    save_updated_data_to_file(
        df_compl, 
        upload_filename='ogd_katalog_downloads', 
        year=year,
        dropped=to_drop,
    )
