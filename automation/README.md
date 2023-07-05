OGD Automation
==============

In diesem Verzeichnis ist der Code für zahlreiche Automationen, welche mit GitHub Actions gesteuert werden.
Die meisten Automationen dienen dazu, Datensätze auf dem Open-Data-Katalog zu aktualisieren.
Grundsätzlich werden keine neuen Datensätze durch diesen Code hier angelegt, sondern lediglich bestehende Datensätze aktualisiert.
D.h. bedeutet, dass initial ein neuer Datensatz manuell angelegt werden muss (entweder durch das CKAN Backend oder via API).


## GitHub Action

Eine GitHub Action wird durch eine YAML-Datei beschreiben, diese sind alle im Verzeichnis `.github/workflows` abgelegt.

GitHub hat eine [umfangreiche Dokumentation zu GitHub Actions](https://docs.github.com/de/actions) und wie diese Dateien aufgebaut sind.
In dieser Dokumentation werden lediglich die wichtigsten Punkte erklärt.

```mermaid
flowchart TD
    A>"Zeitsteuerung ⌛️"]
    B>"Manuell"]
    C(GitHub Action starten)
    A --> C
    B --> C
    C --> D{Daten geändert im Repo?}
    D -->|Ja| E(Commit + Push)
    D -->|Nein| F(Daten in CKAN aktualiseren)
    E --> F
    F --> G(Metadaten in CKAN aktualisieren)
    G --> Ende
```

### Secrets
### 
