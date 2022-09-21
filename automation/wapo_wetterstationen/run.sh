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
year=$(date +'%Y')
wget https://data.stadt-zuerich.ch/dataset/sid_wapo_wetterstationen/download/messwerte_mythenquai_${year}.csv -O $DIR/messwerte_mythenquai.csv
wget https://data.stadt-zuerich.ch/dataset/sid_wapo_wetterstationen/download/messwerte_tiefenbrunnen_${year}.csv -O $DIR/messwerte_tiefenbrunnen.csv

# 2. populate the database with the current CSV
echo "Populating databases from CSVs..."
rm -rf $DIR/mythenquai.sqlite
rm -rf $DIR/tiefenbrunnen.sqlite
sqlite3 $DIR/mythenquai.sqlite -cmd '.mode csv' -cmd ".import $DIR/messwerte_mythenquai.csv data" .quit
sqlite3 $DIR/tiefenbrunnen.sqlite -cmd '.mode csv' -cmd ".import $DIR/messwerte_tiefenbrunnen.csv data" .quit
sqlite3 $DIR/mythenquai.sqlite -cmd 'create unique index ix_timestamp on data(timestamp_utc);' .quit
sqlite3 $DIR/tiefenbrunnen.sqlite -cmd 'create unique index ix_timestamp on data(timestamp_utc);' .quit

# 3. run the scraper, update the db
echo "Fetch todays data from website..."
python $DIR/scrape_from_website.py

# 3. Merge events
echo "Merge events..."
python $DIR/merge_data.py -d $DIR/mythenquai.sqlite -f $DIR/messwerte_mythenquai_today.csv
python $DIR/merge_data.py -d $DIR/tiefenbrunnen.sqlite -f $DIR/messwerte_tiefenbrunnen_today.csv
rm $DIR/messwerte_mythenquai_today.csv
rm $DIR/messwerte_tiefenbrunnen_today.csv

# 3. Export the database as csv
echo "Export database to CSV..."
sqlite3 -header -csv $DIR/mythenquai.sqlite "select * from data order by timestamp_utc asc;" > $DIR/messwerte_mythenquai_${year}.csv
sqlite3 -header -csv $DIR/tiefenbrunnen.sqlite "select * from data order by timestamp_utc asc;" > $DIR/messwerte_tiefenbrunnen_${year}.csv
sed -i 's/""//g' $DIR/messwerte_mythenquai_${year}.csv
sed -i 's/""//g' $DIR/messwerte_tiefenbrunnen_${year}.csv
