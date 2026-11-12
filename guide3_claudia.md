# Definition of Done

Die Definition of Done (DoD) gilt für **jede** User Story. Eine Story ist erst „Done“, wenn alle Kriterien erfüllt und belegt sind.

| Kategorie | Kriterium (Was muss erfüllt sein?) | Prüfung / Nachweis |
|---|---|---|
| **1. Fachliche Fertigstellung** | Alle Akzeptanzkriterien der User Story sind erfüllt. | Jedes Kriterium wurde einzeln geprüft und im Board abgehakt. |
| | Die Funktion ist end-to-end nutzbar (Kamera → Raspberry Pi → OPC UA → Datenbank → Dashboard). | Vorführung des kompletten Ablaufs am Testaufbau. |
| **2. Entwicklung & Code-Qualität** | Der Code ist vollständig, lauffähig und einheitlich formatiert. | Start ohne Fehler oder Warnungen im Log. |
| | Ein zweites Teammitglied hat den Code geprüft (Vier-Augen-Prinzip). | Review-Kommentar bzw. Freigabe im Repository. |
| | Der Stand ist im Repository (Git) eingecheckt. | Commit mit aussagekräftiger Nachricht vorhanden. |
| **3. Test & Qualitätssicherung** | Die zutreffenden Szenarien wurden getestet (z. B. Person erkannt / keine Person / Kamera offline). | Testprotokoll mit Ergebnis je Szenario. |
| | Alle Dienste (Erkennung, OPC-UA-Server, Datenbank, Dashboard) sind erreichbar und arbeiten zusammen. | Statusanzeige im Dashboard bzw. Funktionstest. |
| | Es sind keine kritischen Fehler offen. | Keine offenen Fehler-Tickets mit Priorität „kritisch“. |
| **4. Dokumentation** | Geänderte technische Aspekte (Datenbankstruktur, OPC-UA-Knoten, Konfiguration) sind dokumentiert. | Dokumentation im Repository ist aktualisiert. |
| | Hinweise für Anwender (Einrichtung, Bedienung) sind ergänzt. | Abschnitt in der Anwenderdokumentation vorhanden. |
| **5. Sicherheit & Datenschutz** | Es werden keine Bilddaten, Gesichtsmerkmale oder personenbezogenen Daten gespeichert (DSGVO). | Prüfung der Datenbank und des Speichers: nur Zeitstempel, Personenanzahl, Erkennungs- und Kamerastatus. |
| | Zugriffe sind über Rollen geschützt. | Test mit einem nicht berechtigten Benutzer schlägt fehl. |
| **6. Lieferung** | Die Funktion läuft auf dem Testaufbau (Raspberry Pi mit AI HAT+). | Vorführung am Gerät. |
| **7. Abnahme** | Der Product Owner hat die Story im Sprint Review geprüft und abgenommen. | Abnahme vermerkt, Story im Board auf „Done“. |

---

# User Stories

**Produktziel:** Attentio ermöglicht Unternehmen der Sicherheitsbranche eine datenschutzfreundliche, kostengünstige und nachrüstbare Personenerkennung mit Local AI und Edge-Computing.

| Feature | ID | User Story | Akzeptanzkriterien |
|---|---|---|---|
| **F1 Personenerkennung ohne Gesichtserkennung** | US-1.1 | Als IT-Administratorin Sarah Klein möchte ich, dass das System Personen erkennt, ohne Gesichtsmerkmale zu verarbeiten, damit meine Datenschutzbedenken ausgeräumt sind. | • Die Erkennung arbeitet ausschließlich mit Personenumrissen, nicht mit Gesichtsmerkmalen.<br>• Es werden keine Gesichtsvektoren, Templates oder Gesichtsausschnitte gespeichert.<br>• Die Verarbeitung ist in der Dokumentation nachvollziehbar beschrieben. |
| | US-1.2 | Als externer Wartungstechniker Tobias Stein möchte ich, dass mein Gesicht nicht gespeichert wird, damit ich bei meiner Arbeit im Gebäude nicht identifizierbar erfasst werde. | • Ereignisse enthalten keine Angaben, die eine Person identifizieren.<br>• Gesichter werden weder im Live-Feed noch in Aufzeichnungen dauerhaft gespeichert.<br>• Das System unterscheidet nicht zwischen bekannten und unbekannten Personen. |
| **F2 Datenbankdokumentation über Middleware (OPC UA)** | US-2.1 | Als IT-Administratorin Sarah Klein möchte ich eine vollständige Dokumentation der Datenbankstruktur über die Middleware abrufen können, damit ich die Integration nachvollziehen und warten kann. | • Die Dokumentation enthält Tabellen, Felder, Datentypen und Beziehungen.<br>• Sie entspricht der jeweils installierten Version.<br>• Der Zugriff ist auf berechtigte Rollen beschränkt. |
| **F3 Dashboardübersicht** | US-3.1 | Als IT-Administratorin Sarah Klein möchte ich eine übersichtliche Dashboard-Ansicht mit dem Status von Kameras, Ereignissen und Systemen, damit ich den Betrieb schnell überblicken kann. | • Der Systemstatus ist ohne Scrollen auf einem Bildschirm sichtbar.<br>• Kameras und Systeme zeigen Online-, Offline- und Fehlerstatus an. |
| | US-3.2 | Als Wachmann Markus Becker möchte ich wichtige Ereignisse auf einen Blick erkennen, damit ich nicht erst durch Details suchen muss. | • Kritische Ereignisse sind durch Farbe und Symbol hervorgehoben.<br>• Ereignisse sind nach Priorität und Zeitpunkt sortiert.<br>• Neue Alarme erscheinen automatisch, ohne dass das Dashboard neu geladen werden muss. |
| **F4 Live-Feed der Kamera einsehen** | US-4.1 | Als Wachmann Markus Becker möchte ich den Live-Feed einer Kamera direkt aus dem Dashboard oder einer Alarmmeldung öffnen, damit ich bei einem potenziellen Alarm schneller reagieren kann. | • Der Live-Feed ist mit höchstens einem Klick aus dem Dashboard oder einer Alarmmeldung erreichbar.<br>• Das Video startet innerhalb von höchstens 15 Sekunden.<br>• Die Verzögerung zwischen Realität und Anzeige beträgt höchstens ___ Sekunden *(Zielwert im Team festlegen)*. |
| **F5 Einfaches Setup des Add-Ons & Kompatibilität** | US-5.1 | Als Sicherheitstechniker Thomas Wagner möchte ich das Add-On einfach konfigurieren können, damit die Inbetriebnahme schnell und fehlerfrei gelingt. | • Zugriff und Konfiguration sind über eine Weboberfläche möglich.<br>• Sinnvolle Standardwerte sind bereits vorbelegt.<br>• Vor dem Abschluss prüft das System die Kompatibilität mit den vorhandenen Kameras und Systemen und meldet Probleme verständlich. |
| | US-5.2 | Als Geschäftsführer Michael Schröder möchte ich, dass das Add-On ohne zusätzlichen Aufwand für die Mitarbeitenden auskommt, damit der Betriebsablauf nicht gestört wird. | • Im Tagesbetrieb ist keine manuelle Bedienung durch Mitarbeitende nötig.<br>• Bestehende Abläufe bleiben unverändert.<br>• Die Installation erfordert keine ungeplanten Ausfallzeiten des Hauptsystems. |

