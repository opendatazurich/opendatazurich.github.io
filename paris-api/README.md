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

Hier ein vereinfachtes konzeptuelles Datenmodell des Parlamentsinformationssystem:

![Paris Datenmodell](<https://opendatazurich.github.io/ris-api/pics/Paris_Datenmodell.png>)

Diese Dokumentation bietet einen **Schnelleinstieg in das Paris-API**.
Im Kapitel 1 werden pro Entität ein paar typische Beispiels-Abfragen erläutert. 
Im Kapitel 2 wird ein konkretes Programmier-Beispiel mit Python als Jupyter-Notebook zur Verfügung gestellt. Dieses kann ausserdem auch auf Binder aufgerufen werden, wodurch der Code interaktiv im Browser gestartet werden kann.

Eine Übersicht über alle Funktionen der API mit Beispielen bietet auch die [**PDF-Anleitung der Paris-API**](https://data.stadt-zuerich.ch/dataset/parlamentsdienste_paris_api/download/Anleitung_Paris_API_Gemeinderat_Zuerich.pdf).

**Inhaltsverzeichnis**

1. [Beispiel-Abfragen](#beispiel-abfragen)
   1. [Personen suchen](#personen-suchen)
   3. [Geschäft suchen](#geschäft-suchen)
   4. [Protokolle suchen](#protokolle-suchen)
   5. [Ratspost suchen](#ratspost-suchen)
2. [Programmier-Beispiele](#programmier-beispiele)

## Beispiel-Abfragen

Alle Abfragen nutzen als Basis-URL [`http://www.gemeinderat-zuerich.ch/api/`](http://www.gemeinderat-zuerich.ch/api/), öffnet man über den Browser diese Seite, kann man sich die einzelnen Indizes anschauen und die gültigen Suchfelder anzeigen lassen.

Jeder Index verfügbar auch über ein maschinenlesbares Schema: https://www.gemeinderat-zuerich.ch/api/{{index}}/schema z.B. https://www.gemeinderat-zuerich.ch/api/kontakt/schema

Das API verwender die Abfragesprache CQL, mit der sich die Resultate eingrenzen und Sortieren lassen.
Jeder Index hat definierte Suchfelder, die im CQL-Query verwendet werden können.

Alle Indizes nutzen sogenannte GUIDs als eindeutige Identifier.
Mit dem Suchfeld `ID` kann nach diesen GUIDs gesucht werden.

### Personen suchen

**Endpunkt:**

`http://www.gemeinderat-zuerich.ch/api/kontakt/searchdetails?q={{cql-query}}&l=de-CH`

Verfügbare Suchfelder:
- ID 
- Fraktion 
- Jahrgang 
- AktivesRatsmitglied 
- Geschlecht 
- Kommission 
- Name 
- NameVorname 
- Vorname 
- Partei 
- Wahlkreis 
- Wohnkreis

Alternativ kann der Index _Behoerdenmandat_ verwendet werden, da dort die Beziehung zwischen Person und Amt hinterlegt ist:

`http://www.gemeinderat-zuerich.ch/api/behoerdenmandat/searchdetails?q={{cql-query}}&l=de-CH`

Verfügbare Suchfelder:
- Name
- Gremium
- Partei
- Wohnkreis
- Wahlkreis
- Dauer


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

**Suche nach aktiven Mitgliedern der GPK:**

`GET http://www.gemeinderat-zuerich.ch/api/behoerdenmandat/searchdetails?q=gremium any "GPK" AND Dauer_end > "9999-12-31 00:00:00" &l=de-CH&s=1&m=100`

```xml
<SearchDetailResponse xmlns="http://www.cmiag.ch/cdws/searchDetailResponse" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" IDXSEQ="1278032" q="gremium any "GPK" AND Dauer_end > "9999-12-31 00:00:00" " l="de-CH" s="1" m="1000" numHits="12" indexName="Behoerdenmandat">
   <Hit Guid="0097f0e3f991481fb690ec212cf17987" SEQ="1147798" Relevance="2.668081">
      <Snippet><EM>GPK (</EM>Geschäftsprüfungskommission) <EM>GPK </EM>0bab680addc94a9e83cd184947ee46ce D050DF43 5336 47C2 8BF0 11F0BAB7758A </Snippet>
      <Behordenmandat xmlns="http://www.cmiag.ch/cdws/Behoerdenmandat" xmlns:cmi="http://cmiag.ch" OBJ_GUID="0097f0e3f991481fb690ec212cf17987" SEQ="1147798" IDX="Behoerdenmandat">
         <Name>Bucher</Name>
         <Vorname>Gregor</Vorname>
         <KontaktGuid>eff3cfde35254c71b2370a93b26bf7fc</KontaktGuid>
         <AltsystemID>4084208D-6380-4D59-A426-01231472D25B</AltsystemID>
         <Dauer>
            <Start xsi:nil="false">2009-02-01T00:00:00.000</Start>
            <End xsi:nil="false">9999-12-31T23:59:59.000</End>
            <Text>01.02.2009 -</Text>
         </Dauer>
         <Gremium>GPK (Geschäftsprüfungskommission)</Gremium>
         <GremiumGuid>0bab680addc94a9e83cd184947ee46ce</GremiumGuid>
         <Gremiumstyp>Kommission</Gremiumstyp>
         <Partei/>
         <ParteiGuid/>
         <Titel/>
         <Wahlkreis>6</Wahlkreis>
         <WahlkreisOrder xsi:nil="true"/>
         <Wohnkreis>6</Wohnkreis>
         <Funktion>Sekretariat</Funktion>
         <Sitz xsi:nil="true"/>
      </Behordenmandat>
   </Hit>
   <Hit Guid="2cac0e895ead4ecdbb6499aa07458f6a" SEQ="1194816" Relevance="2.668081">
   ...
   </Hit>
   <Hit Guid="78b2bfc84dd8439082cf53d3d6da1356" SEQ="1195241" Relevance="2.668081">
   ...
   </Hit>
   <Hit Guid="df003fc284494792bf429308af7e3a9f" SEQ="1195595" Relevance="2.668081">
   ...
   </Hit>
   <Hit Guid="6e0e7057496e47d6852971bc796d9bfa" SEQ="1198434" Relevance="2.668081">
   ...
   </Hit>
   <Hit Guid="3f829a2225cb499ba7d323b5c76c6b0e" SEQ="1204353" Relevance="2.668081">
   ...
   </Hit>
   <Hit Guid="0e4b163c1087471ca37c513d67491c86" SEQ="1205251" Relevance="2.668081">
   ...
   </Hit>
   <Hit Guid="c2d5f14ded71423ea4ea9ac40b22c9bb" SEQ="1205345" Relevance="2.668081">
   ...
   </Hit>
   <Hit Guid="11cc45a8335647158585bbfe083fc3c2" SEQ="1210940" Relevance="2.668081">
   ...
   </Hit>
   <Hit Guid="75dfa941191d4a10bfd0a80a141271d5" SEQ="1220611" Relevance="2.668081">
   ...
   </Hit>
   <Hit Guid="b6d2a4d8ac5d478894f1061e47422690" SEQ="1240574" Relevance="2.668081">
   ...
   </Hit>
   <Hit Guid="b0ed5064c656490ea9ee146c380bf727" SEQ="1259556" Relevance="2.668081">
   ...
   </Hit>
</SearchDetailResponse>
```

### Geschäft suchen

**Endpunkt**:

`http://www.gemeinderat-zuerich.ch/api/geschaeft/searchdetails?q={{cql-query}}&l=de-CH`

Verfügbare Suchfelder:
- ID 
- GRNr
- Titel
- Geschaeftsart
- Ablaufschritt
- Beginn
- Departement
- VorberatendeKommission
- Dokument
- FristBis
- NameVorname
- Partei
- PendentBei
- Eingereicht
- Volltext
- Verweise
- Dringlich

**Geschäfte von 2016 finden:**

`GET http://www.gemeinderat-zuerich.ch/api/geschaeft/searchdetails?q=beginn_start > "2016-01-01 00:00:00" AND beginn_start < "2017-01-01 00:00:00" sortBy beginn_start/sort.ascending&l=de-CH&s=1&m=100`

**ACHTUNG:** Pagination beachten, mit `s` kann die Nummer des ersten zurückgegebenen Treffers angegeben werden. Mit Hilfe von `m` die Maximale Anzahl Treffer.
Mit diesen beiden Parameterns lässt sich eine Pagination implementieren.
Dies ist Sache der abfragenden Drittapplikation.

````xml
<SearchDetailResponse xmlns="http://www.cmiag.ch/cdws/searchDetailResponse" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" IDXSEQ="1285451" q="beginn_start > "2016-01-01 00:00:00" AND beginn_start < "2017-01-01 00:00:00" sortBy beginn_start/sort.ascending" l="de-CH" s="1" m="100" numHits="4040" indexName="Geschaeft">
	<Hit Guid="75183f1744fb4a9c8464c70cc8a0f9f5" SEQ="788242" Relevance="1">
		<Snippet/>
		<Geschaeft xmlns="http://www.cmiag.ch/cdws/Geschaeft" xmlns:cmi="http://cmiag.ch" OBJ_GUID="75183f1744fb4a9c8464c70cc8a0f9f5" SEQ="788242" IDX="Geschaeft">
			<GRNr>2016/11</GRNr>
			<GRNrSort/>
			<Titel>Traminfrastruktur beim Albert-Näf-Platz, betriebliche Nutzung und Notwendigkeit der Gleisverbindung Ohm-/Schaffhauserstrasse sowie Unterhalts- und Investitionskosten für die Gleisanlage</Titel>
			<Geschaeftsart>Schriftliche Anfrage</Geschaeftsart>
			<Geschaeftsstatus>Abgeschlossen</Geschaeftsstatus>
			<Dringlich xsi:nil="false">false</Dringlich>
			<VorberatendeKommission/>
			<WeitereVorberatendeKommissionen/>
			<FederfuehrendesDepartement>
			...
			</FederfuehrendesDepartement>
			<MitbeteiligteDepartemente/>
			<Beginn>
				<Start xsi:nil="false">2016-01-06T00:00:00.000</Start>
				<End xsi:nil="false">2016-01-07T00:00:00.000</End>
				<Text>06.01.2016</Text>
			</Beginn>
			<PendentBei/>
			<Referendum>Kein Referendum</Referendum>
			<Ablaufschritte>
			...
			</Ablaufschritte>
			<Erstunterzeichner>
				<KontaktGremium OBJ_GUID="4e2b9a0c0fe3422ebea010dd250ad373">
				<Name>Hans Jörg Käppeli</Name>
				<Partei>SP</Partei>
				<IstGremium xsi:nil="false">false</IstGremium>
				</KontaktGremium>
			</Erstunterzeichner>
			<Mitunterzeichner/>
			<AnzahlMitunterzeichnende xsi:nil="true"/>
			<VerweisZu/>
			<VerweisVon/>
			<Traktanden/>
		</Geschaeft>
	</Hit>
	<Hit Guid="2aa163cc0f404d1fb0a589ab4c5db763" SEQ="820481" Relevance="1">
		<Snippet/>
		<Geschaeft xmlns="http://www.cmiag.ch/cdws/Geschaeft" xmlns:cmi="http://cmiag.ch" OBJ_GUID="2aa163cc0f404d1fb0a589ab4c5db763" SEQ="820481" IDX="Geschaeft">
		...
		</Geschaeft>
	</Hit>
	<Hit Guid="064919aa8e67493782188cc8ef5e0e94" SEQ="867593" Relevance="1">
		<Snippet/>
		<Geschaeft xmlns="http://www.cmiag.ch/cdws/Geschaeft" xmlns:cmi="http://cmiag.ch" OBJ_GUID="064919aa8e67493782188cc8ef5e0e94" SEQ="867593" IDX="Geschaeft">
		...
		</Geschaeft>
	</Hit>
	...
	...
</SearchDetailResponse>
````

### Protokolle suchen

Ein Sitzungsprotokoll ist einer Sitzung angehängt, und kann von dort bezogen werden

**Endpunkt:**

`https://www.gemeinderat-zuerich.ch/api/sitzung/searchdetails/?q={{cql-query}}&l=de-CH`

Verfügbare Suchfelder:
- Sitzungsdatum_start
- Sitzungsdatum_end
- Titel
- PersonWortmeldung
- PersonWortmeldungPartei


**Protokolle vom Januar 2019 suchen:**

`GET https://www.gemeinderat-zuerich.ch/api/sitzung/searchdetails/?q=sitzungsdatum_start > "2019-01-01 00:00:00" and sitzungsdatum_start < "2019-01-31 23:59:59" sortBy sitzungsdatum_start/sort.ascending&l=de-CH&m=5`

```xml
<SearchDetailResponse xmlns="http://www.cmiag.ch/cdws/searchDetailResponse" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" IDXSEQ="1286201" q="sitzungsdatum_start > "2019-01-01 00:00:00" and sitzungsdatum_start < "2019-01-31 23:59:59"" l="de-CH" s="1" m="5" numHits="218" indexName="Sitzung">
    <Hit Guid="701a6efe54024040b27b2901246816b1" SEQ="1274826" Relevance="1">
    <Snippet/>
    <Sitzung xmlns="http://www.cmiag.ch/cdws/Sitzung" xmlns:cmi="http://cmiag.ch" OBJ_GUID="701a6efe54024040b27b2901246816b1" SEQ="1274826" IDX="Sitzung">
        <Titel>33. Sitzung</Titel>
        <Datum>
            <Start xsi:nil="false">2019-01-09T00:00:00.000</Start>
            <End xsi:nil="false">2019-01-10T00:00:00.000</End>
            <Text>09.01.2019</Text>
        </Datum>
        <Beginn/>
        <Ende/>
        <EndeNachMitternacht/>
        <VideoURL/>
        <Traktanden>
        ...
        </Traktanden>
        <Dokumente>
            <Dokument OBJ_GUID="5b806f9d41ba47efbd180aaccaee33e9">
            ...
            </Dokument>
            <Dokument OBJ_GUID="f729b69dd1724dd1bf10b1400babd2fa">
            ...
            </Dokument>
            <Dokument OBJ_GUID="9cf56e38b2db4bb98baffef27ab88ab6">
                <Titel>GR-Protokoll 20190109.033 substanziell</Titel>
                <File ID="9cf56e38b2db4bb98baffef27ab88ab6-332" FileName="GR-Protokoll 20190109.033 substanziell">
                <Version Nr="1">
                <Rendition Extension="pdf" Ansicht="PDF"/>
                </Version>
                </File>
                <Kategorie>Protokoll</Kategorie>
            </Dokument>
        </Dokumente>
        <Sitzungsaufzeichnung>
        ...
        </Sitzungsaufzeichnung>
    </Sitzung>
    </Hit>
    <Hit Guid="14f5477698b94df6a924ae4046d8b8ec" SEQ="1274708" Relevance="1">
    ...
    </Hit>
    <Hit Guid="3766e307d269442a9390c4c832b7a6e8" SEQ="1274952" Relevance="1">
    ...
    </Hit>
    <Hit Guid="af70361f65b344f68182feb904abe0e6" SEQ="1244238" Relevance="1">
    ...
    </Hit>
    <Hit Guid="87a5eaadd21445e889a90fbfad369492" SEQ="1256795" Relevance="1">
    ...
    </Hit>
</SearchDetailResponse>
```

Bei jeder Sitzung sind Dokumente abgehängt (z.B. Protokoll), welche dann wiefolgt bezogen werden können:

`https://www.gemeinderat-zuerich.ch/dokumente/{{guid}}`

Beispiel von oben, die ID vom `File` muss verwendet werden (nicht vom Dokument!):

```xml
<Dokument OBJ_GUID="9cf56e38b2db4bb98baffef27ab88ab6">
    <Titel>GR-Protokoll 20190109.033 substanziell</Titel>
    <File ID="9cf56e38b2db4bb98baffef27ab88ab6-332" FileName="GR-Protokoll 20190109.033 substanziell">
    <Version Nr="1">
    <Rendition Extension="pdf" Ansicht="PDF"/>
    </Version>
    </File>
    <Kategorie>Protokoll</Kategorie>
</Dokument>
```

Dokument: https://www.gemeinderat-zuerich.ch/dokumente/9cf56e38b2db4bb98baffef27ab88ab6-332

### Ratspost suchen

**Endpunkt:**

`https://www.gemeinderat-zuerich.ch/api/ratspost/searchdetails/?q={{cql-query}}&l=de-CH`

Verfügbare Suchfelder:
- Datum_Start
- Datum_End
- Dokument

**Ratspost vom 1. Quartal 2023 suchen:**

`GET https://www.gemeinderat-zuerich.ch/api/ratspost/searchdetails/?q=Datum_Start > "2023-01-01 00:00:00" and Datum_Start < "2023-01-04 00:00:00" sortBy Datum_Start/sort.ascending&l=de-CH`

```xml
<SearchDetailResponse xmlns="http://www.cmiag.ch/cdws/searchDetailResponse" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" IDXSEQ="1062008" q="2023-01-01 00:00:00" and Datum_Start < "2023-01-04 00:00:00" sortBy Datum_Start/sort.ascending" l="de-CH" s="1" m="5" numHits="1" indexName="Ratspost">
    <Hit Guid="4446c8ba780b4edbaa3df66c4c5b261f" SEQ="1062008" Relevance="1">
        <Snippet/>
        <Ratspost xmlns="http://www.cmiag.ch/cdws/Ratspost" xmlns:cmi="http://cmiag.ch" OBJ_GUID="4446c8ba780b4edbaa3df66c4c5b261f" SEQ="1062008" IDX="Ratspost">
            <Datum>
                <Start xsi:nil="false">2023-05-04T00:00:00.000</Start>
                <End xsi:nil="false">2023-05-05T00:00:00.000</End>
                <Text>04.05.2023</Text>
            </Datum>
            <Einleitungstext/>
            <NaechsteSitzungDatum>2023-05-10T00:00:00.000</NaechsteSitzungDatum>
            <NaechsteSitzungGuid>614cfb372af649d89520fe3827052898</NaechsteSitzungGuid>
            <Dokumente>
            ...
            </Dokumente>
            <Positionen>
                <Position OBJ_GUID="9e50848fa91341398dfe0160432ec9e8">
                    <Kapitel>Neue Weisungen</Kapitel>
                    <KapitelSortierung xsi:nil="false">60</KapitelSortierung>
                    <GeschaeftGuid>f28b1ad5a7634c4f80f765a60e8020c9</GeschaeftGuid>
                    <GRNr>2023/173</GRNr>
                    <Titel>**Kultur, Konzeptförderung Tanz und Theater, Genehmigung 6-jährige Konzeptförderbeiträge 2024–2029, Aufteilung Rahmenkredit** Weisung, 05.04.2023</Titel>
                    <Dokumente>
                    ...
                    </Dokumente>
                </Position>
                <Position OBJ_GUID="d71c7f42c3f84f1e848c284c4d771375">
                ...
                </Position>
                <Position OBJ_GUID="1908f6ceaa204bad8ef538ac3974fbc6">
                ...
                </Position>
                <Position OBJ_GUID="4a28a929c0fc42dd950586c641650bbe">
                ...
                </Position>
                <Position OBJ_GUID="92ab56f05c16484a9a4a94cc211a4ef9">
                ...
                ...
                ...
            </Positionen>
        </Ratspost>
    </Hit>
</SearchDetailResponse>
```

Die Datei kann wie folgt bezogen werden:

`https://www.gemeinderat-zuerich.ch/sitzungen/ratspost/?Id={Id}`

Beispiel: https://www.gemeinderat-zuerich.ch/sitzungen/ratspost/?Id=3b0204f0-f9a4-4fc9-86cc-e66bbfd03a52

## Programmier-Beispiele

Hinweis für **Python**: wir empfehlen für den Zugriff auf die Schnittstelle den API-Wrapper [**goifer**](https://pypi.org/project/goifer/) zu verwenden.
Dies vereinfacht die Zugriffe auf die einzelnen Entitäten sehr.

Im [Jupyter-Notebook Paris-API-Beispiele.ipynb](https://github.com/opendatazurich/opendatazurich.github.io/blob/master/paris-api/Paris-API-Beispiele.ipynb) sind einige Python-Beispiele im Umgang mit dem API beschrieben.
