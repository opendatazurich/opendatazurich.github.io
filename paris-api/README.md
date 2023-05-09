# Paris-API, Gemeinderat Stadt Zürich (GRZ)

Diese Dokumentation beschreibt die Programmierschnittstelle (API) des Parlamentsinformationssystem (Paris) des Gemeinderats der Stadt Zürich. Über das API lassen sich folgende Entitäten/Indizes abfragen:

* Ablaufschritt
* Abstimmung
* Behoerdenmandat
* Departement
* Dokument
* Files
* Ratspost
* Ratspostfiles
* Geschaeft
* Geschaeftsart
* Geschaeftsuebersicht
* Geschaeft_Person
* Gremiumdetail
* Gremiumstyp
* Gremiumsuebersicht
* Jahr
* Kontakt
* Partei
* Pendentbei
* Referendum
* Sitzung
* Wahlkreis
* Wohnkreis

Diese Dokumentation bietet einen **Schnelleinstieg in das Paris-API**.
Im Kapitel 1 werden pro Entität ein paar typische Beispiels-Abfragen erläutert. 
Im Kapitel 2 wird ein konkretes Programmier-Beispiel mit Python als Jupyter-Notebook zur Verfügung gestellt. Dieses kann ausserdem auch auf Binder aufgerufen werden, wodurch der Code interaktiv im Browser gestartet werden kann.

**Inhaltsverzeichnis**

