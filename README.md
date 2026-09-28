[![Project Status: Active – The project has reached a stable, usable state and is being actively developed.](https://www.repostatus.org/badges/latest/active.svg)](https://www.repostatus.org/#active)

> [!Note]
> This repository collects descriptions and instructions for the City of Zurich's APIs. It also contains workflows for automatic data updates of the open data catalogue.
> 
> In diesem Repository werden Beschreibungen und Anleitungen zu APIs der Stadt Zürich gesammelt. Ausserdem enthält es Workflows für automatische Datenaktualisierungen des Open Data Katalogs.

# Open Data Zurich API Dokumentation

Die Open Data Zurich API Dokumentation bietet eine Übersicht über verschiedene APIs (Schnittstellen), die von der Stadt Zürich zur Verfügung gestellt werden, sowie Trainingsmaterial für verschiedene Gebiete der Datennutzung. Diese Ressourcen ermöglichen den Zugriff auf unterschiedliche Datensätze und Informationen, die für Entwickler:innen, Forscher:innen und interessierte Bürger:innen nützlich sein können.

## Verfügbare Schnittstellen/APIs

1. [RIS-API (Ratshausinformationssystems), Gemeinderat Stadt Zürich (GRZ)](/ris-api/): Diese API bietet Zugang zu Informationen des Parlamentsinformationssystem (Paris) des Gemeinderats der Stadt Zürich.
1. [Zürich Tourismus API](/zt-api/): Über das Zürich Tourismus API lassen sich Daten von Zürich Tourismus über Attraktionen, Unterkünfte, Restaurants und mehr abfragen.
1. [ParkenDD API](/parkendd-api/): Diese API liefert Daten zu Parkplätzen in Zürich, einschließlich Verfügbarkeit und Standorte.
1. [Geoportal der Stadt Zürich](/geoportal/): Diese Dokumentation beschreibt den Umgang mit Daten aus dem [Geoportal der Stadt Zürich](https://www.stadt-zuerich.ch/geodaten/) ohne GIS-Software.
1. [RPK-API (Finanzdaten der Stadt Zürich), Finanzverwaltung](/rpk-api/): Diese API stellt Finanzdaten der Stadt Zürich zur Verfügung, die von der Finanzverwaltung bereitgestellt werden.
1. [SRU-API des Stadtarchivs Zürich](https://opendatazurich.github.io/sar-sru-api/): Diese API bietet Zugang zu historischen Daten und Archivmaterial des Stadtarchivs Zürich.

## Trainingsmaterial

1. [Wikidata Training](https://opendatazurich.github.io/wikidata-training/): Trainingsmaterial zu Wikidata Abfragen mit Python.
1. [Crashkurs «Datenvisualisierung»](https://opendatazurich.github.io/crashkurs-dataviz/): Einfache Datenanalyse und -visualisierung mit Excel und Datawrapper.
1. [Crashkurs «Power BI Datenvisualisierung»](https://opendatazurich.github.io/crashkurs-dataviz-powerbi/): Eine Anleitung für Power BI-Einsteiger:innen unter Verwendung von Open Data.
1. [Kurs «Crowdsourcing-Daten nutzen» (OpenSteetMap, Wikidata)](https://opendatazurich.github.io/kurs-crowdsourced-data/): Workshop in Form eines Jupyter Notebooks um städtische Daten mit OpenStreetMap und WikiData kombinieren.
1. [Starter Code](https://opendatazurich.github.io/starter-code/): Einfache Code Vorlagen in Python und R für jeden Datensatz auf https://data.stadt-zuerich.ch/.

## Weitere Projekte

1. [Schnelleinstieg ins Thema OGD](https://opendatazurich.github.io/ssz_odz_schnelleinstieg/): Der «Schnelleinstieg Open Government Data» bietet Ihnen einen direkten Zugang zum Thema. Entstanden ist er für das Wissenschaftsfestival Scientifica. Hier finden Sie Antworten zu den Fragen: Wo finde ich offene Verwaltungsdaten? Was wurde mit offenen Daten bereits erstellt? Wie kann ich diese mit natürlicher Sprache abfragen? Wie kann ich sofort offene Verwaltungsdaten analysieren?
1. [Umfrage bei OGD-Katalog-Nutzenden](https://opendatazurich.github.io/umfrage-ogd-katalog/): Auswertung einer Online-Befragung von Statistik Stadt Zürich und der Universität Zürich dazu, wie die offenen Verwaltungsdaten der Stadt Zürich genutzt und wahrgenommen werden.

# Automation

Über das Repository [opendatazurich.github.io](https://github.com/opendatazurich/opendatazurich.github.io) werden einige Datenaktualisierungen des [OGD Katalogs](https://data.stadt-zuerich.ch/) verwaltet. Der Code dazu befindet sich im Unterordner "automation" und wird über Github Actions ausgeführt. Das Monitoring der workflows wird in diesem [Repository](https://github.com/opendatazurich/github_actions_monitor) verwaltet.
