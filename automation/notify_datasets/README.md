Harvester Notifications
=======================

||Beschreibung|
|---|---|
|**Status:**|[![Notify about new/updated datasets](https://github.com/opendatazurich/opendatazurich.github.io/actions/workflows/notify_datasets.yml/badge.svg)](https://github.com/opendatazurich/opendatazurich.github.io/actions/workflows/notify_datasets.yml)|
|**Workflow:**|[`notify_datasets.yml`](https://github.com/opendatazurich/opendatazurich.github.io/blob/master/.github/workflows/notify_datasets.yml)|
|**Quelle:**| CKAN API

Jeder Morgen wird dieser Workflow gestartet und notifiziert das OGD-Team via Telegram über den Stand aller Harvester.
Die Daten stammen alle vom CKAN API.

Der ganze Ablauf ist im Skript [`notify.py`](https://github.com/opendatazurich/opendatazurich.github.io/blob/master/automation/notify_datasets/notify.py) implementiert.

## Dokumentation

- notify.py holt sich via CKAN API mit der Action `harvest_source_list` eine Liste aller Harvester und iteriert durch diese Liste.
- Von jedem Harvester:
   * ...werden die aktuellen Infos via `harvest_source_show` geholt, insbesondere die Angaben zum letzten Harvest-Run
   * ...die Angaben zum letzten Run werden interpretiert (Wie lange hat der Run gedauert? Wurden dabei Datensätze hinzugefügt oder gelöscht?)
- Basierend darauf wird ein Status erstellt mit einer Ampel (🟢 = Alles ok, 🟡 = neue Datensätze, evtl. prüfen, 🔴 = Fehler beim Harvester oder gelöschte Datensätze, prüfen)
- Zudem werden Links generiert, die es erlauben zu prüfen welche Datensätze aktualisiert oder neu erstellt wurden
- Alle jeder Harvester-Status wird dann als Telegram-Nachricht einzeln verschickt.
