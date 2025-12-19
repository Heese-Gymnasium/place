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
import base64
import hashlib
import hmac
import json
import secrets
import webbrowser  # Zum automatischen Öffnen des Browsers
import threading   # Für parallele Ausführung (Browser öffnen ohne Server zu blockieren)
import os          # Für Betriebssystem-Funktionen

# Flask für Web-Server
from flask import Flask, render_template, jsonify, request, make_response, session, redirect, url_for, g

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

# Liste erlaubter Admin-E-Mails (konfigurierbar über Umgebungsvariable ADMIN_EMAILS)
ADMIN_EMAILS = {e.strip().lower() for e in os.environ.get("ADMIN_EMAILS", "admin@example.com").split(",") if e.strip()}

# Gemeinsamer Schlüssel für die Signatur-Prüfung des externen Dashboard-SSO
DASHBOARD_SSO_SECRET = os.environ.get("DASHBOARD_SSO_SECRET", "dashboard-demo-secret")

# Rollen-Definitionen
AVAILABLE_ROLES = {"Admin", "Moderator", "User"}

# In-Memory-Userstore (E-Mail als Schlüssel)
users = {}
pending_codes = {}

# ============================================================================
# BENUTZER- UND AUTHENTIFIZIERUNGS-LOGIK
# ============================================================================

def ensure_user(email, name=None, roles=None):
    """
    Sichert oder erstellt einen Benutzer im In-Memory-Store.
    """
    normalized = email.lower()
    user = users.get(normalized)
    assigned_roles = set(roles or [])

    if normalized in ADMIN_EMAILS:
        assigned_roles.add("Admin")

    if not assigned_roles:
        assigned_roles.add("User")

    clean_roles = assigned_roles & AVAILABLE_ROLES or assigned_roles

    if user:
        if name:
            user["name"] = name
        user["roles"] = sorted(set(user.get("roles", [])) | clean_roles)
        users[normalized] = user
        return {"email": normalized, **user}

    user = {
        "name": name or normalized,
        "roles": sorted(clean_roles),
    }
    users[normalized] = user
    return {"email": normalized, **user}


def login_user(user):
    """
    Speichert Benutzerinformationen in der Session.
    """
    session["user_email"] = user["email"]
    session["user_roles"] = user.get("roles", [])
    session["user_name"] = user.get("name", user["email"])


def logout_user():
    """
    Entfernt Benutzerinformationen aus der Session.
    """
    session.pop("user_email", None)
    session.pop("user_roles", None)
    session.pop("user_name", None)


def current_user():
    """
    Gibt den aktuell eingeloggten Benutzer zurück oder None.
    """
    email = session.get("user_email")
    if not email:
        return None

    user = users.get(email.lower())
    if not user:
        return None

    return {"email": email, **user}


@app.before_request
def load_current_user():
    """
    Stellt den aktuellen Benutzer für Templates bereit.
    """
    g.current_user = current_user()

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


@app.route("/login", methods=["GET", "POST"])
def login():
    """
    Login-Seite für Admin-E-Mails mit Einmalcode.
    """
    next_target = request.args.get("next") or request.form.get("next") or url_for("index")
    message = None
    error = None

    if request.method == "POST":
        email = (request.form.get("email") or "").strip().lower()
        code = (request.form.get("code") or "").strip()
        name = (request.form.get("name") or "").strip()

        if not email:
            error = "Bitte E-Mail angeben."
        elif email not in ADMIN_EMAILS:
            error = "E-Mail ist nicht für den Admin-Login freigeschaltet."
        elif not code:
            generated = f"{secrets.randbelow(1000000):06d}"
            pending_codes[email] = generated
            print(f"[LOGIN] Einmalcode für {email}: {generated}")
            message = "Einmalcode generiert. Der Code wurde im Server-Log ausgegeben."
        else:
            expected = pending_codes.get(email)
            if expected != code:
                error = "Ungültiger Einmalcode."
            else:
                user = ensure_user(email, name=name or None, roles={"Admin"})
                pending_codes.pop(email, None)
                login_user(user)
                return redirect(next_target)

    return render_template("login.html", next=next_target, message=message, error=error)


@app.route("/logout")
def logout():
    """
    Beendet die aktuelle Sitzung.
    """
    logout_user()
    return redirect(url_for("index"))


@app.route("/profile", methods=["GET", "POST"])
def profile():
    """
    Ermöglicht angemeldeten Nutzern die Aktualisierung ihres Namens.
    """
    user = current_user()
    if not user:
        return redirect(url_for("login", next=request.path))

    message = None
    if request.method == "POST":
        name = (request.form.get("name") or "").strip()
        if name:
            updated = ensure_user(user["email"], name=name, roles=set(user.get("roles", [])))
            login_user(updated)
            user = updated
            message = "Name aktualisiert."

    return render_template("profile.html", user=user, message=message)


@app.route("/sso/callback", methods=["POST"])
def sso_callback():
    """
    Single-Sign-On Callback für das Dashboard.
    Erwartet einen signierten Payload (Base64-kodiertes JSON).
    """
    data = request.get_json(silent=True) or {}
    payload = data.get("payload", "")
    signature = data.get("signature", "")

    if not payload or not signature:
        return jsonify({"success": False, "error": "Payload oder Signatur fehlt."}), 400

    computed = hmac.new(DASHBOARD_SSO_SECRET.encode(), payload.encode(), hashlib.sha256).hexdigest()
    if not hmac.compare_digest(computed, signature):
        return jsonify({"success": False, "error": "Signatur ungültig."}), 401

    try:
        decoded_payload = base64.b64decode(payload).decode("utf-8")
        payload_data = json.loads(decoded_payload)
    except (ValueError, json.JSONDecodeError, UnicodeDecodeError):
        return jsonify({"success": False, "error": "Payload konnte nicht gelesen werden."}), 400

    email = (payload_data.get("email") or "").strip().lower()
    name = (payload_data.get("name") or "").strip() or email
    roles = set(payload_data.get("roles") or [])
    roles = {role for role in roles if role in AVAILABLE_ROLES}

    if not email:
        return jsonify({"success": False, "error": "E-Mail im Payload fehlt."}), 400

    user = ensure_user(email, name=name, roles=roles)
    login_user(user)

    redirect_target = payload_data.get("redirect") or url_for("index")
    return jsonify({"success": True, "redirect": redirect_target, "email": email, "roles": user.get("roles")})

@app.route("/admin")
def admin():
    """
    Admin-Seite der Anwendung.
    
    Rendert das HTML-Template für Administratoren mit erweiterten Funktionen.
    Übergibt die Canvas-Dimensionen an das Template.
    
    Returns:
        str: Gerendertes HTML der Admin-Seite
    """
    user = current_user()
    if not user or "Admin" not in user.get("roles", []):
        return redirect(url_for("login", next=request.path))

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
