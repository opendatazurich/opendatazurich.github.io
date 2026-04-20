Update Badi Aktuell (Crowd Monitor)
====================

|                           | Beschreibung                                                                                                                                                                                                                                                           |
| ------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Status:**         | [![Update Badi Aktuell (Crowd Monitor)](https://github.com/opendatazurich/opendatazurich.github.io/actions/workflows/update_badi_aktuell.yml/badge.svg)](https://github.com/opendatazurich/opendatazurich.github.io/actions/workflows/update_badi_aktuell.yml) |
| **Workflow:**       | [`update_badi_aktuell.yml`](https://github.com/opendatazurich/opendatazurich.github.io/blob/master/.github/workflows/update_badi_aktuell.yml)                                                                                                            |
| **Quelle:**         | [ASE Diamond API](https://zuerich.pas.ch/)                                                                                                                                                               |
| **Datensatz INT:**  | [Aktuelle Anzahl Badegäste (data.integ.stadt-zuerich.ch)](https://data.integ.stadt-zuerich.ch/dataset/ssd_spo_badi_aktuell)                                                                                                              |
| **Datensatz PROD:** | [Aktuelle Anzahl Badegäste (data.stadt-zuerich.ch)](https://data.stadt-zuerich.ch/dataset/ssd_spo_badi_aktuell)                                                                                                                          |

Dieser Workflow lädt Daten von der [Crowd Monitor API](https://premises.crowdmonitor.ch). Der Datensatz enthält die Anzahl der Gäste, die aktuell im jeweiligen Bad sind. Die Zahlen entsprechen denen, die auch bei [Badi aktuell](https://www.stadt-zuerich.ch/badi-aktuell) veröffentlicht werden.

Die API enthält auch einige Locations, die keine Bäder sind. Deswegen werden sie entfernt. Im Moment sind das: `locations_to_drop = ["Letzigrund", "Josel-Areal", "Messehalle 9"]`

Ausserdem gibt es einige Datensätze, wo die Maximale Kapazität = 0 ist. Diese werden ebenfalls entfernt.


```mermaid
flowchart TB
    Zeit>"Zeitsteuerung ⌛️"]
    Manuell>"Manuell"]
    Start(GitHub Action starten)
    Zeit --> Start
    Manuell --> Start
    Start --> LocationsHolen(Liste der Bäder holen)
    LocationsHolen --> BelegungHolen(Hole Belegungsdaten für jedes Bad)
    BelegungHolen --> SaveCSV(Als CSV abspeichern)
	LocationsHolen -.- FetchData(crowd-monitor.py):::script
	BelegungHolen -.- FetchData(crowd-monitor.py):::script
    SaveCSV -.- FetchData(crowd-monitor.py):::script
    SaveCSV --> DataUpdate(CSV in CKAN aktualisieren)
    DataUpdate -.- upload(upload_resource_to_ckan.py):::script
    DataUpdate --> MetadataUpdate(Metadaten in CKAN aktualisieren)
    MetadataUpdate -.- updatemetadata(update_metadata.py):::script
    MetadataUpdate --> ENDE
    style ENDE stroke-width:5px
    classDef script fill:#EDF2AE,stroke:#666,stroke-width:4px
```
