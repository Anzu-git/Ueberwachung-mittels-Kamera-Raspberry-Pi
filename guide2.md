# Produktziel & Produktvorstellung
### Für wen soll unser Produkt welche Verbesserung erreichen?
Antwort: Ziel des Produktes sind Unternehmen in der Sicherheitsbranche die ihr Sicherheitskonzept mittels moderner Methoden wie Local AI & Edge-Computing verbessern möchten.

### Kurzpitch / Link zur Skizze:
Attentio erkennt in Echtzeit, ob sich Personen in einem überwachten Bereich aufhalten – ob Serverraum, Lager, Labor, Baustelle oder Zufahrt. Die KI-Auswertung läuft lokal auf kompakter Edge-Hardware: Videobilder werden nur im Arbeitsspeicher verarbeitet, nicht aufgezeichnet, und es werden keine Personen identifiziert, sondern ausschließlich anonyme Metadaten wie Anzahl, Zeitpunkt und Kamerastatus erfasst. Über die Industrie-Standardschnittstelle OPC UA lassen sich diese Daten direkt in Datenbanken, Leitstände und bestehende Sicherheits- oder Gebäudeleitsysteme einbinden. So wird jeder Zutritt protokolliert, mit Berechtigungen abgeglichen und auf einem Dashboard sichtbar – inklusive Überwachung, ob die Kamera selbst funktioniert. Attentio macht Zutrittsüberwachung datenschutzfreundlich, kostengünstig und überall nachrüstbar.
### Skizze
<img width="2500" height="1514" alt="image" src="https://github.com/user-attachments/assets/8e7d5844-eada-4157-840f-f2e6394aeec2" />

### Problem
Moderne Kamerasysteme sind viel zu teuer und unser Produkt ist als Add-on kompatibel mit verschiedenen Kamerasystemen und bestehenden Lösungen. Somit ist unser Produkt eine kostengünstige Lösung dieser Problematik. Mittels Attentio Kameraüberwachung wird die Abdeckung des Sicherheitskritischen Beriches erweitert und die Integrität geschützter Systeme zusätzlich unterstützt.

#### Fähigkeiten:
| Kennung und erstes Feature | Was soll damit möglich sein? | Beitrag zum Produktziel |
|---|---|---|
| **F1** | Personenerkennung ohne Gesichtserkennung (aus Datenschutzrechtlichen Gründen) | Grundlegende Funktionalität |
| **F2** | Datenbankdokumentation über Middleware (OPCUA) | Dokumentation & Systemintegration |
| **F3** | Dashboardübersicht | Überwachung & Übersichtlichkeit |
| **F4** | Live-Feed der Kamera einsehen | Usability & User Interface |
| **F5** | Einfaches Setup des Add-Ons & Kompatibilität | Aufwandsreduktion für den Kunden |

# Materialbedarf
| Komponente | Benötigt | Vorhanden |
|---|---|---|
| Raspberry Pi | 2x |  1x |
| Raspberry Pi AI HAT+ (Hailo-8L) | 1x | 1x |
| microSD-Karte | 2x | 1x |
| Kamera Sensor | 1x | 0x |


# Stakeholder
| Stakeholder | Interesse oder Bedürfnis | Das wollen wir mit ihnen klären |
|---|---|---|
| **IT-Administrator** | Dokumentation, Open Source, Vorgehen/Verhalten des Systems bei Updates (→ Logging & Dashboard laufen weiter, Live-Kamera temporär pausiert), Mini-Dashboard für den Status der Kameras (live, off, nicht funktionsfähig) | Wie sollen Updates eingespielt werden, und wer wird benachrichtigt, wenn eine Kamera ausfällt? |
| **Projektteam** | Funktionierende, gut dokumentierte Lösung mit wenig Wartungsaufwand | Bis wann stehen der Pi mit Kamerasensor und die Datenbank bereit, und wer übernimmt welche Aufgabe? |
| **Sicherheitstechniker** | Verwaltung der Sicherheitssysteme, Konfiguration & Nutzung dieser | Zugriff auf die Datenbank, das Dashboard usw.? |
| **Geschäftsführer** | Kostengünstig, kein zusätzlicher Aufwand | Welches Budget steht für Hardware und Betrieb zur Verfügung? |
| **Kunde** | Zuverlässiger Schutz des Areals und einfache Bedienung | Was erwarten Sie konkret von der Bedienung des Dashboards? |
| **Wartungspersonal** | Sind befugt, das Areal zu betreten. Ungehinderter Zutritt während der Wartung und keine Speicherung von Gesichtern | Wie sollen sie über die Überwachung informiert werden, und wie werden ihre Wartungszeiten als befugter Zutritt erfasst? |
| **Kamerahersteller** | Ihre Kameras sollen mit möglichst vielen Systemen kompatibel sein | Unterstützen ihre Kameras H.264-Streaming per RTSP? |
| **Sicherheitspersonal (Nutzer)** | Übersichtliche Darstellung mittels Signalfarben bei Erkennung einer Person sowie Priorisierung von Kameras mit Live-Personenerkennung gegenüber Kameras ohne erkannte Person | Wie soll ein Alarm aussehen (Signalfarbe, Ton, Push-Nachricht)? |

