WAPO Wetterstationen
====================

||Beschreibung|
|---|---|
|**Workflow:**|[`update_wapo_wetterstationen.yml`](https://github.com/opendatazurich/opendatazurich.github.io/blob/master/.github/workflows/update_wapo_wetterstationen.yml)|
|**Quelle:**| FTP-Server
|**Datensatz INT:**|[Messwerte der Wetterstationen der Wasserschutzpolizei Zürich (data.stadt-zuerich.ch)](https://data.stadt-zuerich.ch/dataset/sid_wapo_wetterstationen)|
|**Datensatz PROD:**|[Messwerte der Wetterstationen der Wasserschutzpolizei Zürich (data.integ.stadt-zuerich.ch)](https://data.integ.stadt-zuerich.ch/dataset/sid_wapo_wetterstationen))|

Die Daten der beiden Wetterstationen Mythenquai und Tiefenbrunnen der Wasserschutzpolizei (WAPO) werden uns durch die Tecson AG via FTP-Server bereitgestellt.

Das [Workflow-YAML](https://github.com/opendatazurich/opendatazurich.github.io/blob/master/.github/workflows/update_wapo_wetterstationen.yml) beschreibt den Ablauf im Detail.
Die Skripts werden alle in `run.sh` und schlussendlich das erstellte CSV wieder in CKAN hochgeladen.

```mermaid
flowchart TB
    Zeit>"Zeitsteuerung ⌛️"]
    Manuell>"Manuell"]
    Start(GitHub Action starten, run.sh ausführen)
    Zeit --> Start
    Manuell --> Start
    Start --> DatenVonCKAN(Bestehende Daten von CKAN herunterladen)
    DatenVonCKAN --> DatenInDB(Bestehende Daten in SQLite Datenbank laden)
    DatenInDB --> FTP(Neue Daten von FTP herunterladen)
    FTP -.- fetchftp(fetch_from_ftp.py):::script
    FTP --> Merge(Neue Daten in SQLite Datenbank mergen)
    Merge -.- mergedata(merge_data.py):::script
    Merge --> Export(SQLite Datenbank als CSV exportieren)
    Export --> DataUpdate(CSV in CKAN aktualiseren)
    DataUpdate -.- upload(upload_resource_to_ckan.py):::script
    DataUpdate --> MetadataUpdate(Metadaten in CKAN aktualisieren)
    MetadataUpdate -.- updatemetadata(update_metadata.py):::script
    MetadataUpdate --> Ende["ENDE"]
    style Ende stroke-width:5px
    classDef script fill:#EDF2AE,stroke:#666,stroke-width:4px
```

