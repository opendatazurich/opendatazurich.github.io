import os
from datetime import datetime
import pandas as pd
from webdav4.client import Client
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())


# functions

def download_csv(webdav_client, webdav_folder, local_folder=''):
    """
    Search :webdav_folder:
    Download files to :local_folder: if they are CSV
    Return list with info for downloaded files
    """

    print("Start Downloading CSV Files from:", webdav_folder, " to:", local_folder)
    files = webdav_client.ls(webdav_folder)

    csv_files = []
    for file in files:
        filename = file['display_name']
        filepath = file['name']
        # Splitting the file path
        root, ext = os.path.splitext(filename)
        if ext == '.csv':
            print("Downloading:", filepath)
            local_path = os.path.join(local_folder, filename)
            client.download_file(filepath, local_path)
            file['local_path'] = local_path
            csv_files.append(file)

    return csv_files

def concat_files(csv_files):
    """
    Load and concat locally stored csvs in pandas
    Return pandas dataframe
    """
    df = pd.DataFrame()
    for csv_file in csv_files:
        csv_path = csv_file['local_path']
        csv_file_name = csv_file['display_name']
        print("Loading:", csv_path)
        csv = pd.read_csv(csv_path, sep=';', dtype=str)
        csv['source'] = csv_file_name
        df = pd.concat([df, csv])
    return df

def data_preparation(df):
    """
    Perform data preparation tasks to conform opendatazurich guidelines
    Returns pandas dataframe
    """
    print("Preparing data")
    # drop duplicates
    df = df.drop_duplicates(subset=["Titel","Beschlussnummer","Beschlussdatum","Federführendes Departement"], keep='last').copy()

    # parse dates
    df['Beschlussdatum'] = pd.to_datetime(df['Beschlussdatum'], format="%d.%m.%Y")

    # replace critical characters from string colums
    ## get str cols
    str_cols = df.select_dtypes(include=['object']).columns
    for col in str_cols:
        # replace " if present, as we will use them as quote char
        df[col] = df[col].str.replace('"',"'")

    # add urls to Stadtratsbeschlüsse
    ## date info
    df['year'] = df['Beschlussdatum'].dt.strftime('%Y')
    df['month'] = df['Beschlussdatum'].dt.strftime('%m')
    # rearrange beschlussnummer for url
    df[["Beschlussnummer_number","Beschlussnummer_year"]] = df['Beschlussnummer'].str.split("/", expand=True)
    # add leading zeros
    df["Beschlussnummer_number"] = df["Beschlussnummer_number"].str.zfill(4)
    # concat url
    df["Link"] = "https://www.stadt-zuerich.ch/de/politik-und-verwaltung/politik-und-recht/stadtratsbeschluesse/" + df["year"] + "/" + df["month"] + "/stzh-strb-" + df["Beschlussnummer_year"] + "-" + df["Beschlussnummer_number"] + ".html"

    # sort
    df = df.sort_values(by=["Beschlussdatum","Beschlussnummer_number"], ascending=True)

    return df

def save_df_to_file(df, 
                    output_filename = "SKZ-Beschluesse", # without extension
                    output_cols = ["Titel","Beschlussnummer","Beschlussdatum","Federführendes Departement","Link"]):
    """
    Write df to files.
    """
    # write files
    print(f"Writing {output_filename}.csv")
    df[output_cols].to_csv(f"{output_filename}.csv", index=False, sep=",", encoding="utf-8", quotechar='"')
    print(f"Writing {output_filename}.parquet")
    df[output_cols].to_parquet(f"{output_filename}.parquet", index=False, )




if __name__ == "__main__":

    WEBDAV_USER = os.getenv('WEBDAV_USER')
    WEBDAV_PASSWORD = os.getenv('WEBDAV_PASSWORD')

    # connect to webdav
    url = 'https://www.ssz-webdav.stadt-zuerich.ch/OGD_Dropzone/'
    client = Client(url, auth=(WEBDAV_USER, WEBDAV_PASSWORD), verify=False)
    # download files from webdav
    csv_files = download_csv(client, webdav_folder='/INT_AV/av_skz_strb_oe_datum', local_folder="")
    # load files into pandas
    combined_df = concat_files(csv_files)
    # prepare data
    prepared_df = data_preparation(combined_df)
    # save prepared df
    save_df_to_file(prepared_df, output_filename="SKZ-Beschluesse", output_cols=["Titel","Beschlussnummer","Beschlussdatum","Federführendes Departement","Link"])
