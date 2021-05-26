#!/bin/bash

# Script to run a single scraper

set -e
set -o pipefail

function cleanup {
  exit $?
}
trap "cleanup" EXIT

DIR="$(cd "$(dirname "$0")" && pwd)"

# 1. run the scraper, download the ICS files
echo "Run the scraper..."
python $DIR/scraper.py

# 2. Convert ics to  csv
echo "Convert ICS to CSV..."

echo "start_date,end_date,summary,location,description,uid,created_date" > $DIR/schulferien.csv
for f in $DIR/*.ics;
do
    python $DIR/../ics_to_csv.py -f ${f} --skip-header >> $DIR/schulferien.csv
done
