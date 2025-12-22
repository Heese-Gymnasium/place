"""
Pixel Canvas Anwendung - Ein interaktives Pixel-Zeichenprogramm

Dieses Python-Programm erstellt einen Webserver, der eine interaktive Pixel-Canvas
im Browser anzeigt. Benutzer können auf einzelne Pixel klicken und deren Farbe ändern.
Die Änderungen werden durch regelmäßiges Polling an alle verbundenen Clients übertragen.

Hauptfunktionen:
- Öffnet automatisch einen neuen Browser-Tab mit der Canvas
- Zeigt eine Datenstruktur als Pixel-Grid an (später aus Datenbank ladbar)
- Unterstützt Updates durch HTTP-Polling
- Ermöglicht Farbauswahl für jeden Pixel

Autor: GitHub Copilot
Datum: Dezember 2024
"""

# Standard-Bibliotheken importieren
import webbrowser  # Zum automatischen Öffnen des Browsers
import threading   # Für parallele Ausführung (Browser öffnen ohne Server zu blockieren)
import os          # Für Betriebssystem-Funktionen

# Flask für Web-Server
from flask import Flask, render_template, jsonify, request, make_response

# ============================================================================
# KONSTANTEN - Definieren die grundlegenden Parameter der Canvas
# ============================================================================

# Größe der Canvas in Pixeln (Breite x Höhe)
# Diese Werte können angepasst werden, um die Canvas-Größe zu ändern
CANVAS_WIDTH = 50   # Breite in Pixeln
CANVAS_HEIGHT = 50  # Höhe in Pixeln

# Standard-Hintergrundfarbe für neue Pixel (Weiß im Hex-Format)
DEFAULT_COLOR = "#FFFFFF"

# Server-Konfiguration
HOST = "127.0.0.1"  # Localhost - nur lokaler Zugriff
PORT = 5000         # Port für den Webserver

# ============================================================================
# DATENSTRUKTUR - Speichert den aktuellen Zustand aller Pixel
# ============================================================================

# Die Pixel-Daten werden als zweidimensionale Liste (Matrix) gespeichert
# Jeder Eintrag enthält den Hex-Farbwert des entsprechenden Pixels
# Format: pixel_data[y][x] = "#RRGGBB"
# Diese Struktur kann später durch eine Datenbankanbindung ersetzt werden

def initialisiere_pixel_daten():
    """
    Erstellt und initialisiert die Pixel-Datenstruktur.
    
    Erzeugt eine 2D-Liste mit der definierten Größe, wobei jeder
    Pixel mit der Standard-Hintergrundfarbe (Weiß) initialisiert wird.
    
    Returns:
        list: 2D-Liste mit Farbwerten für jeden Pixel
    
    Zeitkomplexität: O(CANVAS_WIDTH * CANVAS_HEIGHT)
    """
    # List Comprehension für effiziente Erstellung der 2D-Matrix
    # Äußere Liste: Zeilen (y-Koordinate)
    # Innere Liste: Spalten (x-Koordinate)
    return [[DEFAULT_COLOR for _ in range(CANVAS_WIDTH)] for _ in range(CANVAS_HEIGHT)]

# Globale Variable für die Pixel-Daten
# In einer produktiven Anwendung würde dies durch eine Datenbank ersetzt
pixel_data = initialisiere_pixel_daten()

# ============================================================================
# FLASK-APP KONFIGURATION
# ============================================================================

# Flask-Anwendung erstellen
# template_folder: Ordner für HTML-Templates
app = Flask(__name__, template_folder="templates")

# DISABLE JINJA2 CACHING FOR DEVELOPMENT
app.jinja_env.cache = {}
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

# Geheimer Schlüssel für Session-Management und Sicherheit
# In Produktion sollte dieser aus einer Umgebungsvariable geladen werden
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "pixel-canvas-secret-key-2024")

# ============================================================================
# HTTP-ROUTEN - Definieren die erreichbaren Webseiten und API-Endpunkte
# ============================================================================

@app.route("/")
def index():
    """
    Hauptseite der Anwendung.
    
    Rendert das HTML-Template mit der interaktiven Pixel-Canvas.
    Übergibt die Canvas-Dimensionen an das Template.
    
    Returns:
        str: Gerendertes HTML der Hauptseite
    """
    response = make_response(render_template(
        "index.html",
        width=CANVAS_WIDTH,
        height=CANVAS_HEIGHT
    ))
    # Disable caching for development
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

@app.route("/admin")
def admin():
    """
    Admin-Seite der Anwendung.
    
    Rendert das HTML-Template für Administratoren mit erweiterten Funktionen.
    Übergibt die Canvas-Dimensionen an das Template.
    
    Returns:
        str: Gerendertes HTML der Admin-Seite
    """
    response = make_response(render_template(
        "admin.html",
        width=CANVAS_WIDTH,
        height=CANVAS_HEIGHT
    ))
    # Disable caching for development
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

