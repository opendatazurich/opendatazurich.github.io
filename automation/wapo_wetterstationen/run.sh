#!/bin/bash

# Script to run a single scraper

set -e
set -o pipefail

function cleanup {
  exit $?
}
trap "cleanup" EXIT

DIR="$(cd "$(dirname "$0")" && pwd)"

# 1. Get current year file from CKAN
echo "Get current year file from CKAN (Mythenquai and Tiefenbrunnen)"
wget -nv https://data.stadt-zuerich.ch/dataset/sid_wapo_wetterstationen/download/messwerte_mythenquai_seit2007-heute.csv -O $DIR/messwerte_mythenquai.csv
wget -nv https://data.stadt-zuerich.ch/dataset/sid_wapo_wetterstationen/download/messwerte_tiefenbrunnen_seit2007-heute.csv -O $DIR/messwerte_tiefenbrunnen.csv

# 2. populate the database with the current CSV
echo "Populating databases from CSVs..."
rm -rf $DIR/mythenquai.sqlite
rm -rf $DIR/tiefenbrunnen.sqlite
sqlite3 $DIR/mythenquai.sqlite -cmd '.mode csv' -cmd ".import $DIR/messwerte_mythenquai.csv data" -bail .quit
sqlite3 $DIR/tiefenbrunnen.sqlite -cmd '.mode csv' -cmd ".import $DIR/messwerte_tiefenbrunnen.csv data" -bail .quit
sqlite3 $DIR/mythenquai.sqlite -cmd 'create unique index ix_timestamp on data(timestamp_utc);' -bail .quit
sqlite3 $DIR/tiefenbrunnen.sqlite -cmd 'create unique index ix_timestamp on data(timestamp_utc);' -bail .quit

# 3. run the scraper, update the db
echo "Fetch todays data from FTP server..."
python $DIR/fetch_from_ftp.py

# 4. Show new data
echo "New Mythenquai data:"
tail $DIR/messwerte_mythenquai_today.csv
echo ""
echo "New Tiefenbrunnen data:"
tail $DIR/messwerte_tiefenbrunnen_today.csv

# 5. Merge events
echo "Merge events..."
python $DIR/merge_data.py -d $DIR/mythenquai.sqlite -f $DIR/messwerte_mythenquai_today.csv
python $DIR/merge_data.py -d $DIR/tiefenbrunnen.sqlite -f $DIR/messwerte_tiefenbrunnen_today.csv
rm $DIR/messwerte_mythenquai_today.csv
rm $DIR/messwerte_tiefenbrunnen_today.csv

# 6. Export the database as csv
echo "Export database to CSV..."
sqlite3 -header -csv $DIR/mythenquai.sqlite "select * from data order by timestamp_utc asc;" > $DIR/messwerte_mythenquai_seit2007-heute.csv
sqlite3 -header -csv $DIR/tiefenbrunnen.sqlite "select * from data order by timestamp_utc asc;" > $DIR/messwerte_tiefenbrunnen_seit2007-heute.csv
sed -i 's/""//g' $DIR/messwerte_mythenquai_seit2007-heute.csv
sed -i 's/""//g' $DIR/messwerte_tiefenbrunnen_seit2007-heute.csv
