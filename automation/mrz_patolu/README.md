MRZ Patolu
==============

||Beschreibung|
|---|---|
|**Status:**| [![Update mrz_patolu data](https://github.com/opendatazurich/opendatazurich.github.io/actions/workflows/update_mrz_patolu.yml/badge.svg)](https://github.com/opendatazurich/opendatazurich.github.io/actions/workflows/update_mrz_patolu.yml)|
|**Workflow:**| [`update_mrz_patolu.yml`](https://github.com/opendatazurich/opendatazurich.github.io/blob/master/.github/workflows/update_mrz_patolu.yml)|
|**Quelle:**| MuseumPlus |
|**Datensatz INT:**|[Patolu – Indische Textilien aus der Sammlung des Museums Rietberg (data.integ.stadt-zuerich.ch)](https://data.integ.stadt-zuerich.ch/dataset/mrz_patolu)|
|**Datensatz PROD:**|[Patolu – Indische Textilien aus der Sammlung des Museums Rietberg (data.stadt-zuerich.ch)](https://data.stadt-zuerich.ch/dataset/mrz_patolu))|

Die Daten werden durch das Museum Rietberg via MuseumPlus zur Verfügung gestellt. Die zugehörigen Bild-Dateien wurden einmalig manuell hochgeladen (kein Update vorgesehen).

Die Skripts werden alle in [`prepare_data.sh`](https://github.com/opendatazurich/opendatazurich.github.io/blob/master/automation/mrz_patolu/prepare_data.sh) ausgeführt und schlussendlich das erstellte CSV in CKAN hochgeladen.

```mermaid
flowchart TB
    Zeit>"Zeitsteuerung ⌛️"]
    Manuell>"Manuell"]
    Start(GitHub Action starten, prepare_data.sh starten)
    Zeit --> Start
    Manuell --> Start
    Start --> API(Daten von API herunterladen)
    API -.- download(download_data_from_museumplus.py):::script
    API --> Convert(Daten in CSV umwandeln)
    Convert -.- download
    Convert --> DataUpdate(CSV in CKAN aktualiseren)
    DataUpdate -.- upload(upload_resource_to_ckan.py):::script
    DataUpdate --> MetadataUpdate(Metadaten in CKAN aktualisieren)
    MetadataUpdate -.- updatemetadata(update_metadata.py):::script
    MetadataUpdate --> ENDE
    style ENDE stroke-width:5px
    classDef script fill:#EDF2AE,stroke:#666,stroke-width:4px
```

