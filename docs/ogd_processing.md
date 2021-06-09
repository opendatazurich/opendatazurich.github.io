Datenaufbereitung mit Python
============================

Die Datenaufbereitung mit Python für Datensätze, die auf internen Daten basieren, gibt es ein separates Git Repository [opendatazurich/ogd-data-processing](https://github.com/opendatazurich/ogd-data-processing).

Alle diese Datenaufbereitungen sind gleich aufgebaut und werden über Cron gesteuert auf dem internen Linux-Server szhm58504 mit dem Benutzer `opendatazurich`.

Die Idee ist es, die Quelldaten so aufzubereiten, dass diese von einem Harvester auf CKAN importiert werden können.

## Struktur

Jeder Datensatz ist jeweils ein Verzeichnis mit mind. einem `README.md` und einem Skript `update_dataset.sh`
Im README soll erklärt werden, wie der Datensatz aktualisiert werden kann, insbesondere auch die Metadaten.

## Skripte für die Datenaufbereitung

Im ogd-data-processing hat es eine Reihe von Skripten, die bei der Datenaufbereitung helfen:

| Skript                         | Beschreibung                                                   |
|--------------------------------|----------------------------------------------------------------|
| [csv_delim.py][]               | Änderung das Trennzeichen zu `,` und UTF-8 Konvertierung       |
| [update_metadata.py][]         | Metadaten auf CKAN aktualisieren                               |
| [read_meta_xml.py][]           | Wandeln ein `meta.xml`[^metaxml] zu JSON oder Python dict um   |
| [upload_resource_to_ckan.py][] | Um Dateien als Ressourcen auf CKAN zu stellen                  |
| [xls_to_meta_xml.py][]         | Wandelt ein Metadaten-Excel zu einem `meta.xml`[^metaxml] um   |

[csv_delim.py]: https://github.com/opendatazurich/ogd-data-processing/blob/main/csv_delim.py
[update_metadata.py]: https://github.com/opendatazurich/ogd-data-processing/blob/main/update_metadata.py
[read_meta_xml.py]: https://github.com/opendatazurich/ogd-data-processing/blob/main/read_meta_xml.py
[upload_resource_to_ckan.py]: https://github.com/opendatazurich/ogd-data-processing/blob/main/upload_resource_to_ckan.py
[xls_to_meta_xml.py]: https://github.com/opendatazurich/ogd-data-processing/blob/main/xls_to_meta_xml.py

## Datensatz aufbereiten

Typischer Aufbau einer `update_dataset.sh` Skripts:

```bash
#!/bin/bash

set -e
set -o pipefail

function cleanup {
  exit $?
}
trap "cleanup" EXIT

DIR="$(cd "$(dirname "$0")" && pwd)"

# Load python environment
if ! command -v scl &> /dev/null
then
    scl enable rh-python36 bash
fi
source $DIR/../env/bin/activate


# Config
DATA_DIR=/mnt/OGD/Daten/Quelldaten/HBD/bauarchiv_zuerich_um_1910
DROPZONE_DIR=/mnt/OGD_Dropzone/DWH
DATASET=baz_zuerich_um_1910

# Load .env
source $DIR/../.env

# generate meta.xml
python $DIR/../xls_to_meta_xml.py -f $DATA_DIR/OGD-Metadaten_BAZ_Zürich1910.xlsx -o $DIR/meta.xml

# copy everything to DROPZONE
cp $DIR/meta.xml $DROPZONE_DIR/$DATASET
cp $DATA_DIR/link.xml $DROPZONE_DIR/$DATASET
python $DIR/../csv_delim.py -f $DATA_DIR/LIST_BAZ_GLAMhack2021_Zürich1910.csv -d ";" -e cp1252 > $DROPZONE_DIR/$DATASET/baz_zuerich_um_1910.csv 
```

In diesem Beispiel wird eine Quelldatei (CSV) für OGD aufbereitet (korrekte Codierung und Trennzeichen) und in der DWH-Dropzone zur Verfügung gestellt.

In `.env` sind alle Umgebungsvariablen definiert, diese umfassen folgende Werte: 

```
CKAN_BASE_URL=https://data.stadt-zuerich.ch
CKAN_API_KEY=<api-key>
GITHUB_TOKEN=<token>
```

[^metaxml]: `meta.xml` sind die CKAN-Metadaten in XML Form, so dass der Harvester diese interpretieren kann.
