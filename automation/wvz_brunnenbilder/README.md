Update WVZ Brunnenbilder
====================

|  | Beschreibung |
| - | - |
| **Status:**  | [![Update WVZ Brunnenbilder](https://github.com/opendatazurich/opendatazurich.github.io/actions/workflows/update_wvz_brunnenbilder.yml/badge.svg)](https://github.com/opendatazurich/opendatazurich.github.io/actions/workflows/update_wvz_brunnenbilder.yml) |
| **Workflow:**       | [`update_wvz_brunnenbilder.yml`](https://github.com/opendatazurich/opendatazurich.github.io/blob/master/.github/workflows/update_wvz_brunnenbilder.yml) |
| **Quelle:**         | [Geodatensatz mit den Brunnen der Stadt Zürich](https://data.stadt-zuerich.ch/dataset/geo_brunnen) und [Brunnenwebseite](https://www.stadt-zuerich.ch/de/umwelt-und-energie/wasser/trinkwasser/brunnen.html) |
| **Datensatz INT:**  | [Brunnenbilder (data.integ.stadt-zuerich.ch)](https://data.integ.stadt-zuerich.ch/dataset/dib_wvz_brunnenbilder) |
| **Datensatz PROD:** | [Brunnenbilder (data.stadt-zuerich.ch)](https://data.stadt-zuerich.ch/dataset/dib_wvz_brunnenbilder)  |

Dieser Datensatz ist eine Ergänzung zum [Geodatensatz mit den Brunnen der Stadt Zürich](https://data.stadt-zuerich.ch/dataset/geo_brunnen). Der Geodatensatz selbst enthält auch Links zu Bildern. Diese sind jedoch nur im Netz der Stadt Zürich zugänglich und nicht öffentlich, da einige davon urheberrechtlich geschützt sind. Dieser Workflow sammelt deswegen die URLs der öffentlich zugänglichen [Brunnenwebseite](https://www.stadt-zuerich.ch/de/umwelt-und-energie/wasser/trinkwasser/brunnen.html) und der zugehörigen Bilder per Webscraping. Über die Brunnennummer können diese Informationen mit dem Geodatensatz verknüpft werden.

**Optional** wäre es möglich die Bilder selbst herunterzuladen und als ZIP zu speichern über die Funktionen `download_images` und `zip_images`. Das ist im Moment aber nicht nötig, deswegen ist das auskommentiert.


```mermaid
flowchart TB
    Zeit>"Zeitsteuerung ⌛️"]
    Manuell>"Manuell"]
    Start(GitHub Action starten)
    Zeit --> Start
    Manuell --> Start
    Start --> GeodatenAbfrage(Geodaten von Brunnen abfragen)
    GeodatenAbfrage --> UrlsExtrahieren(Webscraping von Bild URLs)
    UrlsExtrahieren --> CsvOutput(Als CSV ablegen)
	GeodatenAbfrage -.- FetchData(brunnen_image_scraper.py):::script
	UrlsExtrahieren -.- FetchData(brunnen_image_scraper.py):::script
    CsvOutput -.- FetchData(brunnen_image_scraper.py):::script
    CsvOutput --> DataUpdate(CSVs in CKAN aktualisieren)
    DataUpdate -.- upload(upload_resource_to_ckan.py):::script
    DataUpdate --> MetadataUpdate(Metadaten in CKAN aktualisieren)
    MetadataUpdate -.- updatemetadata(update_metadata.py):::script
    MetadataUpdate --> ENDE
    style ENDE stroke-width:5px
    classDef script fill:#EDF2AE,stroke:#666,stroke-width:4px
```
