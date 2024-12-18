# -*- coding: utf-8 -*-
"""Convert CSV File to parquet file

Usage:
  csv_to_parquet.py --csv_input <csv_path> --parquet_export <parquet_path> [--dtypes <dtpye_dict>]
  csv_to_parquet.py -i ogd_katalog_inventar.csv -e ogd_katalog_inventar.parquet -d '{"anzahl_ressourcen":"float","datentyp":"category"}'
  csv_to_parquet.py (-h | --help)
  csv_to_parquet.py --version

Options:
  -h, --help                        Show this screen.
  --version                         Show version.
  -i, --csv_input <csv_path>        Path to CSV File.
  -e, --parquet_export <parquet_path>        Patho to parquet Export.
  -d, --dtypes <dtpye_dict>         Dictionairy with column names an desired Datatype.

"""

import pandas as pd
import json
from docopt import docopt

arguments = docopt(__doc__, version="1.0")

print(arguments['--csv_input'])
print(arguments['--parquet_export'])
print(arguments['--dtypes'])


def read_csv_file(filepath, dtype_dict=None):
    """
    Read CSV file to dataframe.
    Parameters:
        filepath:               path and filename of CSV
        dtype_dict (optional):  json with column name an desired datatype. 
                                example: '{"anzahl_ressourcen":"float","datentyp":"category"}'
    """
    # use datatype dictionairy if provided
    if dtype_dict:
        dtypes = json.loads(dtype_dict)
    else:
        dtypes = None
    # load df
    print("Reading CSV", filepath)
    df = pd.read_csv(filepath, dtype=dtypes)
    print(df.info())
    return df

def save_as_parquet(df, outpath):
    """
    Save dataframe as parquet
    Parameters: 
        df:         pandas dataframe
        outpath:    path and filename for parquet file
    Returns:
        None
    """
    print("Save parquet to ", outpath)
    df.to_parquet(outpath, index=False)

def convert_csv_to_parquet(filepath, outpath, dtype_dict=None):
    """
    Calling separate functions read_csv_file and save_as_parquet
    Returns: 
        None

    """
    df = read_csv_file(filepath, dtype_dict)
    save_as_parquet(df, outpath)


if __name__ == '__main__':
    convert_csv_to_parquet(arguments['--csv_input'], arguments['--parquet_export'], arguments['--dtypes'])