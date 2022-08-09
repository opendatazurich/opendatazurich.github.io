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
echo "Populating database from CSV schulferien.csv..."
python $DIR/populate_database.py -n mythenquai.sqlite -f $DIR/messwerte_mythenquai.csv
python $DIR/populate_database.py -n tiefenbrunnen.sqlite -f $DIR/messwerte_tiefenbrunnen.csv

# 3. run the scraper, update the db
echo "Run the scraper..."
python $DIR/fetch_from_api.py

# 3. Merge events
echo "Merge events..."
python $DIR/merge_data.py

# 3. Export the database as csv
echo "Export database to CSV..."
sqlite3 -header -csv $DIR/mythenquai.sqlite "select * from data order by timestamp_utc asc;" > messwerte_mythenquai_${year}.csv
sqlite3 -header -csv $DIR/tiefenbrunnen.sqlite "select * from data order by timestamp_utc asc;" > messwerte_tiefenbrunnen_${year}.csv
sed -i 's/""//g' messwerte_mythenquai_${year}.csv
sed -i 's/""//g' messwerte_tiefenbrunnen_${year}.csv
