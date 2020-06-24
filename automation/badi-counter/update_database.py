#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# This script creates a new sqlite database based on the CSV is reiceives as an argument
# The sqlite database is used as an intermediate step to merge new data in existing CSVs

import sqlite3
import csv
import traceback
import os
import sys


__location__ = os.path.realpath(
    os.path.join(
        os.getcwd(),
        os.path.dirname(__file__)
    )
)

def is_int(v):
    try:
        int(v)
        return True
    except (TypeError, ValueError):
        return False

DATABASE_NAME = os.path.join(__location__, 'data.sqlite')
conn = sqlite3.connect(DATABASE_NAME)
try:
    # load the csv to sqlite db
    assert len(sys.argv) == 2, "Call script with CSV file as parameter"
    filename = sys.argv[1]
    columns = []
    column_types = {}
    with open(filename,'r') as f:
        dr = csv.DictReader(f) 
        if not columns:
            columns = dr.fieldnames
            column_types = {c: 'integer' for c in columns}
        to_db = []
        for r in dr:
            db_row = []
            for col in columns:
                db_row.append(r[col])
                if not is_int(r[col]):
                    column_types[col] = 'text'
            to_db.append(db_row)

    # create db
    c = conn.cursor()
    columns_defs = ", \n".join([f"{c} {t}" for c, t in column_types.items()])
    c.execute(f'CREATE TABLE IF NOT EXISTS data({columns_defs})')
    c.execute("CREATE UNIQUE INDEX IF NOT EXISTS data_unique ON data(id, date)");

    # add entries
    for row in to_db:
        query = 'INSERT INTO data (\n'
        query += ",\n".join(columns)
        query += ') VALUES ('
        query += ",".join(['?'] * len(columns))
        query += ');'
        try:
            c.execute(query, row)
            conn.commit()
            print("Added new entry")
        except sqlite3.IntegrityError:
            data = dict(zip(columns, row))
            query = 'UPDATE data set\n'
            query += ",\n".join([f"{c} = ?" for c in columns])
            query += ' WHERE id = ? and date = ?'
            row.append(data['id'])
            row.append(data['date'])
            c.execute(query, row)
            conn.commit()
            print("Updated entry")
except Exception as e:
    print("Error: %s" % e, file=sys.stderr)
    print(traceback.format_exc(), file=sys.stderr)
    sys.exit(1)
finally:
    conn.close()
