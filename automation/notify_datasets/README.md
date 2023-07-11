Harvester Notifications
=======================

||Beschreibung|
|---|---|
|**Status:**|[![Notify about new/updated datasets](https://github.com/opendatazurich/opendatazurich.github.io/actions/workflows/notify_datasets.yml/badge.svg)](https://github.com/opendatazurich/opendatazurich.github.io/actions/workflows/notify_datasets.yml)|
|**Workflow:**|[`notify_datasets.yml`](https://github.com/opendatazurich/opendatazurich.github.io/blob/master/.github/workflows/notify_datasets.yml)|
|**Quelle:**| CKAN API

Jeder Morgen wird dieser Workflow gestartet und notifiziert das OGD-Team via Telegram über den Stand aller Harvester.
Die Daten stammen alle vom CKAN API.

Der ganze Ablauf ist im Skript [`notify.sh`](https://github.com/opendatazurich/opendatazurich.github.io/blob/master/automation/notify_datasets/notify.py) implementiert.
