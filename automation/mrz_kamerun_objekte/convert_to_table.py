# -*- coding: utf-8 -*-
"""
Convert data from JSON to tabular format.

Reads a JSON file, normalizes selected nested fields into columns,
and exports the result to CSV.

Example:
    python convert_to_table.py \
        --dir automation/mrz_kamerun_objekte/export \
        --filename_json kamerun_objekte.json \
        --filename_csv kamerun_objekte.csv
"""

import argparse
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



def parse_args():
    parser = argparse.ArgumentParser(
        description="Convert MuseumPlus JSON export to tabular CSV."
    )

    parser.add_argument(
        "--dir",
        "-d",
        required=True,
        help="Directory where input JSON is located and CSV will be written.",
    )

    parser.add_argument(
        "--filename_json",
        required=True,
        help="Name of the JSON file to read.",
    )

    parser.add_argument(
        "--filename_csv",
        required=True,
        help="Name of the output CSV file.",
    )

    parser.add_argument(
        "--version",
        action="version",
        version="Export data from MuseumPlus 1.0",
    )

    return parser.parse_args()


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



def main():
    args = parse_args()

    data_dir = args.dir
    filename_json = args.filename_json
    filename_csv = args.filename_csv

    filepath_json = os.path.join(data_dir, filename_json)
    print("Reading", filepath_json)
    df = pd.read_json(filepath_json)
    print(df)

    df = normalize_to_cols(df, NORMALIZE_TO_COL_JSON_COLNAMES)

    for col in EXTRACT_IN_COL_JSON_COLNAMES:
        print("extract_json for:", col)
        df[col] = df[col].apply(extract_json, sep_level1="\n", sep_level2=" ")

    print("Columns in final df:", df.columns)
    print(df)

    filepath_csv = os.path.join(data_dir, filename_csv)
    print("Writing", filepath_csv)
    df.to_csv(filepath_csv, index=False)


if __name__ == "__main__":
    main()


