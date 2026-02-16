# -*- coding: utf-8 -*-
"""Convert data from json to tabular format

Read json file and normalize in pandas df. Export tp CSV or parquet

Usage:
  convert_to_table.py  --dir <dir> --filename_json <filename_json> --filename_csv <filename_csv>
  convert_to_table.py (-h | --help)
  convert_to_table.py --version

Options:
  -h, --help                            Show this screen.
  --version                             Show version.
  -d, --dir <dir>                       Directory to write fi
  -fi, --filename_json <filename_json>  Name of the json to read.
  -fi, --filename_csv <filename_csv>    Name of the csv to write.

"""
from docopt import docopt


# get arguments
arguments = docopt(__doc__, version='Export data from MuseumPlus 1.0')

import pandas as pd
import os

# constants

# the sub elements of these json fields get extracted to seperate columns. See: normalize_to_cols()
NORMALIZE_TO_COL_JSON_COLNAMES = ['Urheber*innen', 'Datierung', ]

# the sub elements of these json fields get extracted into ONE column see: extract_json()
EXTRACT_IN_COL_JSON_COLNAMES = [
    'Titel_Bezeichnungen',
    'Masse',
    'Provenienz_Details', 
    'Inschriften', 
    'Literatur', 
    'Herstellungsort',
]

data_dir = arguments['--dir'] #"automation/mrz_kamerun_objekte/export"
filename_json = arguments['--filename_json'] #"kamerun_objekte.json"
filename_csv = arguments['--filename_csv'] #"kamerun_objekte.csv"



# functions

def normalize_to_cols(df, colname_list):
    """
    Normalizes all columns of given list to seperate columns and drops original column.
    
    :param df: Description
    :param colname_list: Description
    """
    for col in colname_list:
        print("_______________________________________________________________")
        print(col)
        normalized = pd.json_normalize(df[col].explode())

        df = pd.concat([df, normalized], axis=1)
        print(normalized)
        df = df.drop(columns=col)

    return df

def extract_json(x, sep_level1="\n", sep_level2= " "):
    """
    Takes a json object an extracts the given fields to a string.
    Goes 2 levels deep. Each level has its own seperator
    
    :param x: json object
    :param field: key of the field you want
    :param sep_level1: Seperator
    :param sep_level2: Seperator
    """
    if not isinstance(x, list) or len(x) == 0:
        return pd.NA
    
    output = ""
    for y in x:
        for z in y:
            output = output + z + ": " + y[z] + sep_level2
        output += sep_level1

    return output



if __name__ == "__main__":
    filepath_json = os.path.join(data_dir, filename_json)
    print("Reading", filepath_json)
    df = pd.read_json(filepath_json)
    print(df)

    df = normalize_to_cols(df, NORMALIZE_TO_COL_JSON_COLNAMES)

    for col in EXTRACT_IN_COL_JSON_COLNAMES:
        print("extract_json for:", col)
        df[col]= df[col].apply(extract_json, sep_level1="\n", sep_level2= " ")

    print("Columns in Final df:", df.columns)
    print(df)


    filepath_csv = os.path.join(data_dir, filename_csv)
    print("Writing", filepath_csv)
    df.to_csv(filepath_csv, index=False)
