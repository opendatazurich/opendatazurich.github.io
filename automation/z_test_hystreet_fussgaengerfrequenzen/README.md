Hystreet: Fussgängerfrequenzen an der Bahnhofstrasse
====================================================

||Beschreibung|
|---|---|
|**Status:**|[![Update hystreet_fussgaengerfrequenzen data](https://github.com/opendatazurich/opendatazurich.github.io/actions/workflows/update_hystreet_fussgaengerfrequenzen.yml/badge.svg)](https://github.com/opendatazurich/opendatazurich.github.io/actions/workflows/update_hystreet_fussgaengerfrequenzen.yml)|
|**Workflow:**|[`update_hystreet_fussgaengerfrequenzen.yml`](https://github.com/opendatazurich/opendatazurich.github.io/blob/master/.github/workflows/update_hystreet_fussgaengerfrequenzen.yml)|
|**Quelle:**| [Hystreet API](https://static.hystreet.com/#/)
|**Datensatz INT:**|[Passantenfrequenzen an der Bahnhofstrasse - Stundenwerte (data.integ.stadt-zuerich.ch)](https://data.integ.stadt-zuerich.ch/dataset/hystreet_fussgaengerfrequenzen)|
|**Datensatz PROD:**|[Passantenfrequenzen an der Bahnhofstrasse - Stundenwerte (data.stadt-zuerich.ch)](https://data.stadt-zuerich.ch/dataset/hystreet_fussgaengerfrequenzen)|

Die Daten werden von Hystreet via ein [API](https://static.hystreet.com/#/) zur Verfügung gestellt.

Das Skript [`fetch_from_api.py`](https://github.com/opendatazurich/opendatazurich.github.io/blob/master/automation/hystreet_fussgaengerfrequenzen/fetch_from_api.py) lädt die aktuellen Daten, anschliessend wird das resultierende CSV und GeoJSON zu CKAN hochgeladen. 

```mermaid
flowchart TB
    Zeit>"Zeitsteuerung ⌛️"]
    Manuell>"Manuell"]
    Start(GitHub Action starten)
    Zeit --> Start
    Manuell --> Start
    Start --> API(Daten von API herunterladen)
    API -.- fetch(fetch_from_api.py):::script
    API --> DataUpdate(CSV und GeoJSON in CKAN aktualiseren)
    DataUpdate -.- upload(upload_resource_to_ckan.py):::script
    DataUpdate --> MetadataUpdate(Metadaten in CKAN aktualisieren)
    MetadataUpdate -.- updatemetadata(update_metadata.py):::script
    MetadataUpdate --> ENDE
    style ENDE stroke-width:5px
    classDef script fill:#EDF2AE,stroke:#666,stroke-width:4px
```
