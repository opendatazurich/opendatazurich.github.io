Abstimmungsresultate
==============================================

||Beschreibung|
|---|---|
|**Status:**|[![Update abstimmungsparolen data](https://github.com/opendatazurich/opendatazurich.github.io/blob/master/.github/workflows/update_abstimmungsergebnisse.yml/badge.svg)](https://github.com/opendatazurich/opendatazurich.github.io/blob/master/.github/workflows/update_abstimmungsergebnisse.yml)|
|**Workflow:**|[`update_abstimmungsparolen.yml`](https://github.com/opendatazurich/opendatazurich.github.io/blob/master/.github/workflows/update_abstimmungsergebnisse.yml)|
|**Quelle:**| Daten vor 2022: Abstimmungsdatenbank von Statistik Stadt Zürich / Daten ab 2022: API von opendata.swiss|
|**Datensatz INT:**|[Abstimmungsresultate der Stadt Zürich, seit 1933 (data.integ.stadt-zuerich.ch)](https://data.integ.stadt-zuerich.ch/dataset/politik_abstimmungen_seit1933)|
|**Datensatz PROD:**|[Abstimmungsresultate der Stadt Zürich, seit 1933 (data.stadt-zuerich.ch)](https://data.stadt-zuerich.ch/dataset/politik_abstimmungen_seit1933)|

Die historischen Daten (bis 2022) stammen aus der Abstimmungsdatenbank von Statistik Stadt Zürich. Die aktuellen Daten (ab 2022) werden über eine API von opendata.swiss bezogen:
- [eidgenössische Vorlagen](https://ckan.opendata.swiss/api/3/action/package_show?id=echtzeitdaten-am-abstimmungstag-zu-eidgenoessischen-abstimmungsvorlagen) 
- [kantonale Vorlagen](https://ckan.opendata.swiss/api/3/action/package_show?id=echtzeitdaten-am-abstimmungstag-zu-kantonalen-abstimmungsvorlagen)
- [kommunale Vorlagen](https://ckan.opendata.swiss/api/3/action/package_show?id=echtzeitdaten-am-abstimmungstag-des-kantons-zurich-kommunale-und-regionale-vorlagen)

Das Skript [fetch_all_data.py](https://github.com/opendatazurich/opendatazurich.github.io/blob/master/automation/abstimmungsergebnisse/fetch_all_data.py) erstellt eine csv-Datei, die dann auf CKAN geladen wird.


```mermaid
flowchart TB
    Zeit>"Zeitsteuerung ⌛️"]
    Manuell>"Manuell"]
    Start(GitHub Action starten)
    Zeit --> Start
    Manuell --> Start
    Start --> DatenHolen(Aktuelle Daten herunterladen)
    DatenHolen --> DatenMergen(Zusammenfügen mit historischen Daten)
	DatenMergen --> DatenExport(Als CSV exportieren)
	DatenHolen -.- FetchData(fetch_all_data.py):::script
	DatenMergen -.- FetchData(fetch_all_data.py):::script
	DatenExport -.- FetchData(fetch_all_data.py):::script
    DatenExport --> DataUpdate(CSV in CKAN aktualiseren)
    DataUpdate -.- upload(upload_resource_to_ckan.py):::script
    DataUpdate --> MetadataUpdate(Metadaten in CKAN aktualisieren)
    MetadataUpdate -.- updatemetadata(update_metadata.py):::script
    MetadataUpdate --> ENDE
    style ENDE stroke-width:5px
    classDef script fill:#EDF2AE,stroke:#666,stroke-width:4px
```
