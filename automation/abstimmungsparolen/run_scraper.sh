#!/bin/bash

# Script to run a single scraper

set -e
set -o pipefail

function cleanup {
  exit $?
}
trap "cleanup" EXIT

DIR="$(cd "$(dirname "$0")" && pwd)"


# 1. populate the database with the current CSV
echo "Populating database from CSV abstimmungsparolen.csv..."
rm -rf $DIR/data.sqlite
sqlite3 $DIR/data.sqlite -cmd ".mode csv" -cmd ".import $DIR/abstimmungsparolen.csv data" .quit

# 2. run the scraper, update the db
echo "Run the scraper..."
python $DIR/scraper.py

# 3. Export the database as csv
echo "Export database to CSV..."
sqlite3 -header -csv $DIR/data.sqlite "select * from data order by datum asc,titel,partei asc;" > $DIR/abstimmungsparolen.csv
sed -i 's/""//g' $DIR/abstimmungsparolen.csv
