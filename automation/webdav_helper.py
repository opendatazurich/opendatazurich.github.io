import os
from dotenv import load_dotenv
import pandas as pd
from webdav4.client import Client

# functions

def download_filetype(webdav_client, webdav_folder, local_folder='', filetype='.csv'):
    """
    Search :webdav_folder:
    Download files to :local_folder: if they are of type :filetype: (lowercase)
    Return list with info for downloaded files
    """

    print(f"Start Downloading {filetype} Files from WebDAV folder:", webdav_folder, " to local folder:", local_folder)
    files = webdav_client.ls(webdav_folder)

    filtered_files = []
    for file in files:
        filename = file['display_name']
        filepath = file['name']
        # Splitting the file path
        root, ext = os.path.splitext(filename)
        if ext.lower() == filetype:
            print("Downloading:", filepath)
            local_path = os.path.join(local_folder, filename)
            client.download_file(filepath, local_path)
            file['local_path'] = local_path
            filtered_files.append(file)

    return filtered_files

def download_file(webdav_client, filepath, local_path=''):
    """
    Downloads single file from webdav (:filepath:) to local storage (:local_path:).
    Checks if file exists before.
    Returns: file path of downloaded file on local disk
    """

    # Splitting the file path
    f_name = os.path.basename(filepath)

    if not webdav_client.exists(filepath):
        print("File not found:", filepath)
    
    local_filepath= os.path.join(local_path,f_name)
    webdav_client.download_file(filepath, local_filepath)
    print("Downloaded file from:", filepath, "to:", local_filepath)

    return local_filepath


def concat_files(csv_files, seperator=","):
    """
    Load and concat locally stored CSVs in pandas
    Return pandas dataframe
    """
    df = pd.DataFrame()
    for csv_file in csv_files:
        csv_path = csv_file['local_path']
        csv_file_name = csv_file['display_name']
        print("Loading:", csv_path)
        csv = pd.read_csv(csv_path, sep=seperator, dtype=str)
        csv['source'] = csv_file_name
        df = pd.concat([df, csv])
    return df


if __name__ == "__main__":
    load_dotenv()
    WEBDAV_USER = os.getenv('WEBDAV_USER')
    WEBDAV_PASSWORD = os.getenv('WEBDAV_PW')

    # connect to webdav
    url = 'https://www.ssz-webdav.stadt-zuerich.ch/OGD_Dropzone/'
    client = Client(url, auth=(WEBDAV_USER, WEBDAV_PASSWORD), verify=False)
    # download files from webdav
    csv_files = download_filetype(client, webdav_folder='INT_ERZ/khkw/auto_massen_energien', local_folder="", filetype='.csv')
    #read an concat downloaded files
    df = concat_files(csv_files, seperator=",")
    print(df)
