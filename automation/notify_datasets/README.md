Harvester Notifications
=======================

||Beschreibung|
|---|---|
|**Status:**|[![Update stimmbeteiligung data](https://github.com/opendatazurich/opendatazurich.github.io/actions/workflows/update_stimmbeteiligung.yml/badge.svg)](https://github.com/opendatazurich/opendatazurich.github.io/actions/workflows/update_stimmbeteiligung.yml)|
|**Workflow:**|[`update_stimmbeteiligung.yml`](https://github.com/opendatazurich/opendatazurich.github.io/blob/master/.github/workflows/update_stimmbeteiligung.yml)|
|**Quelle:**| [Webseite der Stadtkanzlei](https://www.stadt-zuerich.ch/portal/de/index/politik_u_recht/abstimmungen_u_wahlen/aktuell/stand-stimmbeteiligung.html)
|**Datensatz INT:**|[Stimmbeteiligung in Prozent vor Urnengängen (data.integ.stadt-zuerich.ch)](https://data.integ.stadt-zuerich.ch/dataset/politik_stimmbeteiligung-vor-urnengangen)|
|**Datensatz PROD:**|[Stimmbeteiligung in Prozent vor Urnengängen (data.stadt-zuerich.ch)](https://data.stadt-zuerich.ch/dataset/politik_stimmbeteiligung-vor-urnengangen)|

Jeder Morgen wird dieser Workflow gestartet und notifiziert das OGD-Team via Telegram über den Stand aller Harvester.
Die Daten stammen alle vom CKAN API.

Der ganze Ablauf ist im Skript [`notify.sh`](https://github.com/opendatazurich/opendatazurich.github.io/blob/master/automation/notify_datasets/notify.py) implementiert.
