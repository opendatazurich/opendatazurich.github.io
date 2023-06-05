# -*- coding: utf-8 -*-

import os
import sys
import csv
from ftplib import FTP
import traceback
from dotenv import load_dotenv, find_dotenv


load_dotenv(find_dotenv())

# host, user, pw aus dem .env File lesen
host = os.getenv('WAPO_FTP_HOST')
user = os.getenv('WAPO_FTP_USER')
pw = os.getenv('WAPO_FTP_PASSWORD')

 # config
stations = [
    {
        "directory": '/domains/open-data-transfer.space/tecson/upload_mythenquai',
        "filename": 'Mythenquai_406m.csv',
        "output_file": 'messwerte_mythenquai_today.csv',
    },
    {
        "directory": '/domains/open-data-transfer.space/tecson/upload_tiefenbrunnen',
        "filename": 'Tiefenbrunnen_406m.csv',
        "output_file": 'messwerte_tiefenbrunnen_today.csv',
    },
]

__location__ = os.path.realpath(
    os.path.join(
        os.getcwd(),
        os.path.dirname(__file__)
    )
)


def convert_csv_delim(output_path, input_path, input_delim=';', input_encoding='iso-8859-1'):
    with open(input_path, 'r', encoding=input_encoding) as f:
        reader = csv.DictReader(f, delimiter=input_delim)
        rows = []
        for r in reader:
            # strip keys and values of whitespace characters
            row = {k.strip(): v.strip() for k, v in r.items()}

            # skip row if the header is repeated
            if row['Datum/Zeit'] == 'Datum/Zeit':
                continue
            rows.append(row)

    header = rows[0].keys()
    with open(output_path, 'w', newline='', encoding='utf-8') as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=header, delimiter=',')
        writer.writeheader()
        writer.writerows(rows)


try:
    # login on FTP
    ftp = FTP(host)
    ftp.login(user, pw)

    for station in stations:
        # get data
        ftp.cwd(station['directory'])
        files_in_cwd = [f[0] for f in ftp.mlsd()]
        if station['filename'] not in files_in_cwd:
            raise Exception(f"File {station['filename']} not on FTP server in path {station['directory']}")

        with open(station['filename'], 'wb') as fp:
            ftp.retrbinary(f"RETR {station['filename']}", fp.write)

        # convert files to UTF-8 with comma delimiter
        convert_csv_delim(station['output_file'], station['filename'], input_delim=';', input_encoding='iso-8859-1')

        # delete the file on the FTP if everything was okay until here
        #ftp.delete(station['filename'])

    ftp.quit()


except Exception as e:
    print("Error: %s" % e, file=sys.stderr)
    print(traceback.format_exc(), file=sys.stderr)
    sys.exit(1)