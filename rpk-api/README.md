# RPK-API, Finanzverwaltung

Diese Dokumentation beschreibt die Programmierschnittstelle (API) der Finanzdaten der Finanzverwaltung.

**Inhaltsverzeichnis**

1. [Modell](#modell)
1. [Beispiel-Abfragen](#beispiel-abfragen)
   1. [Departemente suchen](#departemente-suchen)
   1. [Institutionen suchen](#institutionen-suchen)
   1. [Konten abfragen](#konten-abfragen)
   1. [Betragsreihen von Konto abfragen](#betragsreihen-von-konto-abfragen)
   1. [2-stellige Sachkonten abfragen](#2-stellige-sachkonten-abfragen)
1. [Programmier-Beispiele](#programmier-beispiele)

Diese Dokumentation bietet einen **Schnelleinstieg in das RPK-API**
Im ersten Teil wird das Modell und ein paar typische Beispiels-Abfragen erläutert. 
Im zweiten Teil wird ein konkretes Programmier-Beispiel mit Python als Jupyter-Notebook zur Verfügung gestellt.

Für das API gibt es eine [interaktive Dokumentation der Endpunkte und deren Parameter](/rpk-api/docs/), welche alle Details beschreibt.

<img src="https://opendatazurich.github.io/rpk-api/rpk_api_swagger-ui.png" height="50%" width="50%" alt="Modell" title="RPK-API Dokumentation">

Das komplette API steht auch als [OpenAPI Spezifikation (Swagger-File)](/rpk-api/docs/openapi.yaml) zum Downlaod zur Verfügung.

## Modell

Über das API lassen sich folgende Entitäten abfragen:

* Departemente/Institutionen
* Konten
* Beträge/Betragsreihen

<img src="https://opendatazurich.github.io/rpk-api/model.png" height="50%" width="50%" alt="Modell" title="Modell">


Der städtische Budget- und Rechnungsprozess durchläuft eine Reihe von Phasen:
Vom Antrag an den Stadtrat, über Nachträge im sogenannten Novemberbrief über das vom Gemeinderat beschlossene Budget sowie zwei Serien mit Nachtragskrediten.
Diese Phasen sind im API als Betragstypen abgebildet.

<img src="https://opendatazurich.github.io/rpk-api/budgetprozess.png" height="50%" width="50%" alt="Budgetprozess" title="Budgetprozess">

### Nachtragskredite

Die zwei Serien von Nachtragskrediten sind jeweils mit einem Code versehen:


| Code* | Serie | Bezeichnung | Parameter `betragsTyp` für das API                                          | Bemerkung |                                                                      
| ----- | ----- | ----------- | --------------------------------------------------------------------------- | --------- |
| N11   | 1     | Ordentlicher Nachtragkredit  | `NACHTRAGSKREDIT11_ANTRAG`, `NACHTRAGSKREDIT11_BESCHLUSS`  |           |        
| N12   | 1     | Ordentliche Übertragungen Nachtragskredit | `NACHTRAGSKREDIT11_ANTRAG`, `NACHTRAGSKREDIT11_BESCHLUSS` | |
| N13   | 1     | Dringlicher Nachtragskredit | `NACHTRAGSKREDIT11_ANTRAG`, `NACHTRAGSKREDIT11_BESCHLUSS` ||
| N14   | 1     | Dingliche Übertragungen Nachtragskredit | `NACHTRAGSKREDIT11_ANTRAG`, `NACHTRAGSKREDIT11_BESCHLUSS`
| N15   | 1     | Statistische Mehreinnahmen Nachtragskredit                            | - | nicht im Budget nachgeführt. |
| N21   | 2     | Ordentlicher Nachtragskredit | `NACHTRAGSKREDIT11_ANTRAG`, `NACHTRAGSKREDIT11_BESCHLUSS` | |
| N22   | 2     | Ordentliche Übertragungen Nachtragskredit | `NACHTRAGSKREDIT11_ANTRAG`, `NACHTRAGSKREDIT11_BESCHLUSS` | |
| N23   | 2     | Dringlicher Nachtragskredit | `NACHTRAGSKREDIT11_ANTRAG`, `NACHTRAGSKREDIT11_BESCHLUSS` | |
| N24   | 2     | Dingliche Übertragungen Nachtragskredit| `NACHTRAGSKREDIT11_ANTRAG`, `NACHTRAGSKREDIT11_BESCHLUSS` | |
| N25   | 2     | Statistische Mehreinnahmen Nachtragskredit | - | | Nur statistisch und nicht im Budget nachgeführt. |

* Bis 2008 wurde im Code Z anstatt N verwendet.

NOVEMBER_BRIEF, GEMEINDERAT_BESCHLUSS, NACHTRAGSKREDIT11_ANTRAG, NACHTRAGSKREDIT12_ANTRAG, NACHTRAGSKREDIT13_ANTRAG, NACHTRAGSKREDIT14_ANTRAG, NACHTRAGSKREDIT11_BESCHLUSS, NACHTRAGSKREDIT12_BESCHLUSS, NACHTRAGSKREDIT13_BESCHLUSS, NACHTRAGSKREDIT14_BESCHLUSS, NACHTRAGSKREDIT21_ANTRAG, NACHTRAGSKREDIT22_ANTRAG, NACHTRAGSKREDIT23_ANTRAG, NACHTRAGSKREDIT24_ANTRAG, NACHTRAGSKREDIT21_BESCHLUSS, NACHTRAGSKREDIT22_BESCHLUSS, NACHTRAGSKREDIT23_BESCHLUSS, NACHTRAGSKREDIT24_BESCHLUSS, RECHNUNG, STADTRAT_ANTRAG, N3, N4

## Beispiel-Abfragen

### Departemente suchen

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
        }
    ]
}
```
(Output gekürzt für bessere Übersicht)

### Konten abfragen

**Endpunkt:**

`https://api.stadt-zuerich.ch/rpkk-rs/v1/konten?bezeichnung=<string>&kontoNr=<string>&orgKey=<string>`

* `bezeichnung`: Bezeichnung der Konten. Eine Suche mit Wildcards (*) ist möglich.
* `kontoNr`: KontoNr der Konten. Eine Suche mit Wildcards (*) ist möglich.
* `orgKey`: Key des Departements oder der Institution.

`orgKey` kann mit den [`/departemente`](#departemente-suchen) oder [`/institutionen`](#institutionen-suchen) Endpunkten gefunden werden.


**Alle Konten der Dienstabteilung Statistik Stadt Zürich anzeigen:**

`GET https://api.stadt-zuerich.ch/rpkk-rs/v1/konten?orgKey=1575`

```json
{
    "value": [
        {
            "bezeichnung": "Löhne des Verwaltungs- und Betriebspersonals",
            "id": 7953,
            "institution": {
                "bezeichnung": "Statistik Stadt Zürich",
                "departement": {
                    "bezeichnung": "Präsidialdepartement",
                    "key": "15",
                    "kurzname": "PRD"
                },
                "key": "1575",
                "kurzname": "SSZ"
            },
            "kontoNr": "3010 00 000"
        },
        {
            "bezeichnung": "Erstattung von Lohn des Verwaltungs- und Betriebspersonals",
            "id": 12041,
            "institution": {
                "bezeichnung": "Statistik Stadt Zürich",
                "departement": {
                    "bezeichnung": "Präsidialdepartement",
                    "key": "15",
                    "kurzname": "PRD"
                },
                "key": "1575",
                "kurzname": "SSZ"
            },
            "kontoNr": "3010 00 900"
        },
        {
            "bezeichnung": "Verpflegungszulagen",
            "id": 7954,
            "institution": {
                "bezeichnung": "Statistik Stadt Zürich",
                "departement": {
                    "bezeichnung": "Präsidialdepartement",
                    "key": "15",
                    "kurzname": "PRD"
                },
                "key": "1575",
                "kurzname": "SSZ"
            },
            "kontoNr": "3042 00 000"
        },
        {
            "bezeichnung": "Übrige Zulagen",
            "id": 12042,
            "institution": {
                "bezeichnung": "Statistik Stadt Zürich",
                "departement": {
                    "bezeichnung": "Präsidialdepartement",
                    "key": "15",
                    "kurzname": "PRD"
                },
                "key": "1575",
                "kurzname": "SSZ"
            },
            "kontoNr": "3049 00 000"
        },
        {
            "bezeichnung": "AG-Beiträge AHV, IV, EO, ALV, Verwaltungskosten",
            "id": 7955,
            "institution": {
                "bezeichnung": "Statistik Stadt Zürich",
                "departement": {
                    "bezeichnung": "Präsidialdepartement",
                    "key": "15",
                    "kurzname": "PRD"
                },
                "key": "1575",
                "kurzname": "SSZ"
            },
            "kontoNr": "3050 00 000"
        },
        {
            "bezeichnung": "Erstattung von AG-Beiträgen AHV, IV, EO, ALV, Verwaltungskosten",
            "id": 12043,
            "institution": {
                "bezeichnung": "Statistik Stadt Zürich",
                "departement": {
                    "bezeichnung": "Präsidialdepartement",
                    "key": "15",
                    "kurzname": "PRD"
                },
                "key": "1575",
                "kurzname": "SSZ"
            },
            "kontoNr": "3050 00 900"
        },
        {
            "bezeichnung": "AG-Beiträge an Pensionskassen",
            "id": 7956,
            "institution": {
                "bezeichnung": "Statistik Stadt Zürich",
                "departement": {
                    "bezeichnung": "Präsidialdepartement",
                    "key": "15",
                    "kurzname": "PRD"
                },
                "key": "1575",
                "kurzname": "SSZ"
            },
            "kontoNr": "3052 00 000"
        },
        {
            "bezeichnung": "AG-Beiträge an Unfall- und Personal-Haftpflichtversicherungen",
            "id": 7957,
            "institution": {
                "bezeichnung": "Statistik Stadt Zürich",
                "departement": {
                    "bezeichnung": "Präsidialdepartement",
                    "key": "15",
                    "kurzname": "PRD"
                },
                "key": "1575",
                "kurzname": "SSZ"
            },
            "kontoNr": "3053 00 000"
        }
    ]
}
```
(Output gekürzt für bessere Übersicht)

### Betragsreihen von Konto abfragen

Um eine Betragsreihe abzufragen, benötigt man zuerst eine Konto-ID (siehe [`/konten` Endpunkt](#konten-abfragen)).

**Endpunkt:**

`https://api.stadt-zuerich.ch/rpkk-rs/v1/betragsreihen?kontoId=<long>,<long>&jahre=<integer>,<integer>`

* **`kontoId`**: (Required) kontoIds der Konten. Mehrere IDs komma-separiert angeben z.B. 7957,7956
* `jahre`: (Required) Jahr(e) für welche(s) die Betragreihen gesucht werden. Mehrere Jahre komma-separiert angeben z.B. 2019,2020

`kontoId` kann mit den [`/konten`](#konten-abfragen) Endpunkt gefunden werden (**ACHTUNG**: es geht um das Feld `id` nicht das Feld `kontoNr`).

Hinweise zur Antwort:

* `betragInRappen`: Betrag in Rappen (`wert * 100 = betragInRappen`)
* `wert`: Betrag in CHF (`betragInRappen / 100 = wert`)
* `betragsTyp`: Dies bezeichnet die Phase im Budgetprozess (siehe [Modell](#modell))

**Betragsreihe des Kontos 7953 ("Löhne des Verwaltungs- und Betriebspersonals" von Statistik Stadt Zürich) für das Jahr 2019 anzeigen:**


`GET https://api.integ.stadt-zuerich.ch/rpkk-rs/v1/betragsreihe?jahre=2019&kontoId=7991`

```json
{
    "value": [
        {
            "betraege": [
                {
                    "begruendung": "Anpassung Löhne von div. Mitarbeitenden aufgrund neuer Einstufung und Wiederbesetzung einer Vakanz.\r\n",
                    "betragInRappen": 340800000,
                    "betragsTyp": "GEMEINDERAT_BESCHLUSS",
                    "wert": 3408000.0
                },
                {
                    "begruendung": "Anpassung Löhne von div. Mitarbeitenden aufgrund neuer Einstufung und Wiederbesetzung einer Vakanz.\r\n",
                    "betragInRappen": 340800000,
                    "betragsTyp": "STADTRAT_ANTRAG",
                    "wert": 3408000.0
                },
                {
                    "betragInRappen": 331575280,
                    "betragsTyp": "RECHNUNG",
                    "wert": 3315752.8
                },
                {
                    "betragInRappen": 2000000,
                    "betragsTyp": "N4",
                    "wert": 20000.0
                }
            ],
            "jahr": 2019
        }
    ]
}
```

### 2-stellige Sachkonten abfragen

**Endpunkt:**

`https://api.stadt-zuerich.ch/rpkk-rs/v1/sachkonto2stellig?departement=<integer>&institution=<integer>&jahr=<integer>,<integer>&betragsTyp=<string>`

* **`jahr`**: (Required) Jahr(e) für welche(s) die Sachkonten gesucht werden. Mehrere Jahre komma-separiert angeben z.B. "2019,2020"
* **`betragsTyp`**: (Required) Betragstyp der Sachkonten. Gültige Werte: NOVEMBER_BRIEF, GEMEINDERAT_BESCHLUSS, NACHTRAGSKREDIT11_ANTRAG, NACHTRAGSKREDIT12_ANTRAG, NACHTRAGSKREDIT13_ANTRAG, NACHTRAGSKREDIT14_ANTRAG, NACHTRAGSKREDIT11_BESCHLUSS, NACHTRAGSKREDIT12_BESCHLUSS, NACHTRAGSKREDIT13_BESCHLUSS, NACHTRAGSKREDIT14_BESCHLUSS, NACHTRAGSKREDIT21_ANTRAG, NACHTRAGSKREDIT22_ANTRAG, NACHTRAGSKREDIT23_ANTRAG, NACHTRAGSKREDIT24_ANTRAG, NACHTRAGSKREDIT21_BESCHLUSS, NACHTRAGSKREDIT22_BESCHLUSS, NACHTRAGSKREDIT23_BESCHLUSS, NACHTRAGSKREDIT24_BESCHLUSS, RECHNUNG, STADTRAT_ANTRAG, N3, N4
* `departement`: Departement für welches die Sachkonten gesucht werden sollen. Wert kann mit den [`/departemente`](#departemente-suchen) Endpunkt gefunden werden.
* `institution`: Institution für welche die Sachkonten gesucht werden sollen. Wert kann mit den [`/institutionen`](#institutionen-suchen) Endpunkt gefunden werden.
* `orgKey`: Key des Departements oder der Institution.

`departement` kann mit den [`/departemente`](#departemente-suchen) oder [`/institutionen`](#institutionen-suchen) Endpunkten gefunden werden.

Hinweise zur Antwort:

* `betrag`: Der Betrag ist in CHF angegeben
* `betragsTyp`: Dies bezeichnet die Phase im Budgetprozess (siehe [Modell](#modell))
* `institution`: Wert kann mit den [`/institutionen`](#institutionen-suchen) Endpunkt aufgelöst werden.
* `sachkonto`: In der [CSV-Datei sachkonto_codes.csv](https://github.com/opendatazurich/opendatazurich.github.io/blob/master/rpk-api/sachkonto_codes.csv) sind alle Sachkonten mit ihrer Bezeichnung aufgelistet.

**Alle Sachkonto des Präsidialdepartements für 2019 anzeigen (gemäss Gemeinderatsbeschluss):**



`GET https://api.stadt-zuerich.ch/rpkk-rs/v1/sachkonto2stellig?departement=15&jahr=2019&betragsTyp=GEMEINDERAT_BESCHLUSS`

```json
{
    "value": [
        {
            "betrag": "3356900",
            "betragsTyp": "GEMEINDERAT_BESCHLUSS",
            "institution": "1500",
            "jahr": 2019,
            "sachkonto": "30"
        },
        {
            "betrag": "4610400",
            "betragsTyp": "GEMEINDERAT_BESCHLUSS",
            "institution": "1505",
            "jahr": 2019,
            "sachkonto": "30"
        },
        {
            "betrag": "1224400",
            "betragsTyp": "GEMEINDERAT_BESCHLUSS",
            "institution": "1506",
            "jahr": 2019,
            "sachkonto": "30"
        },
        {
            "betrag": "6871100",
            "betragsTyp": "GEMEINDERAT_BESCHLUSS",
            "institution": "1510",
            "jahr": 2019,
            "sachkonto": "30"
        },
        {
            "betrag": "6454300",
            "betragsTyp": "GEMEINDERAT_BESCHLUSS",
            "institution": "1520",
            "jahr": 2019,
            "sachkonto": "30"
        },
        {
            "betrag": "21134000",
            "betragsTyp": "GEMEINDERAT_BESCHLUSS",
            "institution": "1530",
            "jahr": 2019,
            "sachkonto": "30"
        },
        {
            "betrag": "800200",
            "betragsTyp": "GEMEINDERAT_BESCHLUSS",
            "institution": "1561",
            "jahr": 2019,
            "sachkonto": "30"
        },
        {
            "betrag": "2388500",
            "betragsTyp": "GEMEINDERAT_BESCHLUSS",
            "institution": "1565",
            "jahr": 2019,
            "sachkonto": "30"
        },
        {
            "betrag": "4145700",
            "betragsTyp": "GEMEINDERAT_BESCHLUSS",
            "institution": "1575",
            "jahr": 2019,
            "sachkonto": "30"
        },
        {
            "betrag": "305000",
            "betragsTyp": "GEMEINDERAT_BESCHLUSS",
            "institution": "1500",
            "jahr": 2019,
            "sachkonto": "31"
        },
        {
            "betrag": "2253000",
            "betragsTyp": "GEMEINDERAT_BESCHLUSS",
            "institution": "1505",
            "jahr": 2019,
            "sachkonto": "31"
        },
        {
            "betrag": "356800",
            "betragsTyp": "GEMEINDERAT_BESCHLUSS",
            "institution": "1506",
            "jahr": 2019,
            "sachkonto": "31"
        },
        {
            "betrag": "9545700",
            "betragsTyp": "GEMEINDERAT_BESCHLUSS",
            "institution": "1510",
            "jahr": 2019,
            "sachkonto": "31"
        },
        {
            "betrag": "4920500",
            "betragsTyp": "GEMEINDERAT_BESCHLUSS",
            "institution": "1520",
            "jahr": 2019,
            "sachkonto": "31"
        },
        {
            "betrag": "4371400",
            "betragsTyp": "GEMEINDERAT_BESCHLUSS",
            "institution": "1530",
            "jahr": 2019,
            "sachkonto": "31"
        },
        {
            "betrag": "82000",
            "betragsTyp": "GEMEINDERAT_BESCHLUSS",
            "institution": "1561",
            "jahr": 2019,
            "sachkonto": "31"
        }
    ]
}
```
(Output gekürzt für bessere Übersicht)

## Programmier-Beispiele

Im [Jupyter-Notebook RPK-API-Beispiele.ipynb](https://github.com/opendatazurich/opendatazurich.github.io/blob/master/rpk-api/RPK-API-Beispiele.ipynb) sind einige Python-Beispiele im Umgang mit dem API beschrieben.

Jupyter-Notebook interaktiv im Browser starten: 

[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/opendatazurich/opendatazurich.github.io/master?filepath=rpk-api/RPK-API-Beispiele.ipynb)
[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/opendatazurich/opendatazurich.github.io/blob/master/rpk-api/RPK-API-Beispiele.ipynb)

<img src="https://opendatazurich.github.io/rpk-api/rpk_api_binder.png" height="50%" width="50%" alt="RPK-API Jupyter Notebook in Binder" title="RPK-API Jupyter Notebook in Binder">