1. [Beispiel-Abfragen](#beispiel-abfragen)
   1. [Kontakte suchen](#kontakte-suchen)
   3. [Geschäft suchen](#geschäft-suchen)
   4. [Protokolle suchen](#protokolle-suchen)
   5. [Ratspost suchen](#ratspost-suchen)
2. [Programmier-Beispiele](#programmier-beispiele)

## Beispiel-Abfragen

Alle Abfragen nutzen als Basis-URL [`http://www.gemeinderat-zuerich.ch/api/`](http://www.gemeinderat-zuerich.ch/api/), öffnet man über den Browser diese Seite, kann man sich die einzelnen Indizes anschauen und die gültigen Suchfelder anzeigen lassen.

Jeder Index verfügbar auch über ein maschinenlesbares Schema: https://www.gemeinderat-zuerich.ch/api/{{index}}/schema z.B. https://www.gemeinderat-zuerich.ch/api/kontakt/schema

### Kontakte suchen

**Endpunkt:**

`http://www.gemeinderat-zuerich.ch/api/kontakt/searchdetails?q={{cql-query}}&l=de-CH`

Alternativ kann der Index _Behoerdenmandat_ verwendet werden, da dort die Beziehung zwischen Person und Amt hinterlegt ist:

`http://www.gemeinderat-zuerich.ch/api/behoerdenmandat/searchdetails?q={{cql-query}}&l=de-CH`

Das CQL-Query ist eine Abfragesprache, mit der sich die Resultate eingrenzen lassen.
Jeder Index hat definierte Suchfelder, die im CQL-Query verwendet werden können (siehe oben).

**Suche nach Name "Peter" (max. 4 Resultate):**

`GET http://www.gemeinderat-zuerich.ch/api/kontakt/searchdetails?q=NameVorname any "Peter"&l=de-CH&s=1&m=4`

```xml
<SearchDetailResponse xmlns="http://www.cmiag.ch/cdws/searchDetailResponse" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" IDXSEQ="1278036" q="NameVorname any "peter"" l="de-CH" s="1" m="4" numHits="9" indexName="Kontakt">
   <Hit Guid="47360b912d0d4f7b9800ace40f2f861a" SEQ="1126343" Relevance="3.518206">
      <Snippet>Marti <EM>Peter </EM></Snippet>
      <Kontakt xmlns="http://www.cmiag.ch/cdws/Kontakt" xmlns:cmi="http://cmiag.ch" OBJ_GUID="47360b912d0d4f7b9800ace40f2f861a" SEQ="1126343" IDX="Kontakt">
      ...
      </Kontakt>
   </Hit>
   <Hit Guid="172c996d83ae4db7869ca5a5d3e33c4d" SEQ="1126394" Relevance="3.518206">
      <Snippet>Niggli <EM>Peter </EM></Snippet>
      <Kontakt xmlns="http://www.cmiag.ch/cdws/Kontakt" xmlns:cmi="http://cmiag.ch" OBJ_GUID="172c996d83ae4db7869ca5a5d3e33c4d" SEQ="1126394" IDX="Kontakt">
      ...
      </Kontakt>
   </Hit>
   <Hit Guid="f0ce797309714920a2e3f331bc3fd1bd" SEQ="1126404" Relevance="3.518206">
      <Snippet><EM>Peter </EM>Karin </Snippet>
      <Kontakt xmlns="http://www.cmiag.ch/cdws/Kontakt" xmlns:cmi="http://cmiag.ch" OBJ_GUID="f0ce797309714920a2e3f331bc3fd1bd" SEQ="1126404" IDX="Kontakt">
      ...
      </Kontakt>
   </Hit>
   <Hit Guid="a71e6ae9d0854d55b520559ed6f95aec" SEQ="1239623" Relevance="3.518206">
      <Snippet>Anderegg <EM>Peter </EM></Snippet>
      <Kontakt xmlns="http://www.cmiag.ch/cdws/Kontakt" xmlns:cmi="http://cmiag.ch" OBJ_GUID="a71e6ae9d0854d55b520559ed6f95aec" SEQ="1239623" IDX="Kontakt">
      ...
      </Kontakt>
   </Hit>
</SearchDetailResponse>
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

### Geschäft suchen

**Endpunkt**:

`http://www.gemeinderat-zuerich.ch/api/Geschaeft?suchBegriff={{suchBegriff}}&grNummer={{grNummer}}&geschaeftsartId={{geschaeftsartId}}&jahr={{jahr}}&departementId={{departementId}}&personId={{personId}}&parteiId={{parteiId}}&geschaeftAuswahl={{geschaeftAuswahl}}&fraktionId={{fraktionId}}&kommissionEinrId={{kommissionEinrId}}&referendumId={{referendumId}}&ablaufschrittId={{ablaufschrittId}}&kommissionId={{kommissionId}}&pendentBeiId={{pendentBeiId}}&sitzungsNummer={{sitzungsNummer}}&datumVon={{datumVon}}&datumBis={{datumBis}}&beschlussNrGR={{beschlussNrGR}}&includeInactive={{includeInactive}}&orderBy={{orderBy}}&orderDir={{orderDir}}&activePage={{activePage}}&pageSize={{pageSize}}`

Die Wertlisten (`geschaeftsartId`, `kommissionEinrId`, `ablaufschrittId`etc.) können mit dem `/Geschaeft/parameter` Endpunkt gefunden werden.



**Geschäfte von 2016 finden:**

`GET http://www.gemeinderat-zuerich.ch/api/Geschaeft?jahr=2016&activePage=1&pageSize=5`

**ACHTUNG:** Pagination beachten, mit `activePage` kann die Seite, die angefragt wird, angegeben werden. Mit Hilfe von `pageSize` und der im Resultat hinterlegten `AnzahlResultate` können so alle Ergebnisse seitenweise abgefragt werden.

````json
{
    "Geschaefte": [
        {
            "GeschaeftId": "1a5920a8-3491-4343-9a76-5ed08278e288",
            "Geschaeftsjahr": 2016,
            "Geschaeftsnummer": 470,
            "Geschaeftstitel": "Einrichtung einer Tempo-30-Zone an der Furttalstrasse innerhalb des Siedlungsgebiets",
            "Geschaeftsart": "Postulat"
        },
        {
            "GeschaeftId": "ffb6b86c-8ba2-42b4-8b29-014e2388e5e7",
            "Geschaeftsjahr": 2016,
            "Geschaeftsnummer": 469,
            "Geschaeftstitel": "Haltestellen an der Wehntalerstrasse und Haltestelle Oberwiesenstrasse, Ausrüstung mit dem Züri-Bord",
            "Geschaeftsart": "Postulat"
        },
        {
            "GeschaeftId": "89bbe9bc-1e29-4dd9-83fc-aa9e7b0f2e42",
            "Geschaeftsjahr": 2016,
            "Geschaeftsnummer": 468,
            "Geschaeftstitel": "Verlängerung der Haltestelle Glaubtenstrasse stadtauswärts an der Wehntalerstrasse",
            "Geschaeftsart": "Postulat"
        },
        {
            "GeschaeftId": "3d31a1d2-b565-432d-93e8-9f2703e86c20",
            "Geschaeftsjahr": 2016,
            "Geschaeftsnummer": 467,
            "Geschaeftstitel": "Bewilligung von Sonntagsverkäufen, Angaben zu den Verfahren, den rechtlichen Grundlagen und zur Bewilligung von Ethno-Food-Märkten in Quartierzentren sowie zur Sonntagskultur im öffentlichen Leben der Stadt",
            "Geschaeftsart": "Schriftliche Anfrage"
        },
        {
            "GeschaeftId": "0be49c87-98d3-4f6b-96c8-94dc2f2d09bb",
            "Geschaeftsjahr": 2016,
            "Geschaeftsnummer": 466,
            "Geschaeftstitel": "Verhinderung von energetischen Sanierungen aufgrund von Vorgaben der Denkmalpflege, Möglichkeiten für eine Entschädigung bauwilliger Eigentümerinnen und Eigentümer sowie für eine Klage gegen die Stadt",
            "Geschaeftsart": "Schriftliche Anfrage"
        }
    ],
    "AnzahlResultate": 469
}
````



### Protokolle suchen

**Endpunkt:**

`http://www.gemeinderat-zuerich.ch/api/Protokoll?sitzungsNummer={{sitzungsNummer}}&suchBegriff={{suchBegriff}}&datumVon={{datumVon}}&datumBis={{datumBis}}`

Die Felder `datumVon`und `datumBis` müssen im Format TT.MM.JJJJ (z.B. 31.01.2019) abgefüllt werden.

**Protokolle vom Januar 2019 suchen:**

`GET https://www.gemeinderat-zuerich.ch/api/Protokoll?datumVon=01.01.2019&datumBis=31.01.2019`

```json
[
    {
        "Id": 6221,
        "FileName": "GR-Protokoll 20190130.037.pdf"
    },
    {
        "Id": 6223,
        "FileName": "GR-Protokoll 20190130.037 substanziell.pdf"
    },
    {
        "Id": 6218,
        "FileName": "GR-Protokoll 20190130.036.pdf"
    },
    {
        "Id": 6222,
        "FileName": "GR-Protokoll 20190130.036 substanziell.pdf"
    },
    {
        "Id": 6216,
        "FileName": "GR-Protokoll 20190123.035.pdf"
    },
    {
        "Id": 6220,
        "FileName": "GR-Protokoll 20190123.035 substanziell.pdf"
    },
    {
        "Id": 6212,
        "FileName": "GR-Protokoll 20190116.034.pdf"
    },
    {
        "Id": 6217,
        "FileName": "GR-Protokoll 20190116 034 substanziell.pdf"
    },
    {
        "Id": 6208,
        "FileName": "GR-Protokoll 20190109.033.pdf"
    },
    {
        "Id": 6219,
        "FileName": "GR-Protokoll 20190109.033 substanziell.pdf"
    }
]
```

Die Datei kann wie folgt bezogen werden:

`https://www.gemeinderat-zuerich.ch/DocumentLoader.aspx?Typ=protokoll&ID={Id}&FileName={FileName}`

Beispiel: https://www.gemeinderat-zuerich.ch/DocumentLoader.aspx?ID=6218&Typ=protokoll&FileName=GR-Protokoll+20190130.036.pdf

### Ratspost suchen

**Endpunkt:**

`https://www.gemeinderat-zuerich.ch/api/Ratspost?datumVon={{datumVon}}&datumBis={{datumBis}}`

Die Felder `datumVon`und `datumBis` müssen im Format TT.MM.JJJJ (z.B. 31.01.2019) abgefüllt werden.

**Ratspost vom 1. Quartal 2019 suchen:**

`GET https://www.gemeinderat-zuerich.ch/api/Ratspost?datumVon=01.01.2019&datumBis=31.03.2019`

```json
[
    {
        "Id": "6fbede90-4660-43d0-9429-ff836807b05b",
        "FileName": "Ratspostversand20190328.html"
    },
    {
        "Id": "107af3a0-f981-4208-8e69-4cdbd397fafc",
        "FileName": "Ratspostversand20190321.html"
    },
    {
        "Id": "424cd2ff-97d0-4255-a953-02fe7c15df56",
        "FileName": "Ratspostversand20190314.html"
    },
    {
        "Id": "479c2ba2-4124-4271-bc19-b0d7e01ec8ea",
        "FileName": "Ratspostversand20190307.html"
    },
    {
        "Id": "19ba52dc-b604-4412-9553-87c3722995e1",
        "FileName": "Ratspostversand20190228.html"
    },
    {
        "Id": "de6fd305-836a-4836-b41f-f9101bbc70bf",
        "FileName": "Ratspostversand20190221.html"
    },
    {
        "Id": "1c72707d-00b5-4b11-8213-8dc81d35c109",
        "FileName": "Ratspostversand20190131.html"
    },
    {
        "Id": "194ce486-eed7-4d92-8947-3c0767d0e2d6",
        "FileName": "Ratspostversand20190124.html"
    },
    {
        "Id": "86d8c3b4-24b7-4406-a45f-4ecf03aa11e3",
        "FileName": "Ratspostversand20190117.html"
    },
    {
        "Id": "3b0204f0-f9a4-4fc9-86cc-e66bbfd03a52",
        "FileName": "Ratspostversand20190110.html"
    },
    {
        "Id": "a84fb659-dd54-43df-8857-4142a3a2aaf7",
        "FileName": "Ratspostversand20190103.html"
    }
]
```

Die Datei kann wie folgt bezogen werden:

`https://www.gemeinderat-zuerich.ch/sitzungen/ratspost/?Id={Id}`

Beispiel: https://www.gemeinderat-zuerich.ch/sitzungen/ratspost/?Id=3b0204f0-f9a4-4fc9-86cc-e66bbfd03a52

## Programmier-Beispiele

Hinweis für **Python**: wir empfehlen für den Zugriff auf die Schnittstelle den API-Wrapper [**goifer**](https://pypi.org/project/goifer/) zu verwenden.
Dies vereinfacht die Zugriffe auf die einzelnen Entitäten sehr.

Im [Jupyter-Notebook RIS-API-Beispiele.ipynb](https://github.com/opendatazurich/opendatazurich.github.io/blob/master/paris-api/Paris-API-Beispiele.ipynb) sind einige Python-Beispiele im Umgang mit dem API beschrieben.

Jupyter-Notebook interaktiv im Browser starten: 

[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/opendatazurich/opendatazurich.github.io/master?filepath=paris-api/Paris-API-Beispiele.ipynb)

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/opendatazurich/opendatazurich.github.io/blob/master/paris-api/Paris-API-Beispiele.ipynb)
