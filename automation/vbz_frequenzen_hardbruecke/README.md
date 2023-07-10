VBZ Passagierfrequenzen
=======================

||Beschreibung|
|---|---|
|**Status:**|[![Update vbz_frequenzen_hardbruecke data](https://github.com/opendatazurich/opendatazurich.github.io/actions/workflows/update_vbz_frequenzen_hardbruecke.yml/badge.svg)](https://github.com/opendatazurich/opendatazurich.github.io/actions/workflows/update_vbz_frequenzen_hardbruecke.yml)|
|**Workflow:**|[`update_vbz_frequenzen_hardbruecke.yml`](https://github.com/opendatazurich/opendatazurich.github.io/blob/master/.github/workflows/update_vbz_frequenzen_hardbruecke.yml)|
|**Quelle:**| VBZ API
|**Datensatz INT:**|[Fahrgastfrequenzen an der VBZ-Haltestelle Hardbrücke (data.integ.stadt-zuerich.ch)](https://data.integ.stadt-zuerich.ch/dataset/vbz_frequenzen_hardbruecke)|
|**Datensatz PROD:**|[Fahrgastfrequenzen an der VBZ-Haltestelle Hardbrücke (data.stadt-zuerich.ch)](https://data.stadt-zuerich.ch/dataset/vbz_frequenzen_hardbruecke)|

Die Daten werden von der VBZ via ein API zur Verfügung gestellt.

Das [Workflow-YAML]([https://github.com/opendatazurich/opendatazurich.github.io/blob/master/.github/workflows/update_vbz_frequenzen_hardbruecke.yml) beschreibt den Ablauf im Detail.
Die Skripts werden alle in [`update_data.sh`](https://github.com/opendatazurich/opendatazurich.github.io/blob/master/automation/vbz_frequenzen_hardbruecke/update_data.sh) und schlussendlich das erstellte CSV in CKAN hochgeladen.

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