@app.route("/api/canvas")
def get_canvas():
    """
    API-Endpunkt zum Abrufen des aktuellen Canvas-Zustands.
    
    Gibt alle Pixel-Daten als JSON zurück. Wird beim initialen
    Laden der Seite verwendet, um den aktuellen Zustand zu laden.
    Auch für regelmäßiges Polling verwendbar.
    
    Returns:
        Response: JSON mit Canvas-Dimensionen und Pixel-Daten
    
    Format: {
        "width": int,
        "height": int,
        "pixels": [[str, ...], ...]
    }
    """
    return jsonify({
        "width": CANVAS_WIDTH,
        "height": CANVAS_HEIGHT,
        "pixels": pixel_data
    })

@app.route("/api/pixel", methods=["POST"])
def update_pixel():
    """
    API-Endpunkt zum Aktualisieren eines einzelnen Pixels.
    
    Empfängt Pixel-Änderungen von Clients, validiert die Daten
    und aktualisiert die Datenstruktur.
    
    Request Body (JSON):
        {
            "x": int,      # X-Koordinate (0 bis CANVAS_WIDTH-1)
            "y": int,      # Y-Koordinate (0 bis CANVAS_HEIGHT-1)
            "color": str   # Farbe im Hex-Format "#RRGGBB"
        }
    
    Returns:
        Response: JSON mit Erfolgs- oder Fehlermeldung
    
    Validierung:
        - Koordinaten müssen innerhalb der Canvas-Grenzen liegen
        - Farbe muss ein gültiger Hex-Farbcode sein
    """
    try:
        # JSON-Daten aus der Anfrage extrahieren
        data = request.get_json()
        
        if not data:
            return jsonify({"success": False, "error": "Keine Daten empfangen"}), 400
        
        # Daten aus dem empfangenen Objekt extrahieren
        x = int(data.get("x", -1))
        y = int(data.get("y", -1))
        color = data.get("color", DEFAULT_COLOR)
        
        # Koordinaten-Validierung: Sicherstellen, dass Pixel innerhalb der Canvas liegt
        if not (0 <= x < CANVAS_WIDTH and 0 <= y < CANVAS_HEIGHT):
            return jsonify({
                "success": False, 
                "error": f"Koordinaten außerhalb der Grenzen: ({x}, {y})"
            }), 400
        
        # Farb-Validierung: Prüfen auf gültiges Hex-Format
        if not (isinstance(color, str) and len(color) == 7 and color.startswith("#")):
            return jsonify({
                "success": False, 
                "error": f"Ungültiges Farbformat: {color}"
            }), 400
        
        # Zusätzliche Validierung: Nur gültige Hex-Zeichen erlauben
        try:
            int(color[1:], 16)  # Versuche, den Hex-Teil zu parsen
        except ValueError:
            return jsonify({
                "success": False, 
                "error": f"Ungültige Hex-Zeichen in Farbe: {color}"
            }), 400
        
        # Pixel-Daten aktualisieren
        pixel_data[y][x] = color
        
        print(f"[PIXEL] Aktualisiert: ({x}, {y}) -> {color}")
        
        return jsonify({
            "success": True,
            "x": x,
            "y": y,
            "color": color
        })
        
    except (ValueError, TypeError) as e:
        # Fehlerbehandlung für ungültige Daten
        print(f"[FEHLER] Ungültige Pixel-Daten: {e}")
        return jsonify({
            "success": False, 
            "error": f"Ungültige Daten: {str(e)}"
        }), 400

# ============================================================================
# HILFSFUNKTIONEN
# ============================================================================

def browser_oeffnen():
    """
    Öffnet den Standard-Browser mit der Canvas-URL.
    
    Diese Funktion wird in einem separaten Thread ausgeführt,
    um den Server-Start nicht zu verzögern. Eine kurze Verzögerung
    stellt sicher, dass der Server bereit ist, bevor der Browser öffnet.
    """
    import time
    # Kurze Verzögerung, damit der Server Zeit hat zu starten
    time.sleep(1.5)
    
    # URL zusammensetzen und im Standard-Browser öffnen
    url = f"http://{HOST}:{PORT}"
    print(f"[INFO] Öffne Browser: {url}")
    webbrowser.open(url)

# ============================================================================
# HAUPTPROGRAMM - Startet den Server
# ============================================================================

if __name__ == "__main__":
    """
    Haupteinstiegspunkt der Anwendung.
    
    Startet den Flask-Server und öffnet automatisch
    einen Browser-Tab mit der Pixel-Canvas-Anwendung.
    """
    print("=" * 60)
    print("  PIXEL CANVAS - Interaktives Pixel-Zeichenprogramm")
    print("=" * 60)
    print(f"  Canvas-Größe: {CANVAS_WIDTH} x {CANVAS_HEIGHT} Pixel")
    print(f"  Server-Adresse: http://{HOST}:{PORT}")
    print("=" * 60)
    print()
    
    # Browser in separatem Thread öffnen
    # daemon=True bedeutet, dass der Thread beendet wird, wenn das Hauptprogramm endet
    browser_thread = threading.Thread(target=browser_oeffnen, daemon=True)
    browser_thread.start()
    
    # Server starten
    # debug=False für Produktion (verhindert Neustart bei Dateiänderungen)
    print("[INFO] Starte Server... (Strg+C zum Beenden)")
    app.run(host=HOST, port=PORT, debug=False, threaded=True)
