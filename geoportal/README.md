# Geoportal

Diese Dokumentation beschreibt den Umgang mit Daten aus dem [Geoportal der Stadt Zürich](https://www.ogd.stadt-zuerich.ch/geodaten/).
Insbesondere werden via Geoportal viele Datensätze als Geo-Webservices (z.B. WMS, WFS) angeboten.
Auf dem Geoportal können die Datensätze manuell in vielen verschiedenen Formaten heruntergeladen werden (z.B. GeoJSON, GPKG, Shapefile, CSV).

**Inhaltsverzeichnis**

1. [Beispiel-Abfragen mit WFS](#beispiel-abfragen-mit-wfs)
   1. [GetCapabilities](#getcapabilities)
   2. [GetFeature](#getfeature)
2. [Programmier-Beispiele](#programmier-beispiele)

## Beispiel-Abfragen mit WFS

Um Daten via WFS zu beziehen, muss zuerst die WFS-URL ausfindig gemacht werden.
Dazu verwendet man am besten direkt das [Geoportal der Stadt Zürich](https://www.ogd.stadt-zuerich.ch/geodaten/).
Auf dem OGD-Katalog gibt es jeweils Verweise auf die Datensätze des Geoportals.

Wenn man einen Datensatz gefunden hat, dessen Daten man gerne verwenden möchte, findet man ganz unten auf dem Geoportal den Link zum WFS-Server:
![](wfs_link.gif)

In diesem Beispiel wird der [Datensatz "Statistische Quartiere"](https://www.ogd.stadt-zuerich.ch/geodaten/Statistische_Quartiere) verwendet.
Der zugehörige WFS-Link ist: https://www.ogd.stadt-zuerich.ch/wfs/geoportal/Statistische_Quartiere

Über [Geocat](https://www.geocat.ch/geonetwork/srv/ger/md.viewer#/full_view/fd1a94fe-4bd4-4a40-99af-8b859dfe82a7) (Link "Komplette Metadaten ansehen" auf dem Geoportal) kann man eine Beschreibung der Metadaten anschauen.
WFS liefert sogenannte Features, und die Features sind in verschiedene Typen ("Layer") gegliedert.
Auf Geocat sind alle Layer beschrieben und der passende kann gewählt werden.

In unserem Beispiel "Statistische Quartiere" gibt es folgende Layer:

* `adm_statistische_quartiere_a`
* `adm_statistische_quartiere_b_p`
* `adm_statistische_quartiere_map`
* `adm_statistische_quartiere_v`

Beim Layer `adm_statistische_quartiere_map` heisst es:

> Dieser Layer kann für Datenvisualisierungen und kartographische Darstellungen verwendet werden.

Dies scheint für Visialisierungen der geeignete Layer zu sein.

### GetCapabilities

Die ganzen Informationen zum Server liefert beim WFS der `GetCapabilities`-Aufruf:

https://www.ogd.stadt-zuerich.ch/wfs/geoportal/Statistische_Quartiere?service=WFS&version=1.1.0&request=GetCapabilities

Das zurückgelieferte XML beinhaltet alle wichtigen Informationen:

* Unterstützte Requests des Servers
* Projektion der Daten
* Unterstützte Dateiformate
* Unterstütze Filter

### GetFeature

Mit `GetFeature` lassen sich Daten via WFS beziehen, z.B. die Statistischen Quartiere als GeoJSON:

https://www.ogd.stadt-zuerich.ch/wfs/geoportal/Statistische_Quartiere?service=WFS&version=1.1.0&request=GetFeature&typename=adm_statistische_quartiere_map&outputFormat=GeoJSON


## Programmier-Beispiele

Im [Jupyter-Notebook Geoportal-Beispiele.ipynb](https://github.com/opendatazurich/opendatazurich.github.io/blob/master/geoportal/Geoportal-WMS-WFS.ipynb) sind einige Python-Beispiele gezeigt, u.a. wie Daten via WFS bezogen werden können oder eine Karte via WMS angezeigt werden kann.

Mit Binder kann das Jupyter-Notebook interaktiv im Browser gestartet werden: [![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/opendatazurich/opendatazurich.github.io/master?filepath=geoportal/Geoportal-Beispiele.ipynb)
