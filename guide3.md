# Definition of Done

| Unsere verbindlichen Qualitätskriterien | So prüfen und belegen wir sie |
|---|---|
|System funktionell| Es werden Keine Fehler oder Warnungen gemeldet und alle Services sind erreichbar|
|System getestet| Anwendbare Szenarien wurden abgebildet|
|Dokumentation vollständig| Geänderte Aspekte und Hinweise ausreichend dokumentiert|
|User Story erfolgreich abgebildet| Akzeptanzkriterien erfüllt|

# User Stories

## 1. Personenerkennung ohne Gesichtserkennung

|---| User Story 1 |
|---|---|
| **User Story** | *„US-1.1: Als IT-Administratorin Sarah Klein möchte ich, dass das System Personen erkennt, ohne Gesichtsmerkmale zu verarbeiten, damit meine Datenschutzbedenken ausgeräumt sind.“* |
| **Akzeptanzkriterien** | • Die Erkennung arbeitet ausschließlich mit Personenumrissen, nicht mit Gesichtsmerkmalen. • Es werden keine Gesichtsvektoren, Templates oder Gesichtsausschnitte gespeichert • Gesichter werden weder im Live-Feed noch in Aufzeichnungen dauerhaft gespeichert. • Das System unterscheidet nicht zwischen bekannten und unbekannten Personen. |

---

## 2. Datenbankdokumentation über Middleware

| | User Story 1 |
|---|---|
| **User Story** | *„US-2.1: Als IT-Administratorin Sarah Klein möchte ich eine vollständige Dokumentation der Datenbankstruktur über die Middleware abrufen können, damit ich die Integration nachvollziehen und warten kann.“* |
| **Akzeptanzkriterien** | • Die Dokumentation enthält Tabellen, Felder, Datentypen und Beziehungen. • Sie entspricht der jeweils installierten Version. • Der Zugriff ist auf berechtigte Rollen beschränkt. |

---

## 3. Dashboardübersicht

| | User Story 1 | User Story 2 |
|---|---|---|
| **User Story** | *„US-3.1: Als IT-Administratorin Sarah Klein möchte ich eine übersichtliche Dashboard-Ansicht mit dem Status von Kameras, Ereignissen und Systemen, damit ich den Betrieb schnell überblicken kann.“* | *„US-3.2: Als Wachmann Markus Becker möchte ich wichtige Ereignisse auf einen Blick erkennen, damit ich nicht erst durch Details suchen muss.“* |
| **Akzeptanzkriterien** | • Der Systemstatus ist ohne Scrollen auf einem Bildschirm sichtbar. • Kameras und Systeme zeigen Online-, Offline- und Fehlerstatus an. | • Kritische Ereignisse sind durch Farbe und Symbol hervorgehoben. • Ereignisse sind nach Priorität und Zeitpunkt sortiert. • Neue Alarme sind sofort sichtbar, ohne dass das Dashboard neu geladen werden muss. |

---

## 4. Live-Feed der Kamera einsehen

| | User Story 1 |
|---|---|
| **User Story** | *„US-4.1: Als Wachmann Markus Becker möchte ich den Live-Feed einer Kamera direkt aus dem Dashboard oder einer Alarmmeldung öffnen, damit ich bei einem potenziellen Alarm schneller reagieren kann.“* |
| **Akzeptanzkriterien** | • Der Live-Feed ist mit höchstens einem Klick aus einer Alarmmeldung erreichbar. • Das Video startet innerhalb von etwa 15 Sekunden. • Die Verzögerung zwischen Realität und Anzeige ist gering genug, um eine Situation sinnvoll zu beurteilen. |

---

## 5. Einfaches Setup des Add-Ons & Kompatibilität

| | User Story 1 | User Story 2 |
|---|---|---|
| **User Story** | *„US-5.1: Als Sicherheitstechniker Thomas Wagner möchte ich das Add-On einfach konfigurieren können, damit die Inbetriebnahme schnell und fehlerfrei gelingt.“* | *„US-5.2: Als Geschäftsführer möchte ich, dass das Add-On ohne zusätzlichen Aufwand für die Mitarbeitenden auskommt, damit der Betriebsablauf nicht gestört wird.“* |
| **Akzeptanzkriterien** | • Der Zugriff und die Konfiguration sind über eine Weboberfläche möglich. • Sinnvolle Standardwerte sind bereits vorbelegt. • Vor dem Abschluss prüft das System die Kompatibilität mit den vorhandenen Kameras und Systemen und meldet Probleme verständlich. | Im Original sind für diese Story keine Akzeptanzkriterien angegeben. |