---

# Beispielszenario: Metallbau Kessler GmbH

Die Metallbau Kessler GmbH in Oldenburg rüstet ihre bestehende Videoüberwachung mit Attentio nach. Das Gelände umfasst einen Eingangsbereich mit Hofeinfahrt, eine Werkhalle, ein Gefahrstofflager für Lacke und Lösungsmittel sowie einen Flur zu den Büros und zum Serverschrank. Vier vorhandene Kameras decken Hof und Eingang, Werkhalle, Gefahrstofflager und Flur ab. Büro, Pausenraum und Umkleiden bleiben kameralos.

**Phase 1: Inbetriebnahme durch Thomas Wagner (US-5.1, US-5.2)**
Sicherheitstechniker Thomas Wagner richtet Attentio an einem Dienstagmorgen über die Weboberfläche ein. Die Standardwerte sind bereits vorbelegt, er prüft nur die Alarmschwellen und die vier Kamerazonen. Vor dem Abschluss meldet das System, dass die Kamera für Hof und Eingang eine ältere Firmware hat, die nicht vollständig kompatibel ist. Die Meldung ist verständlich formuliert und nennt die nötige Aktualisierung. Thomas aktualisiert die Firmware und schließt die Einrichtung ab. Da die Arbeiten außerhalb der Hauptschicht stattfinden und das bestehende System weiterläuft, bemerkt die Belegschaft davon nichts. Geschäftsführer Michael Schröder muss keine Abläufe ändern.

**Phase 2: Datenschutz-Prüfung durch Sarah Klein (US-1.1, US-2.1)**
IT-Administratorin Sarah Klein prüft die Konfiguration, bevor sie die Freigabe erteilt. Laut Dokumentation wertet das System nur Personenumrisse aus. Bilder werden nur im Arbeitsspeicher verarbeitet, gespeichert werden ausschließlich Zeitstempel, Personenanzahl und Kamerastatus. Über die Middleware (OPC UA) ruft sie die Datenbankdokumentation ab und findet für die installierte Version Tabellen, Felder, Datentypen und Beziehungen. Im Rechtemanagement stellt sie sicher, dass nur berechtigte Rollen darauf zugreifen können.

**Phase 3: Nachtschicht mit Markus Becker (US-3.1, US-3.2, US-4.1, US-1.2)**
Wachmann Markus Becker beginnt seine Nachtschicht und öffnet das Dashboard. Der Status aller vier Kameras (online, offline, Fehler) ist ohne Scrollen sichtbar. Um 2:14 Uhr erkennt die Kamera im Gefahrstofflager eine Person. Der Alarm erscheint rot markiert mit Warnsymbol ganz oben in der Liste, ohne dass Markus die Seite neu laden muss. Mit einem Klick öffnet er den Live-Feed, das Video startet nach etwa 8 Sekunden. Er sieht einen Wartungstechniker mit einer Leiter, dessen Einsatz für diese Nacht angekündigt war, und schließt den Alarm als unkritisch ab.

Der externe Wartungstechniker Tobias Stein wird dabei nicht identifizierbar erfasst: Das System speichert keine Gesichter, unterscheidet nicht zwischen bekannten und unbekannten Personen, und das Ereignis enthält nur Zeitpunkt, Kamera und Personenanzahl. Tobias muss sich deshalb weder abmelden noch eine Sondergenehmigung einholen.
