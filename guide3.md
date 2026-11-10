# Definition of Done

| Unsere verbindlichen Qualitätskriterien | So prüfen und belegen wir sie |
|---|---|
| Funktionale Dockeranbindung & erfolgreiche Installation der Container | Fehlerfreier Start & Beinhaltung der Datenbank usw. + Kontrolle durch vier-Augen-Prinzip |
| Tailscale Mesh verbunden | beide Raspberry Pis sind funktionsfähig & verbunden |
| Kameras funktionell & verbunden | Live-Bildübertragung läuft |
| Aufrufbares & Funktionsfähiges Dashboard mit integrierten Kameras | Prüfung durch Projektmitglieder |
| Sauberes Logging | Kontrolle durch Testlogging |
| Datenbank ist konfiguriert & erreichbar | Überprüfung der Datentypen & Datenbankaufbau |

# User Stories

## 1. Personenerkennung ohne Gesichtserkennung

**US-1.1:** Als IT-Administratorin Sarah Klein möchte ich, dass das System Personen erkennt, ohne Gesichtsmerkmale zu verarbeiten, damit meine Datenschutzbedenken ausgeräumt sind.

- Die Erkennung arbeitet ausschließlich mit Personenumrissen, nicht mit Gesichtsmerkmalen.
- Es werden keine Gesichtsvektoren, Templates oder Gesichtsausschnitte gespeichert.
- Die Verarbeitung ist in der Dokumentation nachvollziehbar beschrieben.

**US-1.2:** Als Wartungspersonal möchte ich, dass mein Gesicht nicht gespeichert wird, damit ich bei meiner Arbeit im Gebäude nicht identifizierbar erfasst werde.

- Ereignisse enthalten keine Angaben, die eine Person identifizieren.
- Gesichter werden weder im Live-Feed noch in Aufzeichnungen dauerhaft gespeichert.
- Das System unterscheidet nicht zwischen bekannten und unbekannten Personen.

## 2. Datenbankdokumentation über Middleware

**US-2.1:** Als IT-Administratorin Sarah Klein möchte ich eine vollständige Dokumentation der Datenbankstruktur über die Middleware abrufen können, damit ich die Integration nachvollziehen und warten kann.

- Die Dokumentation enthält Tabellen, Felder, Datentypen und Beziehungen.
- Sie entspricht der jeweils installierten Version.
- Der Zugriff ist auf berechtigte Rollen beschränkt.

## 3. Dashboardübersicht

**US-3.1:** Als IT-Administratorin Sarah Klein möchte ich eine übersichtliche Dashboard-Ansicht mit dem Status von Kameras, Ereignissen und Systemen, damit ich den Betrieb schnell überblicken kann.

- Der Systemstatus ist ohne Scrollen auf einem Bildschirm sichtbar.
- Kameras und Systeme zeigen Online-, Offline- und Fehlerstatus an.

**US-3.2:** Als Wachmann Markus Becker möchte ich wichtige Ereignisse auf einen Blick erkennen, damit ich nicht erst durch Details suchen muss.

- Kritische Ereignisse sind durch Farbe und Symbol hervorgehoben.
- Ereignisse sind nach Priorität und Zeitpunkt sortiert.
- Neue Alarme sind sofort sichtbar, ohne dass das Dashboard neu geladen werden muss.

## 4. Live-Feed der Kamera einsehen

**US-4.1:** Als Wachmann Markus Becker möchte ich den Live-Feed einer Kamera direkt aus dem Dashboard oder einer Alarmmeldung öffnen, damit ich bei einem potenziellen Alarm schneller reagieren kann.

- Der Live-Feed ist mit höchstens einem Klick aus einer Alarmmeldung erreichbar.
- Das Video startet innerhalb von etwa 15 Sekunden.
- Die Verzögerung zwischen Realität und Anzeige ist gering genug, um eine Situation sinnvoll zu beurteilen.

## 5. Einfaches Setup des Add-Ons & Kompatibilität

**US-5.1:** Als Sicherheitstechniker Thomas Wagner möchte ich das Add-On einfach konfigurieren können, damit die Inbetriebnahme schnell und fehlerfrei gelingt.

- Der Zugriff und Konfiguration ist über eine Weboberfläche ermöglicht.
- Sinnvolle Standardwerte sind bereits vorbelegt.
- Vor dem Abschluss prüft das System die Kompatibilität mit den vorhandenen Kameras und Systemen und meldet Probleme verständlich.

**US-5.2:** Als Geschäftsführer möchte ich, dass das Add-On ohne zusätzlichen Aufwand für die Mitarbeitenden auskommt, damit der Betriebsablauf nicht gestört wird.