# Szenario bzw. Beispielzenario inkl. Firma
Die Metallbau Kessler GmbH in Oldenburg hat einen Eingangsbereich mit Hofeinfahrt, eine Werkhalle, ein Gefahrstofflager für Lacke und Lösungsmittel sowie einen Flur zu den Büros und zum Serverschrank. Vier Kameras decken Hof und Eingang, die Werkhalle, das Gefahrstofflager und den Flur ab, während Büro, Pausenraum und Umkleiden kameralos bleiben.

**Phase 1:** Inbetriebnahme durch Thomas Wagner
Thomas Wagner richtet das Add-On bei der Metallbau Kessler GmbH in Oldenburg an einem Dienstagmorgen über die Weboberfläche ein. Die Standardwerte sind bereits vorbelegt. Er muss nur noch die Alarmschwellen und die vier Kamerazonen prüfen: Hof und Eingang, Werkhalle, Gefahrstofflager sowie den Flur zu den Büros und zum Serverschrank. Vor dem Abschluss meldet das System, dass die Kamera für Hof und Eingang eine ältere Firmware hat, die nicht vollständig kompatibel ist. Die Meldung ist verständlich formuliert und nennt die nötige Aktualisierung. Thomas aktualisiert die Firmware und schließt die Inbetriebnahme ab, ohne den Betrieb zu unterbrechen. Peter Lang bekommt davon nichts mit, weil die Arbeiten außerhalb der Hauptschicht stattfinden. Genau das ist sein Kriterium aus US-5.2.

**Phase 2:** Datenschutz-Prüfung durch Sarah Klein
Sarah Klein prüft die Konfiguration, bevor sie die Freigabe erteilt. In der Dokumentation zur Verarbeitung stellt sie fest, dass das System nur Personenumrisse auswertet. Gesichtsvektoren, Templates oder Gesichtsausschnitte gibt es laut Dokumentation nicht. Außerdem kontrolliert sie die Datenbankdokumentation über die Middleware. Dort findet sie für die installierte Version die Tabellen, Felder, Datentypen und Beziehungen. Im Rechtemanagement überprüft sie, dass der Zugriff darauf auf ihre Rolle beschränkt ist. Damit erfüllt das Add-On ihre Anforderungen aus US-1.1 und US-2.1.

**Phase 3:** Alltag im Schichtbetrieb
Markus Becker beginnt seine Nachtschicht und öffnet das Dashboard. Der Systemstatus ist ohne Scrollen sichtbar. Für jede der vier Kameras wird angezeigt, ob sie online oder offline ist oder einen Fehler hat. Um 2:14 Uhr meldet die Kamera im Gefahrstofflager für Lacke und Lösungsmittel eine Bewegung. Der Alarm erscheint rot markiert ganz oben in der Liste, ohne dass Markus die Seite neu laden muss. Mit einem Klick auf die Alarmmeldung gelangt er zum Live-Feed, und das Video startet nach etwa 8 Sekunden. Markus sieht, dass es nur Jan Vogel ist, der Wartungstechniker, der eine Leiter trägt. Jan wird dabei nicht als identifizierbare Person gespeichert, denn das System speichert keine Gesichter und unterscheidet nicht zwischen bekannten und unbekannten Personen. Markus schließt den Alarm als unkritisch ab.
Am nächsten Morgen arbeitet Jan Vogel an den Deckenlampen. Er weiß, dass er auf der Kamera erkennbar ist, aber nicht identifizierbar erfasst wird. Die Ereignisse enthalten keine Angaben, die ihn als Person ausweisen. Deshalb muss er sich weder abmelden noch Sondergenehmigungen einholen.
Zwei Stellen habe ich bewusst offen gelassen, weil sie weder im Original noch im Szenario stehen: in welchem Bereich Jan an den Deckenlampen arbeitet und welche Rollen Thomas, Sarah und Peter bei Kessler haben.
