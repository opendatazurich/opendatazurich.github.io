# RIS-API, Gemeinderat Stadt Zürich (GRZ)

Diese Dokumentation beschreibt die Programmierschnittstelle (API) des Ratshausinformationssystems (RIS) des Gemeinderats der Stadt Zürich. Über das API lassen sich folgende Entitäten abfragen:

* Mitglieder
* Geschäfte
* Protokolle
* Ratspost

Das komplette API ist als OpenAPI Spezifikation (Swagger) verfügbar. Dort sind alle Endpunkte und deren Parameter im Detail erklärt.

**Inhaltsverzeichnis**

1. [Beispiele](#beispiele)
   1. [Mitglieder suchen](#mitglieder-suchen)
2. [Programmier-Beispiele](#programmier-beispiele)

## Beispiele

### Mitglieder suchen

**Endpunkt:**

`http://www.gemeinderat-zuerich.ch/api/Mitglieder?name={{name}}&parteiId={{parteiId}}&fraktionId={{fraktionId}}&wahlkreisId={{wahlkreisId}}&wohnkreisId={{wohnkreisId}}&kommissionId={{kommissionId}}&includeInactive={{includeInactive}}&orderBy={{orderBy}}&orderDir={{orderDir}}`

Die IDs (`parteiId`, `fraktionId`, `wahlkreisId` etc.) können mit dem `/Mitglieder/parameter` Endpunkt gefunden werden.

**Suche nach Name "Martin":**

`GET http://www.gemeinderat-zuerich.ch/api/Mitglieder?name=Martin`

```json
[
    {
        "Id": "72d9c149-3269-42b0-848e-0e21fc8b0c21",
        "Name": "Bürki",
        "Vorname": "Martin",
        "Titel": null,
        "Partei": "FDP",
        "Wahlkreis": "1 und 2",
        "WahlkreisOrderBy": 100
    },
    {
        "Id": "a2c59a56-f498-4b31-bd0d-270e54146fcc",
        "Name": "Götzl",
        "Vorname": "Martin",
        "Titel": null,
        "Partei": "SVP",
        "Wahlkreis": "11",
        "WahlkreisOrderBy": 107
    },
    {
        "Id": "8ba66468-4f2e-450d-9b7e-dbac5e6a26ae",
        "Name": "Marti",
        "Vorname": "Elena",
        "Titel": null,
        "Partei": "Grüne",
        "Wahlkreis": "11",
        "WahlkreisOrderBy": 107
    },
    {
        "Id": "e965adf7-71b7-4e39-a714-175ee4990207",
        "Name": "Marti",
        "Vorname": "Res",
        "Titel": null,
        "Partei": "Grüne",
        "Wahlkreis": " 9",
        "WahlkreisOrderBy": 105
    },
    {
        "Id": "1a2aa558-cbd2-4ab6-8725-7c791cec92ad",
        "Name": "Novak",
        "Vorname": "Martina",
        "Titel": null,
        "Partei": "GLP",
        "Wahlkreis": "7 und 8",
        "WahlkreisOrderBy": 104
    },
    {
        "Id": "3b4bbd28-c4d5-4e62-b4f3-0f32b8a7589b",
        "Name": "Zürcher",
        "Vorname": "Martina",
        "Titel": null,
        "Partei": "FDP",
        "Wahlkreis": "10",
        "WahlkreisOrderBy": 106
    }
]
```



**Suche nach Mitgliedern der GPK:**

`GET http://www.gemeinderat-zuerich.ch/api/Mitglieder?kommissionId=d050df43-5336-47c2-8bf0-11f0bab7758a`

```json
[
    {
        "Id": "8eb28350-c0cb-42db-b4bd-b753fd38ff7b",
        "Name": "Bätschmann",
        "Vorname": "Monika",
        "Titel": null,
        "Partei": "Grüne",
        "Wahlkreis": "10",
        "WahlkreisOrderBy": 106
    },
    {
        "Id": "ba439e1f-e568-4b4b-9816-9fa94a2fb3e5",
        "Name": "Beer",
        "Vorname": "Duri",
        "Titel": null,
        "Partei": "SP",
        "Wahlkreis": " 3",
        "WahlkreisOrderBy": 101
    },
    {
        "Id": "bbfb8ca0-91b1-448d-b1fc-c5e3bb35c158",
        "Name": "Eberle",
        "Vorname": "Natalie",
        "Titel": null,
        "Partei": "AL",
        "Wahlkreis": " 3",
        "WahlkreisOrderBy": 101
    },
    {
        "Id": "af7eb3bf-d095-4438-bc6b-847b3d0db23b",
        "Name": "Helfenstein",
        "Vorname": "Urs",
        "Titel": null,
        "Partei": "SP",
        "Wahlkreis": "4 und 5",
        "WahlkreisOrderBy": 102
    },
    {
        "Id": "3ad30c09-6873-4ee0-a9cf-8b699a5e943c",
        "Name": "im Oberdorf",
        "Vorname": "Bernhard",
        "Titel": "Dr.",
        "Partei": "SVP",
        "Wahlkreis": "12",
        "WahlkreisOrderBy": 108
    },
    {
        "Id": "ceb880c2-db62-491a-9f62-883bb8e72a81",
        "Name": "Kälin-Werth",
        "Vorname": "Simon",
        "Titel": null,
        "Partei": "Grüne",
        "Wahlkreis": "7 und 8",
        "WahlkreisOrderBy": 104
    },
    {
        "Id": "6f80de0e-2322-46c4-891b-3a2781b127c9",
        "Name": "Landolt",
        "Vorname": "Maleica",
        "Titel": null,
        "Partei": "GLP",
        "Wahlkreis": "11",
        "WahlkreisOrderBy": 107
    },
    {
        "Id": "f74d8d44-3950-49bd-983e-3498b36b42ec",
        "Name": "Renggli",
        "Vorname": "Matthias",
        "Titel": null,
        "Partei": "SP",
        "Wahlkreis": " 6",
        "WahlkreisOrderBy": 103
    },
    {
        "Id": "f68282d3-d683-48cf-ade1-c08da3dd76da",
        "Name": "Schmid",
        "Vorname": "Michael",
        "Titel": null,
        "Partei": "FDP",
        "Wahlkreis": "1 und 2",
        "WahlkreisOrderBy": 100
    },
    {
        "Id": "42817325-1645-42da-bd71-a34faa5e597b",
        "Name": "Seidler",
        "Vorname": "Christine",
        "Titel": "Prof.",
        "Partei": "SP",
        "Wahlkreis": " 9",
        "WahlkreisOrderBy": 105
    },
    {
        "Id": "3b4bbd28-c4d5-4e62-b4f3-0f32b8a7589b",
        "Name": "Zürcher",
        "Vorname": "Martina",
        "Titel": null,
        "Partei": "FDP",
        "Wahlkreis": "10",
        "WahlkreisOrderBy": 106
    }
]
```

## Programmier-Beispiele

Im Jupyter-Notebook "Examples.ipynb" sind einige Python-Beispiele im Umgang mit dem API beschrieben.

[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/opendatazurich/opendatazurich.github.io/master?filepath=ris-api/examples/Examples.ipynb)