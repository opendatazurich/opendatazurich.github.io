# pip install google-cloud-storage
import os
import io
import sys
import pandas as pd
from datetime import datetime, timedelta
from dotenv import load_dotenv
from google.cloud import storage
from ckanapi import RemoteCKAN, NotFound, NotAuthorized
import requests

#functions

def download_from_gcs(use_rolling_1_month_bool, bucket_name, download_folder=""):
    """
    Decide if we need the file from yesterday or from the complete last month and download it from google cloud storage.
    Return the path to the downloaded file
    """

    if use_rolling_1_month_bool:
        source_blob_name = "download_tracking_rolling_1_month.csv"
    else:
        # get yesterdays date
        yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y_%m_%d') # for daily triggering (override for manual date)
        print("yesterday:", yesterday)
        source_blob_name = f"download_tracking_{yesterday}.csv"

    # The path to which the file should be downloaded
    destination_file_name = os.path.join(download_folder, source_blob_name)

    storage_client = storage.Client()
    print("Get bucket:", bucket_name)
    bucket = storage_client.bucket(bucket_name)


    # Construct a client side representation of a blob.
    # Note `Bucket.blob` differs from `Bucket.get_blob` as it doesn't retrieve
    # any content from Google Cloud Storage. As we don't need additional data,
    # using `Bucket.blob` is preferred here.
    blob = bucket.blob(source_blob_name)
    print("Downloading", source_blob_name,"to",destination_file_name)
    blob.download_to_filename(destination_file_name)

    return destination_file_name


def load_current_file(filename):
    """
    Load the file that what downloaded into df
    """
    df_new = pd.read_csv(filename, parse_dates=['date'])
    return df_new



def add_missing_metadata():
    """
    Add metadata from CKAN-API in case it is missing
    """
    pass



def get_historical_data(ckan, resource_id, year):
    """
    Download parquet with historical data from OGD catalogue.
        Needs 
        - Resource ID to parquet file
        - ckan connection
    return pandas df
    """
    resource = ckan.action.resource_show(id=resource_id)

    dataset_id = resource['package_id']
    download_url = f"{BASE_URL}/dataset/{dataset_id}/resource/{resource_id}/download"
    print("Download URL:", download_url)

    # Versuche Datei herunterzuladen
    headers = {"Authorization": API_KEY}
    response = requests.get(download_url, headers=headers)

    if response.status_code == 200:
        file_like = io.BytesIO(response.content)
        df = pd.read_parquet(file_like)
        print("Datei geladen")
    else:
        print(f"Fehler beim Download: {response.status_code} - {response.text}")


    return df

def concat_historical_and_current_data(df_all, df_new):
    """
    Check if current data is already in historical data (and delete if so).
    Add current data to historical data
    """
    # Hole die eindeutigen Datumswerte aus df
    dates_to_remove = df_new['date'].unique()
    print("dropping dates from existing data, if present:", dates_to_remove)

    # Entferne die Zeilen aus df_all, deren 'date' in dates_to_remove enthalten ist
    df_all_filtered = df_all[~df_all['date'].isin(dates_to_remove)]

    # concat dfs
    df_compl = pd.concat([df_all_filtered, df_new])
    # drop duplicaes
    df_compl = df_compl.drop_duplicates()
    # sort
    df_compl = df_compl.sort_values(by=list(df_compl))

    print("New df has dates from:", df_compl['date'].min(), " to ", df_compl['date'].max())

    return df_compl

def save_updated_data_to_file(df, upload_filename, year):
    """
    Save to CSV and parquet
    """
    upload_filename_year = upload_filename + "_" + year
    print("write parquet and csv to: ", upload_filename)
    df.to_parquet(f"{upload_filename_year}.parquet")
    df.to_csv(f"{upload_filename_year}.csv")



# arguments
year = sys.argv[1]

# only for local testing
# os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "ogd/webstatistiken/google-download-tracking-sa.json"


load_dotenv(override=True)
# for distinction: use file from yesterday, oder complete last month
# needs an input for the github workflow (default false)

USE_ROLLING_1_MONTH = os.getenv("USE_ROLLING_1_MONTH")
print("USE_ROLLING_1_MONTH:", USE_ROLLING_1_MONTH)
# convert string to bool
use_rolling_1_month_bool = bool(USE_ROLLING_1_MONTH.lower() == "true")

# bucket name from google cloud
bucket_name = "ssz-download-tracking"

#connect to ckan
BASE_URL = os.getenv('CKAN_BASE_URL')
API_KEY = os.getenv('CKAN_API_KEY')
ckan = RemoteCKAN(BASE_URL, apikey=API_KEY)
df_all = get_historical_data(ckan, resource_id = "c17a0cbd-f303-4f51-80e1-d01edec3373f", year=year)

destination_file_name = download_from_gcs(use_rolling_1_month_bool, bucket_name)
df_new = load_current_file(destination_file_name)
print(df_new)




# add additional metadata here
# ...

df_compl = concat_historical_and_current_data(df_all, df_new)

save_updated_data_to_file(df_compl, upload_filename='ogd_katalog_downloads', year=year)
