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



#
data = {'Name': ['Alice', 'Bob', 'Charlie', 'David'],
        'Age': [25, 30, 35, 28],
        'City': ['New York', 'San Francisco', 'Los Angeles', 'Chicago']}

df = pd.DataFrame(data)

df[1:20]

dict_from_df = df.to_dict(orient='records')
for obs in dict_from_df:
    print(obs['Name'])


df_arry[0]
