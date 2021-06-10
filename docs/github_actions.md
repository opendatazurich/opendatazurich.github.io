\newpage

GitHub Actions
==============

GitHub Actions sind ein IaaS (Infrastructure as a service) um beliebigen Code in der Cloud auszuführen.

Bei Open Data Zürich verwenden wir GitHub Actions für 2 Hauptzwecke

1. Automatisierung von Abläufen im Zusammenhang mit dem Open-Data-Katalog
2. Datenaufbereitung von Datensätzen, die über das öffentliche Internet zugänglich sind

In den nachfolgenden Kapiteln werden die einzelnen GitHub Actions beschrieben.

## Open-Data-Katalog Automatisierung

Da unser [Open-Data-Katalog](https://data.stadt-zuerich.ch/) auf CKAN[^ckan] basiert, lassen sich beliebige Aktionen mithilfe des CKAN APIs automatisieren.

### Tagger

Der [Tagger](https://github.com/opendatazurich/opendatazurich.github.io/tree/master/automation/tagger) läuft [regelmässig](https://github.com/opendatazurich/opendatazurich.github.io/actions/workflows/tagger.yml) und setzt bestimmte Tags auf CKAN Datasätzen gemäss der definierten [Konfigurationsdatei](https://github.com/opendatazurich/opendatazurich.github.io/blob/master/automation/tagger/config.yml).

```yaml
architektur:
    tags:
        - architektur
        - arch-hack
    datasets:
        - sid_dav_verkehrszaehlung_miv_od2031
        - sar_geschaeftsberichte

hackathonx:
    tags:
        - hackathonx
        - test123
    queries:
        - "tags:sasa"
```

In der Konfigurationsdatei können beliebige Gruppen definiert werden (im obigen Beispiel `architektur` und `hackathonx`).
Jede Gruppe definiert Tags (als Liste unterhalb von `tags:`), die vergeben werden sollen.
Die Datasets für welche diese Tags vergeben werden sollen lassen sich auf zwei Arten definieren:

1. Liste von Datasets
1. Liste von Queries

Unter `datasets:` (in der Gruppe `architektur` oben) lassen sich beliebig viele Datasets als Liste von Slugs konfigurieren.

Unter `queries:` (in der Gruppe `hackathonx` oben) lassen sich beliebig viele Queries definieren.
Bei den Queries handelt es sich um CKAN-Queries, siehe dazu auch [«Daten finden» (handbook.opendata.swiss)](https://handbook.opendata.swiss/de/content/nutzen/daten-suchen.html).

Es ist auch möglich Queries und eine Liste von Datensätzen miteinander zu verbinden.

### Metadaten-Export als Excel

Diese Action dient dazu, bei Bedarf ein Metadaten-Excel (nach unserer internen Vorlage) zu generieren, basierend auf den in CKAN erfassten Metadaten.
Die Action kann [auf GitHub aufgerufen werden](https://github.com/opendatazurich/opendatazurich.github.io/actions/workflows/export.yml) und als Parameter kann der Slug[^slug] eines Datensatzes angegeben werden.

Die resultierende Excel-Datei kann für max. 90 Tage als Artifact auf einem erfolgreich durchgelaufenen Job heruntergeladen werden ([Beispiel](https://github.com/opendatazurich/opendatazurich.github.io/actions/runs/748390438)).

### Notifikation über die Harvester

Für das Open Data Zürich Team ist es wichtig, täglich informiert zu sein, ob alle Harvester[^harvester] erfolgreich durchgelaufen sind und ob es neue, aktualisierte oder gelöschte Datensätze gibt.
Zu diesem Zweck läuft [dieser Job jeden Morgen](https://github.com/opendatazurich/opendatazurich.github.io/actions/workflows/notify_datasets.yml) und liefert diese Informationen in einen definierten Slack-Channel.

## Datenaufbereitung von öffentlich zugänglichen Daten

Es gibt einige Datensätze, die öffentlich zugänglich sind, jedoch für OGD noch aufbereitet werden müssen. Die Skripts dazu sind in [opendatazurich.github.io > automation]( https://github.com/opendatazurich/opendatazurich.github.io/tree/master/automation) abgelegt. Datensätze, die auf nur intern zugänglichen Daten basieren, werden im Kapitel [Datenaufbereitung mit Python](/docs/ogd_processing.md) beschrieben.

### SSD: Schulferien

Für die Schulferien, werden die [ICS-Dateien vom Schulamt](https://www.stadt-zuerich.ch/ssd/de/index/volksschule/schulferien.html) von der Webseite gescrapt, in ein CSV umgewandelt und schliesslich auf CKAN als Datensatz zur Verfügung gestellt.

### VBZ: Passagierfrequenzen

Dabei handelt es sich um ein internes REST-API, welches alle 30min abgefragt wird und das Ergebnis als CSV auf CKAN zur Verfügung gestellt wird.

### SAR: Geschäftsberichte

Für die Geschäftsberichte wird ein internes API des Stadtarchivs abgefragt und das Ergebnis als CSV zur Verfügung gestellt.

### SKZ: Abstimmungsparolen

Die Stadtkanzlei erfasst auf ihrer [Webseite zu den Gemeindeabstimmungen](https://www.stadt-zuerich.ch/portal/de/index/politik_u_recht/abstimmungen_u_wahlen.html) die Abstimmungsparolen der Parteien im Gemeinderat.
Diese Daten werden jeweils ca. 4 Wochen vor einer Abstimmung erfasst.
Ein Webscraper holt sich die Angaben zu jeder Abstimmung und stellt automatisiert ein CSV auf CKAN zur Verfügung.

[^ckan]: CKAN ist eine Open Source Katalogsoftware, mehr Informationen unter https://ckan.org/.
[^slug]: Der Slug bezeichnet den letzen Teil der URL eines Datasets, bei https://data.stadt-zuerich.ch/dataset/sar_geschaeftsberichte wäre `sar_geschaeftsberichte` der Slug.
[^harvester]: Harvester sind Programme, die automatisiert Daten aus einer Quelle holen und diese in den Open-Data-Katalog importieren.
