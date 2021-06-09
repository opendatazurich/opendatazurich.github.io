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

[^metaxml]: `meta.xml` sind die CKAN-Metadaten in XML Form, so dass der Harvester diese interpretieren kann.
