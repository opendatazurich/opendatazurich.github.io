# RIS-API, Gemeinderat Stadt Zürich (GRZ)

Diese Dokumentation beschreibt die Programmierschnittstelle (API) des Ratshausinformationssystems (RIS) des Gemeinderats der Stadt Zürich. Über das API lassen sich folgende Entitäten abfragen:

* Mitglieder
* Geschäfte
* Protokolle
* Ratspost

Das komplette API ist als OpenAPI Spezifikation (Swagger) verfügbar. Dort sind alle Endpunkte und deren Parameter im Detail erklärt.

Zudem gibt es eine Postman Collection, um das API zu testen: [![Run in Postman](https://run.pstmn.io/button.svg)](https://app.getpostman.com/run-collection/a7f8d0d2370ad8a4be67)

## Beispiele

### Mitglieder suchen

URL: `http://www.gemeinderat-zuerich.ch/api/Mitglieder?name={{name}}&parteiId={{parteiId}}&fraktionId={{fraktionId}}&wahlkreisId={{wahlkreisId}}&wohnkreisId={{wohnkreisId}}&kommissionId={{kommissionId}}&includeInactive={{includeInactive}}&orderBy={{orderBy}}&orderDir={{orderDir}}`



