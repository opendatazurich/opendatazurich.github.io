#!/bin/bash

# Prepare the data

set -e
set -o pipefail

function cleanup {
  exit $?
}
trap "cleanup" EXIT

DIR="$(cd "$(dirname "$0")" && pwd)"

# 1. Generate the CSV and download all attachments
echo "Generate the CSV and download all attachments"
python $DIR/download_data_from_museumplus.py -s "Patolu, MAP" -a $DIR/images > $DIR/mrz_patolu.csv

# 2. Generate a zip file
zip -r $DIR/mrz_patolu_images.zip $DIR/images
