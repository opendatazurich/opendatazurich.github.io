Downloadstatistiken
====================

|                           | Beschreibung                         |
| ------------------------- | ------------------------------------ |
| **Status:**         | [![Update Download Statistics](https://github.com/opendatazurich/opendatazurich.github.io/actions/workflows/update_download_statistics.yml/badge.svg)](https://github.com/opendatazurich/opendatazurich.github.io/actions/workflows/update_download_statistics.yml) |
| **Workflow:**       | [`update_download_statistics.yml`](https://github.com/opendatazurich/opendatazurich.github.io/blob/master/.github/workflows/update_download_statistics.yml)  |
| **Quelle:**         | Auswertung von Datopian. Zur Verfügung gestellt über Google Cloud Storage      |
| **Datensatz INT:**  |                        |
| **Datensatz PROD:** | [Downloads from OGD Katalog (pirvater Datensatz)](https://ckan-prod.zurich.datopian.com/dataset/prd_ssz_ogd_katalog_downloads) |

Datopian wertet die Logdateien von CKAN aus um festzustellen, welche Ressourcen heruntergeladen wurden. In Zukunft ist geplant, dass diese Daten als Open Data veröffentlicht werden. Dies ist ein vorläufiger Workflow, der sicherstellen soll, dass in der Zwischenzeit keine Daten verloren gehen.