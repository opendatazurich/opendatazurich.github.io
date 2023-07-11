Stadtarchiv: Historische Geschäftsberichte
===========================================

||Beschreibung|
|---|---|
|**Status:**|[![Update sar_geschaeftsberichte data](https://github.com/opendatazurich/opendatazurich.github.io/actions/workflows/update_sar_geschaeftsberichte.yml/badge.svg)](https://github.com/opendatazurich/opendatazurich.github.io/actions/workflows/update_sar_geschaeftsberichte.yml)|
|**Workflow:**|[`update_sar_geschaeftsberichte.yml`](https://github.com/opendatazurich/opendatazurich.github.io/blob/master/.github/workflows/update_sar_geschaeftsberichte.yml)|
|**Quelle:**| [Elektronischer Archivkatalog (Query)](https://amsquery.stadt-zuerich.ch/suchinfo.aspx) des Stadtarchivs (via SRU-Schnittstelle)
|**Datensatz INT:**|[Geschäftsberichte des Stadtrats, ab 1859 (data.integ.stadt-zuerich.ch)](https://data.integ.stadt-zuerich.ch/dataset/sar_geschaeftsberichte)|
|**Datensatz PROD:**|[Geschäftsberichte des Stadtrats, ab 1859 (data.stadt-zuerich.ch)](https://data.stadt-zuerich.ch/dataset/sar_geschaeftsberichte)|

Die Daten durch das Stadtarchiv via SRU-Schnittstelle ihres Archivkatalogs zur Verfügung gestellt.

Das Skript [`generate_csv.py`](https://github.com/opendatazurich/opendatazurich.github.io/blob/master/automation/sar_geschaeftsberichte/generate_csv.py) lädt die aktuellen Daten, anschliessend wird das resultierende CSV zu CKAN hochgeladen. 

```mermaid
flowchart TB
    Zeit>"Zeitsteuerung ⌛️"]
    Manuell>"Manuell"]
    Start(GitHub Action starten)
    Zeit --> Start
    Manuell --> Start
    Start --> API(Daten von API herunterladen)
    API -.- generate(generate_csv.py):::script
    API --> Convert(Daten in CSV umwandeln)
    Convert -.- generate
    Convert --> DataUpdate(CSV in CKAN aktualiseren)
    DataUpdate -.- upload(upload_resource_to_ckan.py):::script
    DataUpdate --> MetadataUpdate(Metadaten in CKAN aktualisieren)
    MetadataUpdate -.- updatemetadata(update_metadata.py):::script
    MetadataUpdate --> ENDE
    style ENDE stroke-width:5px
    classDef script fill:#EDF2AE,stroke:#666,stroke-width:4px
```
