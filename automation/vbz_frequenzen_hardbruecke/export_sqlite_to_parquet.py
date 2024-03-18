#!/usr/bin/env python3
"""Export data from SQLite db to parquet

Usage:
  export_sqlite_to_parquet.py --file <path-to-file> --database <path-to-db>
  export_sqlite_to_parquet.py (-h | --help)
  export_sqlite_to_parquet.py --version

Options:
  -h, --help                   Show this screen.
  --version                    Show version.
  -d, --database <path-to-db>  Path to SQLite database file
  -f, --file <path-to-file>    Path to parquet file

"""

import sqlite3
import pandas as pd
import traceback
import os
import sys
from docopt import docopt

arguments = docopt(__doc__, version='Merge data from CSV to a database 1.0')
__location__ = os.path.realpath(
    os.path.join(
        os.getcwd(),
        os.path.dirname(__file__)
    )
)

try:
    print("trying to read in sqlite")
    filename_db = arguments['--database']
    conn = sqlite3.connect(filename_db)
    c = conn.cursor()

    df = pd.read_sql_query('select * from data order by Timestamp asc, Name asc;', conn)

    filename_parquet = arguments['--file']

    # change type of column
    df = df.astype({'In': 'int', 'Out': 'int', 'Name': 'str'})
    df["Timestamp"] = pd.to_datetime(df["Timestamp"])

    df.to_parquet(filename_parquet, index=False)

except Exception as e:

    print("Error: %s" % e, file=sys.stderr)
    print(traceback.format_exc(), file=sys.stderr)
    sys.exit(1)
finally:
    conn.close()