## Stakeholderanalyse:
<img width="641" height="443" alt="image" src="https://github.com/user-attachments/assets/eab4b14d-d4b6-49b2-8356-7a8656966a86" />

# Personas
- Markus Becker (Wachmann)
- Michael Schröder (Geschäftsführer des Kundenunternehmens)
- Sarah Klein (IT-Administratorin)
- Thomas Wagner (Sicherheitstechniker)
- Tobias Stein (Wartungspersonal Extern)

# Features aus Nutzersicht überprüfen:
| Feature aus Schritt 3 | Personas / Bedürfnis | Unsere Entscheidung und Begründung |
|---|---|---|
| Personenerkennung ohne Gesichtserkennung |  IT-Administratorin Sarah Klein (Datenschutzbedenken), Wartungspersonal (möchte nicht das ihr Gesicht gepspeichert wird) | ✔️ behalten ☐ ändern ☐ teilen ☐ streichen |
| Datenbankdokumentation über Middleware | IT-Administratorin Sarah Klein (Mangelnde Dokumentation) | ✔️ behalten ☐ ändern ☐ teilen ☐ streichen |
| Dashboardübersicht | IT-Administratorin Sarah Klein (Übersichtlichkeit), Wachmann Markus Becker (Auf einen Blick wichtiges erkennen) | ✔️ behalten ☐ ändern ☐ teilen ☐ streichen |
| Live-Feed der Kamera einsehen | Wachmann Markus Becker (damit Reaktionszeit bei potentiellem Alarm geringer ist) | ✔️ behalten ☐ ändern ☐ teilen ☐ streichen |
| Einfaches Setup des Add-Ons & Kompatibilität | Sicherheitstechniker Thomas Wagner (Einfache Konfiguration), Geschäftsführer (Kein zusätzlicher Aufwand für Mitarbeiter) | ☐ behalten  ✔️ ändern bzw. wurde hinzugefügt ☐ teilen ☐ streichen |

# User Stories

## 1. Personenerkennung ohne Gesichtserkennung

**US-1.1:** Als IT-Administratorin Sarah Klein möchte ich, dass das System Personen erkennt, ohne Gesichtsmerkmale zu verarbeiten, damit meine Datenschutzbedenken ausgeräumt sind.

- Die Erkennung arbeitet ausschließlich mit Personenumrissen oder Bewegungsmerkmalen, nicht mit Gesichtsmerkmalen.
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

- Kritische Ereignisse sind durch Farbe und Symbol hervorgehoben, nicht nur durch Farbe.
- Ereignisse sind nach Priorität und Zeitpunkt sortiert.
- Neue Alarme sind sofort sichtbar, ohne dass das Dashboard neu geladen werden muss.

## 4. Live-Feed der Kamera einsehen

**US-4.1:** Als Wachmann Markus Becker möchte ich den Live-Feed einer Kamera direkt aus dem Dashboard oder einer Alarmmeldung öffnen, damit ich bei einem potenziellen Alarm schneller reagieren kann.

- Der Live-Feed ist mit höchstens einem Klick aus einer Alarmmeldung erreichbar.
- Das Video startet innerhalb von etwa 3 Sekunden.
- Die Verzögerung zwischen Realität und Anzeige ist gering genug, um eine Situation sinnvoll zu beurteilen.

## 5. Einfaches Setup des Add-Ons & Kompatibilität

**US-5.1:** Als Sicherheitstechniker Thomas Wagner möchte ich das Add-On einfach konfigurieren können, damit die Inbetriebnahme schnell und fehlerfrei gelingt.

- Ein geführter Setup-Assistent führt Schritt für Schritt durch die Konfiguration.
- Sinnvolle Standardwerte sind bereits vorbelegt.
- Vor dem Abschluss prüft das System die Kompatibilität mit den vorhandenen Kameras und Systemen und meldet Probleme verständlich.

**US-5.2:** Als Geschäftsführer möchte ich, dass das Add-On ohne zusätzlichen Aufwand für die Mitarbeitenden auskommt, damit der Betriebsablauf nicht gestört wird.

- Im Tagesbetrieb ist keine manuelle Bedienung durch Mitarbeitende nötig.
- Bestehende Abläufe bleiben unverändert.
- Die Installation erfordert keine ungeplanten Ausfallzeiten des Hauptsystems.
