# Produktziel & Produktvorstellung
### Für wen soll unser Produkt welche Verbesserung erreichen?
Antwort: Ziel des Produktes sind Unternehmen in der Sicherheitsbranche die ihr Sicherheitskonzept mittels moderner Methoden wie Local AI & Edge-Computing verbessern möchten.

### Kurzpitch / Link zur Skizze:
Attentio erkennt in Echtzeit, ob sich Personen in einem überwachten Bereich aufhalten – ob Serverraum, Lager, Labor, Baustelle oder Zufahrt. Die KI-Auswertung läuft lokal auf kompakter Edge-Hardware: Videobilder werden nur im Arbeitsspeicher verarbeitet, nicht aufgezeichnet, und es werden keine Personen identifiziert, sondern ausschließlich anonyme Metadaten wie Anzahl, Zeitpunkt und Kamerastatus erfasst. Über die Industrie-Standardschnittstelle OPC UA lassen sich diese Daten direkt in Datenbanken, Leitstände und bestehende Sicherheits- oder Gebäudeleitsysteme einbinden. So wird jeder Zutritt protokolliert, mit Berechtigungen abgeglichen und auf einem Dashboard sichtbar – inklusive Überwachung, ob die Kamera selbst funktioniert. Attentio macht Zutrittsüberwachung datenschutzfreundlich, kostengünstig und überall nachrüstbar.
### Skizze
<img width="2500" height="1514" alt="image" src="https://github.com/user-attachments/assets/8e7d5844-eada-4157-840f-f2e6394aeec2" />

### Was soll unser Produkt ermöglichen?
Moderne Kamerasysteme sind viel zu teuer und unser Produkt ist als Add-on kompatibel mit verschiedenen Kamerasystemen und bestehenden Lösungen. Somit ist unser Produkt eine kostengünstige Lösung dieser Problematik. Mittels Attentio Kameraüberwachung wird die Abdeckung des Sicherheitskritischen Beriches erweitert und die Integrität geschützter Systeme zusätzlich unterstützt.

#### Fähigkeiten:
| Kennung und erstes Feature | Was soll damit möglich sein? | Beitrag zum Produktziel |
|---|---|---|
| **F1** |  Personenerkennung ohne Gesichtserkennung (aus Datenschutzrechtlichen Gründen) | Grundlegende Funktionalität |
| **F2** | Datenbankdokumentation über Middleware (OPCUA) | Dokumentation & Systemintegration |
| **F3** | Dashboardübersicht mittels Node-Red | Überwachung & Übersichtlichkeit |
| **F4** | Live-Feed der Kamera einsehen | Usability & User Interface |

# Materialbedarf
| Gruppe | Projekt/Thema | Komponente | Anzahl |
|---|---|---|
| Raspberry Pi 5 Model B Rev 1.1 Broadcom BCM2712, 4 × Arm Cortex-A76 mit 2,4 GHz, 8 GB LPDDR4X, Gigabit-Ethernet |
| Raspberry Pi AI HAT+ (Hailo-8L) | 13 TOPS INT8 KI-Beschleuniger, PCIe über den FFC-Anschluss des Pi 5, Gerät-/Hailo: ≈ 41 °C unter Last |
| Speicher | microSD-Karte, ≈ 119 GB | Betriebssystem, Docker (Tracker-Image ≈ 10 GB) |
| Kamera |  | Liefert den Kamerastream |
| Raspberry Pi mit Kamerasensor (geplant) | Raspberry Pi mit Kamerasensor, Hardware-H.264-Encoder, Tailscale | Künftige Kamera und Datenbank für die Metadaten |
