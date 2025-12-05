# Pixel Canvas - Interaktives Pixel-Zeichenprogramm

Ein Python-basiertes interaktives Pixel-Canvas-Programm, das im Browser läuft. Benutzer können auf einzelne Pixel klicken und deren Farbe ändern. Änderungen werden in Echtzeit an alle verbundenen Clients übertragen.

## 🎨 Funktionen

- **Automatisches Browser-Öffnen**: Das Programm öffnet automatisch einen neuen Browser-Tab
- **Interaktive Pixel-Canvas**: Klicke auf jeden Pixel, um seine Farbe zu ändern
- **Echtzeit-Updates**: Änderungen werden sofort an alle verbundenen Clients übertragen
- **Farbauswahl**: Integrierter Color Picker zur Auswahl der gewünschten Farbe
- **Koordinaten-Anzeige**: Zeigt die aktuelle Position des Mauszeigers auf der Canvas
- **Responsive Design**: Moderne, ansprechende Benutzeroberfläche

## 🚀 Installation

### Voraussetzungen

- Python 3.8 oder höher
- pip (Python Package Manager)

### Installation der Abhängigkeiten

```bash
# Repository klonen oder herunterladen
git clone https://github.com/Heese-Gymnasium/place.git
cd place

# Virtuelle Umgebung erstellen (empfohlen)
python -m venv venv
source venv/bin/activate  # Linux/Mac
# oder: venv\Scripts\activate  # Windows

# Abhängigkeiten installieren
pip install -r requirements.txt
```

## 💻 Verwendung

```bash
# Anwendung starten
python app.py
```

Nach dem Start:
1. Ein Browser-Tab öffnet sich automatisch mit der Adresse `http://127.0.0.1:5000`
2. Wähle eine Farbe mit dem Color Picker in der Werkzeugleiste
3. Klicke auf einen beliebigen Pixel, um seine Farbe zu ändern
4. Die Änderungen werden in Echtzeit angezeigt

Zum Beenden: `Strg+C` im Terminal drücken.

## 📁 Projektstruktur

```
place/
├── app.py              # Haupt-Server-Anwendung (Flask + SocketIO)
├── requirements.txt    # Python-Abhängigkeiten
├── templates/
│   └── index.html      # Frontend-Template (HTML/CSS/JavaScript)
└── README.md           # Diese Dokumentation
```

## 🔧 Konfiguration

Die Canvas-Größe und andere Parameter können in `app.py` angepasst werden:

```python
CANVAS_WIDTH = 50   # Breite in Pixeln
CANVAS_HEIGHT = 50  # Höhe in Pixeln
DEFAULT_COLOR = "#FFFFFF"  # Standard-Hintergrundfarbe
HOST = "127.0.0.1"  # Server-Adresse
PORT = 5000         # Server-Port
```

## 🔌 Technologie

- **Backend**: Python 3, Flask, Flask-SocketIO
- **Frontend**: HTML5 Canvas, JavaScript, Socket.IO
- **Echtzeit-Kommunikation**: WebSockets via Socket.IO
- **Styling**: CSS3 mit modernem Design

## 🗄️ Datenbankanbindung (Zukunft)

Die aktuelle Implementierung speichert Pixel-Daten im Arbeitsspeicher. Für eine persistente Speicherung kann die `pixel_data` Variable durch eine Datenbankanbindung ersetzt werden. Die Datenstruktur ist bereits darauf vorbereitet:

```python
# Beispiel: Laden aus einer Datenbank
def lade_pixel_aus_datenbank():
    # TODO: Datenbankverbindung implementieren
    # z.B. mit SQLite, PostgreSQL oder MongoDB
    pass
```

## 📝 Lizenz

MIT License
