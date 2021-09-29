#!/bin/bash

# Prepare the data

set -e
set -o pipefail

# make sure Python uses UTF-8 when printing to stdout
export PYTHONIOENCODING=utf-8

function cleanup {
  exit $?
}
trap "cleanup" EXIT

DIR="$(cd "$(dirname "$0")" && pwd)"

# 1. Generate the CSV and download all attachments
echo "Generate the CSV"
python $DIR/download_data_from_museumplus.py -s "Patolu, MAP" > $DIR/mrz_patolu.csv
