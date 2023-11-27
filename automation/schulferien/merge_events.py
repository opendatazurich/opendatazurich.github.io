#!/usr/bin/env python3

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

try:
    # create tmp table
    DATABASE_NAME = os.path.join(__location__, 'data.sqlite')
    conn = sqlite3.connect(DATABASE_NAME)
    c = conn.cursor()
    c.execute('DROP TABLE IF EXISTS tmp')
    c.execute(
        '''
        CREATE TABLE tmp (
            start_date iso_date,
            end_date iso_date,
            summary text,
            created_date iso_date,
            UNIQUE(start_date, end_date, summary)
        )
        '''
    )

    # add entries to tmp table
    query = "insert into tmp "
    query += "select min(start_date) start_date, max(end_date) end_date, summary, min(created_date) created_date "
    query += "from data group by summary, strftime('%Y', start_date) having count(1) > 1"
    c.execute(query)

    # delete original entries from data
    query = "delete from data where ROWID in ("
    query += "select d.ROWID from data d inner join tmp t on ("
    query += "t.summary = d.summary and strftime('%Y', t.start_date) = strftime('%Y', d.start_date)))"
    c.execute(query)

    # add records from tmp to data
    query = "insert into data select * from tmp"
    c.execute(query)
    c.execute('DROP TABLE IF EXISTS tmp')

    conn.commit()
except Exception as e:
    print("Error: %s" % e, file=sys.stderr)
    print(traceback.format_exc(), file=sys.stderr)
    sys.exit(1)
finally:
    conn.close()
