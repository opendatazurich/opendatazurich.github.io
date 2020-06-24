#!/bin/bash

# Script to fetch new data from api and update csv

set -e
set -o pipefail

function cleanup {
  exit $?
}
trap "cleanup" EXIT

DIR="$(cd "$(dirname "$0")" && pwd)"


# 1. populate the database with the current CSV
echo "Populating database from CSV badi_counter.csv..."
$DIR/update_database.py $DIR/badi_counter.csv

# 2. fetch new data, update the db
echo "Fetch new data..."
$DIR/fetch_from_api.py > $DIR/temp.csv
$DIR/update_database.py $DIR/temp.csv
rm $DIR/temp.csv

# 3. Export the database as csv
echo "Export database to CSV..."
sqlite3 -header -csv $DIR/data.sqlite "select * from data order by date asc;" > $DIR/badi_counter.csv
