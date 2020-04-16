# RPK-API, Finanzverwaltung

Diese Dokumentation beschreibt die Programmierschnittstelle (API) der Finanzdaten der Finanzverwaltung. Über das API lassen sich folgende Entitäten abfragen:

* Departemente/Institutionen
* Konten
* Beträge/Betragsreihen

![Modell](<https://opendatazurich.github.io/rpk-api/model.png>)


Für das API gibt es eine [interaktive Dokumentation der Endpunkte und deren Parameter](/rpk-api/docs/), welche alle Details beschreibt.

![RPK-API-API Dokumentation](<https://opendatazurich.github.io/rpk-api/rpk_api_swagger-ui.png>)

Das komplette API steht auch als [OpenAPI Spezifikation (Swagger-File)](/rpk-api/docs/openapi.yaml) zum Downlaod zur Verfügung.

Diese Dokumentation bietet einen **Schnelleinstieg in das RPK-API**.
Im Kapitel 1 werden ein paar typische Beispiels-Abfragen erläutert. 
Im Kapitel 2 wird ein konkretes Programmier-Beispiel mit Python als Jupyter-Notebook zur Verfügung gestellt.


**Inhaltsverzeichnis**

1. [Beispiel-Abfragen](#beispiel-abfragen)
   1. [Departemente suchen](#departemente-suchen)
   2. [Institutionen suchen](#institutionen-suchen)
2. [Programmier-Beispiele](#programmier-beispiele)

## Beispiel-Abfragen

### Departemente abfragen

**Endpunkt:**

`https://api.stadt-zuerich.ch/rpkk-rs/v1/departemente/{orgKey}`

Der orgKey Parameter ist optional, er kann verwendet werden um einen Departements-Key wieder aufzulösen in den zugehörigen Namen.

**ACHTUNG:** Der orgKey eines Departements entspricht nicht dem orgKey einer Institution. Ein Departement ist auch eine Institution und hat entsprechend zwei verschiedene Keys.


**Alle Departemente anzeigen:**

`GET https://api.stadt-zuerich.ch/rpkk-rs/v1/departemente`

```json
{
    "value": [
        {
            "bezeichnung": "Behörden und Gesamtverwaltung",
            "key": "10",
            "kurzname": "BUG"
        },
        {
            "bezeichnung": "Präsidialdepartement",
            "key": "15",
            "kurzname": "PRD"
        },
        {
            "bezeichnung": "Finanzdepartement",
            "key": "20",
            "kurzname": "FD"
        },
        {
            "bezeichnung": "Sicherheitsdepartement",
            "key": "25",
            "kurzname": "SID"
        },
        {
            "bezeichnung": "Gesundheits- und Umweltdepartement",
            "key": "30",
            "kurzname": "GUD"
        },
        {
            "bezeichnung": "Tiefbau- und Entsorgungsdepartement",
            "key": "35",
            "kurzname": "TED"
        },
        {
            "bezeichnung": "Hochbaudepartement",
            "key": "40",
            "kurzname": "HBD"
        },
        {
            "bezeichnung": "Departement der Industriellen Betriebe",
            "key": "45",
            "kurzname": "DIB"
        },
        {
            "bezeichnung": "Schul- und Sportdepartement",
            "key": "50",
            "kurzname": "SSD"
        },
        {
            "bezeichnung": "Sozialdepartement",
            "key": "55",
            "kurzname": "SD"
        }
    ]
}
```

**Ein einzelnes Departement anzeigen:**

`GET https://api.stadt-zuerich.ch/rpkk-rs/v1/departemente/20`

```json
{
    "bezeichnung": "Finanzdepartement",
    "key": "20",
    "kurzname": "FD"
}
```

### Institutionen suchen


**Endpunkt:**

`https://api.stadt-zuerich.ch/rpkk-rs/v1/institutionen/{orgKey}`

Der orgKey Parameter ist optional, er kann verwendet werden um einen Instiutions-Key wieder aufzulösen in den zugehörigen Namen.

**ACHTUNG:** Der orgKey einer Institution entspricht nicht dem orgKey eines Departements. Eine Instistution gehört immer zu einem Departement.

**Alle Institutionen anzeigen:**

`GET https://api.stadt-zuerich.ch/rpkk-rs/v1/institutionen`

```json
{
    "value": [
        {
            "bezeichnung": "Gemeinde",
            "departement": {
                "bezeichnung": "Behörden und Gesamtverwaltung",
                "key": "10",
                "kurzname": "BUG"
            },
            "key": "1000",
            "kurzname": "GZ"
        },
        {
            "bezeichnung": "Gemeinderat",
            "departement": {
                "bezeichnung": "Behörden und Gesamtverwaltung",
                "key": "10",
                "kurzname": "BUG"
            },
            "key": "1005",
            "kurzname": "GRZ"
        },
        {
            "bezeichnung": "Finanzkontrolle",
            "departement": {
                "bezeichnung": "Behörden und Gesamtverwaltung",
                "key": "10",
                "kurzname": "BUG"
            },
            "key": "1007",
            "kurzname": "ZFK"
        },
        {
            "bezeichnung": "Beauftragte/r in Beschwerdesachen",
            "departement": {
                "bezeichnung": "Behörden und Gesamtverwaltung",
                "key": "10",
                "kurzname": "BUG"
            },
            "key": "1010",
            "kurzname": "OMB"
        },
        {
            "bezeichnung": "Stadtrat",
            "departement": {
                "bezeichnung": "Behörden und Gesamtverwaltung",
                "key": "10",
                "kurzname": "BUG"
            },
            "key": "1015",
            "kurzname": "STR"
        },
        {
            "bezeichnung": "Stadtkanzlei",
            "departement": {
                "bezeichnung": "Behörden und Gesamtverwaltung",
                "key": "10",
                "kurzname": "BUG"
            },
            "key": "1020",
            "kurzname": "SKZ"
        },
        {
            "bezeichnung": "Rechtskonsulent",
            "departement": {
                "bezeichnung": "Behörden und Gesamtverwaltung",
                "key": "10",
                "kurzname": "BUG"
            },
            "key": "1025",
            "kurzname": "REK"
        },
        {
            "bezeichnung": "Kindes- und Erwachsenenschutzbehörde (neu 5530)",
            "departement": {
                "bezeichnung": "Behörden und Gesamtverwaltung",
                "key": "10",
                "kurzname": "BUG"
            },
            "key": "1030",
            "kurzname": "KEB"
        },
        {
            "bezeichnung": "Datenschutzbeauftragte/r",
            "departement": {
                "bezeichnung": "Behörden und Gesamtverwaltung",
                "key": "10",
                "kurzname": "BUG"
            },
            "key": "1035",
            "kurzname": "DAS"
        },
        {
            "bezeichnung": "Gesamtverwaltung",
            "departement": {
                "bezeichnung": "Behörden und Gesamtverwaltung",
                "key": "10",
                "kurzname": "BUG"
            },
            "key": "1060",
            "kurzname": "GVZ"
        },
        {
            "bezeichnung": "Stadtamtsfrau-/Stadtammann- und Betreibungsämter",
            "departement": {
                "bezeichnung": "Behörden und Gesamtverwaltung",
                "key": "10",
                "kurzname": "BUG"
            },
            "key": "1070",
            "kurzname": "BNN"
        },
        {
            "bezeichnung": "Friedensrichterinnen- und Friedensrichterämter",
            "departement": {
                "bezeichnung": "Behörden und Gesamtverwaltung",
                "key": "10",
                "kurzname": "BUG"
            },
            "key": "1080",
            "kurzname": "FNN"
        },
        {
            "bezeichnung": "Präsidialdepartement Departementssekretariat",
            "departement": {
                "bezeichnung": "Präsidialdepartement",
                "key": "15",
                "kurzname": "PRD"
            },
            "key": "1500",
            "kurzname": "PRD"
        },
        {
            "bezeichnung": "Kultur (alt)",
            "departement": {
                "bezeichnung": "Präsidialdepartement",
                "key": "15",
                "kurzname": "PRD"
            },
            "key": "1501",
            "kurzname": "KTR"
        },
        {
            "bezeichnung": "Stadtentwicklung",
            "departement": {
                "bezeichnung": "Präsidialdepartement",
                "key": "15",
                "kurzname": "PRD"
            },
            "key": "1505",
            "kurzname": "STE"
        },
        {
            "bezeichnung": "Fachstelle für Gleichstellung",
            "departement": {
                "bezeichnung": "Präsidialdepartement",
                "key": "15",
                "kurzname": "PRD"
            },
            "key": "1506",
            "kurzname": "ZFG"
        },
        {
            "bezeichnung": "Museum Rietberg",
            "departement": {
                "bezeichnung": "Präsidialdepartement",
                "key": "15",
                "kurzname": "PRD"
            },
            "key": "1520",
            "kurzname": "MRZ"
        },
        ...
    ]
}
```


## Programmier-Beispiele

Im [Jupyter-Notebook RPK-API-Beispiele.ipynb](https://github.com/opendatazurich/opendatazurich.github.io/blob/master/rpk-api/RPK-API-Beispiele.ipynb) sind einige Python-Beispiele im Umgang mit dem API beschrieben.

Jupyter-Notebook interaktiv im Browser starten: 

[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/opendatazurich/opendatazurich.github.io/master?filepath=rpk-api/RPK-API-Beispiele.ipynb)

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/opendatazurich/opendatazurich.github.io/blob/master/rpk-api/RPK-API-Beispiele.ipynb)

![RPK-API Dokumentation](<https://opendatazurich.github.io/rpk-api/rpk_api_binder.png>)
