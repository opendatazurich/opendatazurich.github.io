Dateninventar des OGD-Katalogs
==============================

||Beschreibung|
|---|---|
|**Status:**|[![Update Dateninventar des OGD-Katalogs](https://github.com/opendatazurich/opendatazurich.github.io/actions/workflows/update_ckan_metadata.yml/badge.svg)](https://github.com/opendatazurich/opendatazurich.github.io/actions/workflows/update_ckan_metadata.yml)|
|**Workflow:**|[`update_ckan_metadata.yml`](https://github.com/opendatazurich/opendatazurich.github.io/actions/workflows/update_ckan_metadata.yml)|
|**Quelle:**| [OGD Katalog](https://data.stadt-zuerich.ch/)
|**Datensatz INT:**|[Dateninventar des OGD-Katalogs der Stadt Zürich (data.integ.stadt-zuerich.ch)](https://data.integ.stadt-zuerich.ch/dataset/int_dwh_prd_ssz_ogd_katalog_inventar)|
|**Datensatz PROD:**|[Dateninventar des OGD-Katalogs der Stadt Zürich (data.stadt-zuerich.ch)](https://data.stadt-zuerich.ch/dataset/prd_ssz_ogd_katalog_inventar)|

Die wichtigsten Metadaten aller veröffentlichten Datensätze des [OGD-Katalog](https://data.stadt-zuerich.ch/) mittels der [CKAN API](https://docs.ckan.org/en/2.9/api/) bezogen und als Dateninventar wiederum zur Verfügung gestellt.

Das Skript [`fetch_from_api.py`](https://github.com/opendatazurich/opendatazurich.github.io/blob/master/automation/ogd_metadata/fetch_from_api.py) lädt die aktuellen Daten, anschliessend wird das resultierende CSV zu CKAN hochgeladen. 

```mermaid
flowchart TB
    Zeit>"Zeitsteuerung ⌛️"]
    Manuell>"Manuell"]
    Start(GitHub Action starten)
    Zeit --> Start
    Manuell --> Start
    Start --> API(Daten von API herunterladen)
    API -.- fetch(fetch_from_api.py):::script
    API --> DataUpdate(CSV in CKAN aktualiseren)
    DataUpdate -.- upload(upload_resource_to_ckan.py):::script
    DataUpdate --> MetadataUpdate(Metadaten in CKAN aktualisieren)
    MetadataUpdate -.- updatemetadata(update_metadata.py):::script
    MetadataUpdate --> ENDE
    style ENDE stroke-width:5px
    classDef script fill:#EDF2AE,stroke:#666,stroke-width:4px
```