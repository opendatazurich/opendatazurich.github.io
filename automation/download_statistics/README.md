Downloadstatistiken
====================

|                           | Beschreibung                         |
| ------------------------- | ------------------------------------ |
| **Status:**         | [![Update Download Statistics](https://github.com/opendatazurich/opendatazurich.github.io/actions/workflows/update_download_statistics.yml/badge.svg)](https://github.com/opendatazurich/opendatazurich.github.io/actions/workflows/update_download_statistics.yml) |
| **Workflow:**       | [`update_download_statistics.yml`](https://github.com/opendatazurich/opendatazurich.github.io/blob/master/.github/workflows/update_download_statistics.yml)  |
| **Quelle:**         | Auswertung von Datopian. Zur Verfügung gestellt über Google Cloud Storage      |
| **Datensatz INT:**  |                        |
| **Datensatz PROD:** | [Downloads from OGD Katalog (privater Datensatz)](https://ckan-prod.zurich.datopian.com/dataset/prd_ssz_ogd_katalog_downloads) |

Datopian wertet die Logdateien von CKAN aus um festzustellen, welche Ressourcen heruntergeladen wurden. Datopian stellt über einen Google Cloud Bucket täglich eine neue Datei mit den Downloaddaten vom vorherigen Tag zur Verfügung. Alternativ kann man auch alle Daten der vergangenen Tage verwenden. Dies wird in Github Actions über die Option `USE_ROLLING_1_MONTH` gesteuert.

Im Datensatz enthalten sind unter anderem die Spalten ``dataset_name``, ``resource_id`` und ``resource_name``. Diese sind aber nicht immer befüllt. Um die Datenqualität zu verbessern werden diese Spalten, wenn möglich mit Metadaten von CKAN aufgefüllt. Ist zum Beispiel nur die `resource_id` vorhanden, kann man mit Hilfe der CKAN-Metadaten `dataset_name` und `resource_name` herausfinden. Die benötigten Funktionen dafür befinden sich im Skript [`add_metadata.py`](add_metadata.py). Mit diesem Skript wurden auch die vorhandenen historischen Daten einmalig erweitert. Das passierte am 07.07.2026 zuletzt. Dabei muss man beachten, dass man von den CKAN Metadaten immer nur den aktuellen Stand hat. Wurde zum Beispiel im Jahr davor eine Ressource heruntergeladen, deren Ressourcen ID nicht mehr existiert, können dazu später auch keine Metadaten mehr gefunden werden.

Es werden nicht alle Rohdaten übernommen, sondern es wird gefiltert nach diesem Muster: `dataset_name vohanden UND (resource_name vorhanden ODER resource_id vorhanden)`. Diejenigen Datensätze, die entfernt wurden, werden zeitlich begrenzt als artifact gespeichert.

> **In Zukunft ist geplant, dass diese Daten als Open Data veröffentlicht werden. Dies ist ein vorläufiger Workflow, der sicherstellen soll, dass in der Zwischenzeit keine Daten verloren gehen.**

**To do:**
- [ ] Metadaten beschreiben
- [ ] Datensatz veröffentlichen