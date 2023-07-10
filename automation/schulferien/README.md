Schulferien
=============

||Beschreibung|
|---|---|
|**Status:**|[![Update Schulferien data](https://github.com/opendatazurich/opendatazurich.github.io/actions/workflows/update_schulferien.yml/badge.svg)](https://github.com/opendatazurich/opendatazurich.github.io/actions/workflows/update_schulferien.yml)|
|**Workflow:**|[`update_schulferien.yml`](https://github.com/opendatazurich/opendatazurich.github.io/actions/workflows/update_schulferien.yml)|
|**Quelle:**| [ICS-Dateien von der Webseite des Schulamts](https://www.stadt-zuerich.ch/ssd/de/index/volksschule/schulferien.html)
|**Datensatz INT:**|[Ferien und schulfreie Tage der Volksschule der Stadt Zürich, Schuljahre 2020/2021 bis 2024/2025 (data.integ.stadt-zuerich.ch)](https://data.integ.stadt-zuerich.ch/dataset/ssd_schulferien)|
|**Datensatz PROD:**|[Ferien und schulfreie Tage der Volksschule der Stadt Zürich, Schuljahre 2020/2021 bis 2024/2025 (data.stadt-zuerich.ch)](https://data.stadt-zuerich.ch/dataset/ssd_schulferien)|

Die Daten werden vom Schulamt [via Webseite als ICS](https://www.stadt-zuerich.ch/ssd/de/index/volksschule/schulferien.html) zur Verfügung gestellt.

Die Skripte werden alle in [`run_scraper.sh`](https://github.com/opendatazurich/opendatazurich.github.io/blob/master/automation/schulferien/run_scraper.sh) und schlussendlich das erstellte CSV im Repository und in CKAN hochgeladen.

```mermaid
flowchart TB
    Zeit>"Zeitsteuerung ⌛️"]
    Manuell>"Manuell"]
    Start(GitHub Action starten, update_data.sh ausführen)
    Zeit --> Start
    Manuell --> Start
    Start --> DatenVonCKAN(Bestehende Daten von CKAN herunterladen)
    DatenVonCKAN --> DatenInDB(Bestehende Daten in SQLite Datenbank laden)
    DatenInDB --> API(Neue Daten von API herunterladen)
    API -.- fetch(fetch_from_api.py):::script
    API --> Merge(Neue Daten in SQLite Datenbank mergen)
    Merge -.- merge(merge_data.py):::script
    Merge --> Export(SQLite Datenbank als CSV exportieren)
    Export --> DataUpdate(CSV in CKAN aktualiseren)
    DataUpdate -.- upload(upload_resource_to_ckan.py):::script
    DataUpdate --> MetadataUpdate(Metadaten in CKAN aktualisieren)
    MetadataUpdate -.- updatemetadata(update_metadata.py):::script
    MetadataUpdate --> ENDE
    style ENDE stroke-width:5px
    classDef script fill:#EDF2AE,stroke:#666,stroke-width:4px
```
