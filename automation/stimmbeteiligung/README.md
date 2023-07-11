Stimmbeteiligung vor Urnengängen
=================================

||Beschreibung|
|---|---|
|**Status:**|[![Update stimmbeteiligung data](https://github.com/opendatazurich/opendatazurich.github.io/actions/workflows/update_stimmbeteiligung.yml/badge.svg)](https://github.com/opendatazurich/opendatazurich.github.io/actions/workflows/update_stimmbeteiligung.yml)|
|**Workflow:**|[`update_stimmbeteiligung.yml`](https://github.com/opendatazurich/opendatazurich.github.io/blob/master/.github/workflows/update_stimmbeteiligung.yml)|
|**Quelle:**| [Webseite der Stadtkanzlei](https://www.stadt-zuerich.ch/portal/de/index/politik_u_recht/abstimmungen_u_wahlen/aktuell/stand-stimmbeteiligung.html)
|**Datensatz INT:**|[Stimmbeteiligung in Prozent vor Urnengängen (data.integ.stadt-zuerich.ch)](https://data.integ.stadt-zuerich.ch/dataset/politik_stimmbeteiligung-vor-urnengangen)|
|**Datensatz PROD:**|[Stimmbeteiligung in Prozent vor Urnengängen (data.stadt-zuerich.ch)](https://data.stadt-zuerich.ch/dataset/politik_stimmbeteiligung-vor-urnengangen)|

Die Daten werden von der [Webseite der Stadtkanzlei](https://www.stadt-zuerich.ch/portal/de/index/politik_u_recht/abstimmungen_u_wahlen/aktuell/stand-stimmbeteiligung.html) gescrapt.

Die Skripte werden alle in [`run_scraper.sh`](https://github.com/opendatazurich/opendatazurich.github.io/blob/master/automation/stimmbeteiligung/run_scraper.sh) und schlussendlich das erstellte CSV im Repository und in CKAN hochgeladen.

```mermaid
flowchart TB
    Zeit>"Zeitsteuerung ⌛️"]
    Manuell>"Manuell"]
    Start(GitHub Action starten, run_scraper.sh ausführen)
    Zeit --> Start
    Manuell --> Start
    Start --> DatenVonCKAN(Bestehende Daten von CKAN herunterladen)
    DatenVonCKAN --> DatenInDB(Bestehende Daten in SQLite Datenbank laden)
    DatenInDB --> populate(populate_database.py):::script
    DatenInDB --> Scraper(Neue Daten von Webseite scrapen)
    Scraper -.- scrape(scraper.py):::script
    Scraper --> Merge(Neue Daten in SQLite Datenbank mergen)
    Merge -.- merge(merge_events.py):::script
    Merge --> Export(SQLite Datenbank als CSV exportieren)
    Export --> Commit(Daten in Repository committen)
    Commit --> DataUpdate(CSV in CKAN aktualiseren)
    DataUpdate -.- upload(upload_resource_to_ckan.py):::script
    DataUpdate --> MetadataUpdate(Metadaten in CKAN aktualisieren)
    MetadataUpdate -.- updatemetadata(update_metadata.py):::script
    MetadataUpdate --> ENDE
    style ENDE stroke-width:5px
    classDef script fill:#EDF2AE,stroke:#666,stroke-width:4px
```
