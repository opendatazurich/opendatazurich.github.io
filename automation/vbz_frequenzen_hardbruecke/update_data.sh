#!/bin/bash

# Script to update the VBZ data

set -e
set -o pipefail

function cleanup {
  exit $?
}
trap "cleanup" EXIT

DIR="$(cd "$(dirname "$0")" && pwd)"
echo DIR

# 1. Get current year file from CKAN
year=$(date +'%Y')
echo "Get current year file from CKAN..."
curl -L https://data.stadt-zuerich.ch/dataset/vbz_frequenzen_hardbruecke/download/frequenzen_hardbruecke_${year}.csv --output $DIR/frequenzen_hardbruecke.csv # integration
cat $DIR/frequenzen_hardbruecke.csv | wc -l
head $DIR/frequenzen_hardbruecke.csv
echo "..."
tail $DIR/frequenzen_hardbruecke.csv

# 2. populate the database with the current CSV
echo "Populating databases from CSV..."
rm -rf $DIR/frequenzen_hardbruecke.sqlite
sqlite3 $DIR/frequenzen_hardbruecke.sqlite -cmd '.mode csv' -cmd ".import $DIR/frequenzen_hardbruecke.csv data" .quit
sqlite3 $DIR/frequenzen_hardbruecke.sqlite -cmd 'create unique index ix_timestamp_name on data(Timestamp, Name);' .quit

# 3. fetch data from api, update the db
echo "Fetch from API..."
python $DIR/fetch_from_api.py > $DIR/frequenzen_hardbruecke_today.csv
cat $DIR/frequenzen_hardbruecke_today.csv  | wc -l
head $DIR/frequenzen_hardbruecke_today.csv
echo "..."
tail $DIR/frequenzen_hardbruecke_today.csv

# 4. Merge events
echo "Merge data..."
python $DIR/merge_data.py -d $DIR/frequenzen_hardbruecke.sqlite -f $DIR/frequenzen_hardbruecke_today.csv
rm $DIR/frequenzen_hardbruecke_today.csv

# 5. Export the database as csv
echo "Export database to CSV..."
sqlite3 -header -csv $DIR/frequenzen_hardbruecke.sqlite "select * from data order by Timestamp asc, Name asc;" > $DIR/frequenzen_hardbruecke_${year}.csv
sed -i 's/""//g' $DIR/frequenzen_hardbruecke_${year}.csv
cat $DIR/frequenzen_hardbruecke_${year}.csv | wc -l

# 6. Export the database as parquet
echo "Export database to parquet..."
python $DIR/export_sqlite_to_parquet.py -d $DIR/frequenzen_hardbruecke.sqlite -f $DIR/frequenzen_hardbruecke_${year}.parquet



