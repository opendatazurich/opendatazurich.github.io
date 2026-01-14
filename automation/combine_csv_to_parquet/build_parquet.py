import pandas as pd
import requests
import json
import pyarrow as pa
import pyarrow.parquet as pq

from dataset_metadata import dataset_metadata



def get_csv_urls(ckan_base_url, dataset_id):
    """
    Gets the download urls for all csv ressources of a ckan dataset with :dataset_id:
    
    :param ckan_base_url: Base URL from CKAN
    :param dataset_id: Dataset Slug from CKAN
    """
    url = f"{ckan_base_url}/api/action/package_show?id={dataset_id}"
    csv_list = []
    r = requests.get(url)
    j = json.loads(r.text)
    ressources = j['result']['resources']
    for ressource in ressources:
        download_url = ressource['url']
        if download_url.endswith(".csv"):
            print(download_url)
            csv_list.append(download_url)
    return csv_list


def load_and_merge_csvs(csv_list, metadata):
    """
    Downloads all csv files from :csv_list: and casts datatypes, according to :dtypes:.
    Timestamps are formatted
    All csv file are appended to one dataframe

    
    :param csv_list: List of download urls for csv files
    :param metadata: dictionairy with metadata for each dataset (like dtype dict for reading csv)
    :return: Dataframe 
    """
    dtypes = metadata["dtypes"]
    df = pd.DataFrame()

    for csv in csv_list:
        print("Lade", csv)
        csv_df = pd.read_csv(csv, low_memory=False, dtype=dtypes, parse_dates=False)

        if {"date_col", "date_format_input"} <= metadata.keys():
            date_col = metadata["date_col"]
            date_format_input = metadata["date_format_input"]
            print("- Lokalisiere timestamp", date_col)
            csv_df[date_col] = localize_timestamp(csv_df[date_col], date_format_input)
        else:
            print(f"- KEINE Datetime Formatierung, weil date_col oder date_format_input nicht in dataset_metadata von  {metadata["dataset_id"]}")

        df = df._append(csv_df)

    return df

def localize_timestamp(date_col: pd.Series, date_format_input) -> pd.Series:
        """
        Docstring for localize_timestamp
        
        :param date_col: Series with timestamp as string
        :type date_col: pd.Series
        :param date_format_input: format of the timestamp like "%Y-%m-%dT%H:%M:%S"
        :return: Series with formatted timestamp in isoformat als string (e.g. 2026-01-07T19:00:00+01:00)
        :rtype: Series[Any]
        """
        # convert to datetime (no timezone)
        date_col_dt = pd.to_datetime(date_col, format=date_format_input, utc=False)

        # reformat 
        date_col_dt = date_col_dt.dt.tz_localize('Europe/Zurich', ambiguous='infer').apply(lambda x: x.isoformat())

        return date_col_dt

def write_file(df, filepath):
    """
    Write :df: as parquet to :filepath:
    Use special timestamp options
    
    :param df: pd.DataFrame
    :param filepath: Filepath
    """
    # Arrow-Tabelle mit Zeitzonen-Support
    table = pa.Table.from_pandas(df, preserve_index=False)

    # Schreiben ins Parquet
    pq.write_table(table, filepath, use_deprecated_int96_timestamps=False)


if __name__ == "__main__":

    ckan_base_url = "https://data.stadt-zuerich.ch"

    for dataset in dataset_metadata:
        print("-"*100)
        dataset_id = dataset["dataset_id"]
        parquet_filename = dataset["parquet_filename"]
        print(dataset_id)

        csv_list = sorted(get_csv_urls(ckan_base_url, dataset_id))
        # print(csv_list)

        df = load_and_merge_csvs(csv_list, dataset)
        print(df.info())
        print(df)
        filepath = f"{parquet_filename}"
        write_file(df, filepath=filepath)
        print("Datei geschrieben nach:", filepath)
