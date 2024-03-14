#!/usr/bin/env python3
"""Merge data from CSV to an existing SQLite db

Usage:
  merge_data.py --file <path-to-file> --database <path-to-db>
  merge_data.py (-h | --help)
  merge_data.py --version

Options:
  -h, --help                   Show this screen.
  --version                    Show version.
  -f, --file <path-to-file>    Path to CSV file
  -d, --database <path-to-db>  Path to SQLite database file

"""

import sqlite3
import csv
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

print("trying to read in data")

try:
    # read in sql database
    filename = arguments['--file']
    to_db = []
    with open(filename, 'r') as f:
        dr = csv.DictReader(f) 
        for r in dr:
            to_db.append(dict(r))

    # print(to_db[1])
    # print(len(to_db))
    print("succsesfully read in today data to database")

    db_path = arguments['--database']
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    for data in to_db:
        try:
            print(data)
            c.execute(
                '''
                INSERT INTO data
                VALUES
                (?,?,?,?)
                ''',
                list(data.values())
            )
            print("Successfully added new entry.")
        except sqlite3.IntegrityError:
            try:
                # keys that are updated
                update_keys = [
                    'In',
                    'Out',
                ]
                for key in update_keys:
                    if key in data and data[key] is not None and data[key] != '':
                        c.execute(
                            f'UPDATE data SET "{key}" = ? WHERE Timestamp = ? and Name = ?;',
                            [data[key], data['Timestamp'], data['Name']]
                        )
                        print(f"Successfully updated field '{key}': {data[key]} ({data['Timestamp']}, {data['Name']}).")
            except sqlite3.Error as e:
                print("Error: an error occured in sqlite3: ", e.args[0], file=sys.stderr)
                conn.rollback()
                raise
        finally:
            conn.commit()

except Exception as e:
    print("Error: %s" % e, file=sys.stderr)
    print(traceback.format_exc(), file=sys.stderr)
    sys.exit(1)
finally:
    conn.close()
