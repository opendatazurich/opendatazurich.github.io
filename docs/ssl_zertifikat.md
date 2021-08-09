\newpage

SSL/TLS Zertifikat
==================

Aktuell gibt es zwei Zertifikate die für OGD relevant sind:

- Integrationsumgebung: https://data.integ.stadt-zuerich.ch
- Produktionsumgebung: https://data.stadt-zuerich.ch

Für die Integrationsumgebung kommt ein self-signed Zertifikat der OIZ zum Zug, die zugehörigen CA-Zertifikate sind auf http://pki.stzh.ch/ publiziert.
Die Root-CA Zertifikate der PKI der Stadt Zürich sind auf den städtischen Geräte hinterlegt und daher können die Seite stadtintern aufgerufen werden und es werden keine Zertifikatsfehler angezeigt.
Stadtextern erscheint jedoch eine Warnmeldung, und zum anzeigen der Webseite muss entweder manuell das CA-Zertifikat installiert werden oder eine Ausnahme im Browser hinterlegt werden.

Für die produktive Umgebung (welche für die Öffentlichkeit gedacht ist) kommt ein "offizielles" Zertifikat zum Einsatz (aktuell signiert von QuoVadis).
Die QuoVadis CA ist bei den meisten Betriebsystemen und Browsers als vertrauenswürdig hinterlegt, so dass mit keinen Warnungen zu rechnen ist.

Beide Zertifikate sind jeweils für **1 Jahr** gültig und müssen rechtzeitig via Service Desk bestellt und auf dem Server ausgetauscht werden.

## Bestellung

Da die Zertifikate ein Ablaufdatum haben, ist es wichtig genügend früh eine Bestellung für ein Zertifikat auszulösen (ca. 1 Monat vor Ablauf sollte genügen).
Das Ablaufdatum lässt sich sehr einfach ermitteln mit Hilfe des Browsers.

1. Auf die gewünschte Seite navigieren, z.B. https://data.stadt-zuerich.ch
2. In der Adresszeile auf das Schloss-Icon klicken
3. Auf «Verbindung ist sicher» und «Weitere Informationen» klicken (je nach Browser unterschiedlich)
4. Auf «Zertifikat anzeigen» klicken

Beim angezeigten Zertifikat ist dann das Gültigsdatum drin.

**Achtung:** Zertifikate haben immer ein Start- und ein Endgültigkeitsdatum. Achtet bei der Bestellung darauf, dass das neue Zertifikat ca. 1-2 Wochen vor dem Ablaufdatum des alten Zerfikats liegt.
So kann die Umstellung genau in dieser Übergangszeit erfolgen, ohne dass es zu Zertifikatsfehlern bei den Benutzern kommt.
Wird das Zertifikat zu früh oder spät gewechselt, wird dem Benutzer eine Fehlermeldung angezeigt.

Zertifikate können via Service Desk bestellt werden, dabei muss der Typ gewählt werden (PKI Stadt Zürich oder QuoVadis) und für welche Adressen das Zertifikat gültig ist (data.stadt-zuerich.ch oder data.integ.stadt-zuerich.ch).

## Zerifikate auf dem Server austauschen

Die Zertifikate werden üblicherweise als PFX-Datei geliefert, aus dieser Datei lassen sich der Public- und der Private Key der Zertifikats extrahieren.
Um die Dateien zu extrahieren benötigt man `openssl`, welches auf dem Server bereits installiert ist.

## Abschluss

Nach dem Austausch lohnt es sich die neue Konfiguration [via SSLLabs testen](https://www.ssllabs.com/ssltest/) zu lassen.
Dort werden dann u.a. die Zertifikatsketten geprüft.
