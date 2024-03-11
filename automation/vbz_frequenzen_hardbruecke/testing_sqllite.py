import sqlite3
import csv
import traceback
import os
import sys
from docopt import docopt
import pandas as pd
import sqlite3

os.getcwd()
filename = "vbz_frequenzen_hardbruecke/data/vbz_hardbruecke_frequenzen_2024.csv"
pd.read_csv(filename)

to_db = []
with open(filename, 'r') as f:
    dr = csv.DictReader(f)
    for r in dr:
        to_db.append(dict(r))



filename = arguments['--file']
to_db = []
with open(filename, 'r') as f:
    dr = csv.DictReader(f)
    for r in dr:
        to_db.append(dict(r))
