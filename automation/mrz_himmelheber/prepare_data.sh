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
echo "Export the CSVs"
python $DIR/export_data_from_museumplus.py -s "Himmelheber-Fotoarchiv (Furbo)" -e "71027" -p $DIR/mrz_himmelheber_fotos.csv
python $DIR/export_data_from_museumplus.py -s "Himmelheber-Stücke in der Sammlung" -e "71027" -p $DIR/mrz_himmelheber_objekte.csv
