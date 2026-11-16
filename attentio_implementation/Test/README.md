# Attentio – Testaufbau (Analyse-Knoten)

Code des aktuellen Testaufbaus: Ein Notebook mit Webcam sendet einen Videostream an einen
**Raspberry Pi 5 mit Hailo-8L AI HAT+**. Dieser erkennt und verfolgt Personen, stellt ein
annotiertes Live-Bild bereit und liefert anonyme Metadaten (Anzahl, Kamerastatus, Zeitstempel)
per **OPC UA**. Im Zielsystem ersetzt ein Raspberry Pi mit Kamerasensor das Notebook und
übernimmt Datenbank und Dashboard.

```
Kamera-Host ──RTSP /source──▶ MediaMTX ──▶ Tracker (Hailo-8L + ByteTrack) ──▶ MediaMTX /annotated
                                              │
                                              └─▶ people.json (tmpfs) ──▶ OPC-UA-Server (1 Hz)
```

## Struktur

| Pfad | Inhalt |
|---|---|
| `app/track.py` | Einstiegspunkt: Live-Modus (RTSP) und Datei-Modus, Leerlaufverhalten, Encoder |
| `app/detectors.py` | Hailo-Detektor (Letterbox, Kacheln, NMS), ByteTrack-Anbindung, Haltezeit |
| `app/state.py` | Schreibt den Zustand (`people.json`) atomar für den OPC-UA-Server |
| `app/bytetrack_custom.yaml` | Tracker-Schwellen |
| `opcua/server.py` | OPC-UA-Server (asyncua) mit drei Variablen |
| `docker-compose.yml` | MediaMTX, Tracker, OPC-UA-Server, Batch-Modus |
| `Dockerfile.hailo`, `Dockerfile.opcua` | Images für Tracker und OPC-UA-Server |
| `mediamtx.yml` | RTSP-Server-Konfiguration (Passwörter als Platzhalter) |

## Voraussetzungen

- Raspberry Pi 5 mit Raspberry Pi OS / Debian 13 (trixie), Hailo-8L AI HAT+
- `sudo apt install hailo-all` (HailoRT 4.23), Gerät `/dev/hailo0` vorhanden
- Docker mit Docker Compose
- Optional: Tailscale, um den Knoten nur im privaten Netz erreichbar zu machen

## Einrichtung

```bash
# 1. Modell bereitstellen (wird mit hailo-all installiert, nicht im Repository)
cp /usr/share/hailo-models/yolov5s_personface_h8l.hef app/model.hef

# 2. Zugangsdaten setzen
cp .env.example .env                  # BIND_IP und TRACKER_PASS eintragen
openssl rand -hex 16                  # je ein Passwort für publisher und tracker erzeugen
# in mediamtx.yml CHANGE_ME_PUBLISHER / CHANGE_ME_TRACKER ersetzen
# (tracker-Passwort = TRACKER_PASS in .env)

# 3. Bauen und starten
docker compose build
docker compose up -d
docker compose logs -f tracker-live-hailo
```

Ohne Stream wartet der Tracker im Leerlauf (≈ 25 MiB, Hailo frei) und lädt das Modell erst,
wenn ein Bild ankommt. Nach 120 s ohne Stream beendet er sich sauber und wird von Docker neu
gestartet – das ist beabsichtigt.

## Kamera einspeisen (Notebook, ffmpeg unter Windows)

```bash
# Kameras und Modi anzeigen
ffmpeg -hide_banner -list_devices true -f dshow -i dummy
ffmpeg -hide_banner -list_options true -f dshow -i video="KAMERANAME"

# Stream senden
ffmpeg -f dshow -video_size 1280x720 -framerate 30 -i video="KAMERANAME" \
  -c:v libx264 -preset ultrafast -tune zerolatency \
  -b:v 2500k -maxrate 2500k -bufsize 2500k -g 30 \
  -f rtsp -rtsp_transport tcp rtsp://publisher:<passwort>@<BIND_IP>:8554/source
```

## Ansehen (geringe Latenz)

```bash
ffplay -fflags nobuffer -flags low_delay -framedrop -threads 1 -rtsp_transport tcp rtsp://<BIND_IP>:8554/annotated
vlc --network-caching=200 rtsp://<BIND_IP>:8554/annotated   # zusätzlich FFmpeg-Threads = 1 einstellen
```

Gemessen im LAN: ≈ 80 ms Kamera-bis-Bildschirm auf `/source`, ≈ 100 ms auf `/annotated`.

## OPC UA

Endpunkt `opc.tcp://<BIND_IP>:4840/camera-tracker/`, Namensraum `urn:camera-tracker` (Index 2),
anonym, nur lesend, Aktualisierung 1 Hz.

| NodeId | Typ | Bedeutung |
|---|---|---|
| `ns=2;s=PeopleTracking.PersonCount` | Int32 | Aktuell erkannte Personen (Erkennung = PersonCount > 0) |
| `ns=2;s=PeopleTracking.Timestamp` | DateTime (UTC) | Beobachtungszeitpunkt; ändert sich jede Sekunde |
| `ns=2;s=PeopleTracking.CameraConnected` | Boolean | `false`, wenn kein Stream anliegt (Anzahl dann 0) |

Der Server ist ohne Transportsicherheit (Modus None) und daher nur für private Netze gedacht.

## Erkennungsoptionen

Zusätzliche Optionen sind eingebaut, aber standardmäßig aus, da sie im Vergleichstest mehr
Personen fanden, die Anzahl aber unruhiger machten: `--tiles=2`, `--nms-iou=0.7`,
`--hef=/app/yolov8s_h8l.hef` (aus `/usr/share/hailo-models/` kopieren). Haltezeit gegen
Flackern: `--hold` (Standard 1 s).

## Datenschutz

Bilder werden nur im Arbeitsspeicher verarbeitet und nicht gespeichert; es werden keine
Personen identifiziert. Ausgegeben werden nur das annotierte Live-Bild und anonyme Metadaten.

## Lizenzhinweise

Abhängigkeiten u. a.: ultralytics (**AGPL-3.0**, genutzt für ByteTrack), FFmpeg mit x264
(**GPL**), asyncua (LGPL-3.0), OpenCV (Apache 2.0), MediaMTX (MIT), HailoRT (MIT/GPL-2.0).
Die Hailo-Firmware und die Modelle (`.hef`) sind nicht Teil dieses Repositorys.
