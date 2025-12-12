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
from datetime import datetime, timedelta

# Flask für Web-Server
from flask import Flask, render_template, jsonify, request, make_response, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash

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

# Datenbank-Konfiguration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///pixelcanvas.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Datenbank initialisieren
db = SQLAlchemy(app)

# Login Manager initialisieren
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# ============================================================================
# DATENBANK-MODELLE
# ============================================================================

class User(UserMixin, db.Model):
    """Benutzer-Modell für Authentifizierung und Moderation"""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    is_moderator = db.Column(db.Boolean, default=False)
    is_banned = db.Column(db.Boolean, default=False)
    timeout_until = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_activity = db.Column(db.DateTime, default=datetime.utcnow)
    pixels_placed = db.Column(db.Integer, default=0)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def is_timed_out(self):
        if self.timeout_until and self.timeout_until > datetime.utcnow():
            return True
        return False
    
    def can_place_pixel(self):
        """Prüft ob Benutzer Pixel platzieren darf"""
        if self.is_banned:
            return False
        if self.is_timed_out():
            return False
        return True

class PixelHistory(db.Model):
    """Speichert die Historie aller Pixel-Änderungen"""
    id = db.Column(db.Integer, primary_key=True)
    x = db.Column(db.Integer, nullable=False)
    y = db.Column(db.Integer, nullable=False)
    color = db.Column(db.String(7), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref='pixel_history')

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

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
    import time
    cache_bust = str(int(time.time()))
    
    response = make_response(render_template(
        "index.html",
        width=CANVAS_WIDTH,
        height=CANVAS_HEIGHT,
        cache_bust=cache_bust
    ))
    # Disable caching for development
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    response.headers['ETag'] = cache_bust
    print(f"[DEBUG] Serving index.html with cache_bust={cache_bust}")
    return response

@app.route("/login", methods=["GET", "POST"])
def login():
    """Login-Seite und Handler"""
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == "POST":
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            if user.is_banned:
                flash('Dein Account wurde gesperrt.', 'error')
                return redirect(url_for('login'))
            
            if user.is_timed_out():
                flash(f'Dein Account ist bis {user.timeout_until.strftime("%Y-%m-%d %H:%M")} gesperrt.', 'error')
                return redirect(url_for('login'))
            
            login_user(user)
            user.last_activity = datetime.utcnow()
            db.session.commit()
            
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('index'))
        else:
            flash('Ungültiger Benutzername oder Passwort.', 'error')
    
    return render_template('login.html')

@app.route("/register", methods=["GET", "POST"])
def register():
    """Registrierungs-Seite und Handler"""
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == "POST":
        username = request.form.get('username')
        password = request.form.get('password')
        
        if User.query.filter_by(username=username).first():
            flash('Benutzername bereits vergeben.', 'error')
            return redirect(url_for('register'))
        
        user = User(username=username)
        user.set_password(password)
        
        # Erster Benutzer wird zum Admin
        if User.query.count() == 0:
            user.is_admin = True
            user.is_moderator = True
        
        db.session.add(user)
        db.session.commit()
        
        flash('Registrierung erfolgreich! Bitte melde dich an.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route("/logout")
@login_required
def logout():
    """Logout Handler"""
    logout_user()
    return redirect(url_for('index'))

@app.route("/admin")
@login_required
def admin():
    """Admin-Dashboard mit Statistiken und Benutzerverwaltung"""
    if not current_user.is_admin and not current_user.is_moderator:
        flash('Keine Berechtigung für diese Seite.', 'error')
        return redirect(url_for('index'))
    
    # Statistiken sammeln
    total_users = User.query.count()
    total_pixels = PixelHistory.query.count()
    active_users_count = User.query.filter(
        User.last_activity >= datetime.utcnow() - timedelta(minutes=5)
    ).count()
    
    # Alle Benutzer abrufen
    users = User.query.order_by(User.created_at.desc()).all()
    
    # Top-Benutzer nach Pixeln
    top_users = User.query.order_by(User.pixels_placed.desc()).limit(10).all()
    
    # Letzte Pixel-Änderungen
    recent_pixels = PixelHistory.query.order_by(PixelHistory.timestamp.desc()).limit(20).all()
    
    return render_template('admin.html',
                         total_users=total_users,
                         total_pixels=total_pixels,
                         active_users_count=active_users_count,
                         users=users,
                         top_users=top_users,
                         recent_pixels=recent_pixels,
                         now=datetime.utcnow())

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
        # Prüfe ob Benutzer angemeldet ist
        if not current_user.is_authenticated:
            return jsonify({"success": False, "error": "Nicht angemeldet"}), 401
        
        # Prüfe ob Benutzer Pixel platzieren darf
        if not current_user.can_place_pixel():
            if current_user.is_banned:
                return jsonify({"success": False, "error": "Dein Account wurde gesperrt"}), 403
            if current_user.is_timed_out():
                return jsonify({"success": False, "error": f"Gesperrt bis {current_user.timeout_until.strftime('%Y-%m-%d %H:%M')}"}), 403
        
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
        
        # In Historie speichern
        pixel_history = PixelHistory(x=x, y=y, color=color, user_id=current_user.id)
        db.session.add(pixel_history)
        
        # Benutzer-Statistiken aktualisieren
        current_user.pixels_placed += 1
        current_user.last_activity = datetime.utcnow()
        db.session.commit()
        
        print(f"[PIXEL] Aktualisiert: ({x}, {y}) -> {color} by {current_user.username}")
        
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

@app.route("/api/admin/ban_user", methods=["POST"])
@login_required
def ban_user():
    """Sperrt einen Benutzer permanent"""
    if not current_user.is_admin and not current_user.is_moderator:
        return jsonify({"success": False, "error": "Keine Berechtigung"}), 403
    
    data = request.get_json()
    user_id = data.get('user_id')
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({"success": False, "error": "Benutzer nicht gefunden"}), 404
    
    # Admins können nicht gesperrt werden
    if user.is_admin:
        return jsonify({"success": False, "error": "Admins können nicht gesperrt werden"}), 403
    
    user.is_banned = True
    db.session.commit()
    
    return jsonify({"success": True, "message": f"Benutzer {user.username} wurde gesperrt"})

@app.route("/api/admin/unban_user", methods=["POST"])
@login_required
def unban_user():
    """Hebt die Sperre eines Benutzers auf"""
    if not current_user.is_admin and not current_user.is_moderator:
        return jsonify({"success": False, "error": "Keine Berechtigung"}), 403
    
    data = request.get_json()
    user_id = data.get('user_id')
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({"success": False, "error": "Benutzer nicht gefunden"}), 404
    
    user.is_banned = False
    db.session.commit()
    
    return jsonify({"success": True, "message": f"Sperre von {user.username} aufgehoben"})

@app.route("/api/admin/timeout_user", methods=["POST"])
@login_required
def timeout_user():
    """Setzt einen Benutzer für eine bestimmte Zeit auf Timeout"""
    if not current_user.is_admin and not current_user.is_moderator:
        return jsonify({"success": False, "error": "Keine Berechtigung"}), 403
    
    data = request.get_json()
    user_id = data.get('user_id')
    minutes = data.get('minutes', 60)
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({"success": False, "error": "Benutzer nicht gefunden"}), 404
    
    # Admins können nicht getimeoutet werden
    if user.is_admin:
        return jsonify({"success": False, "error": "Admins können nicht getimeoutet werden"}), 403
    
    user.timeout_until = datetime.utcnow() + timedelta(minutes=minutes)
    db.session.commit()
    
    return jsonify({"success": True, "message": f"Benutzer {user.username} für {minutes} Minuten gesperrt"})

@app.route("/api/admin/remove_timeout", methods=["POST"])
@login_required
def remove_timeout():
    """Hebt einen Timeout auf"""
    if not current_user.is_admin and not current_user.is_moderator:
        return jsonify({"success": False, "error": "Keine Berechtigung"}), 403
    
    data = request.get_json()
    user_id = data.get('user_id')
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({"success": False, "error": "Benutzer nicht gefunden"}), 404
    
    user.timeout_until = None
    db.session.commit()
    
    return jsonify({"success": True, "message": f"Timeout von {user.username} aufgehoben"})

@app.route("/api/admin/set_moderator", methods=["POST"])
@login_required
def set_moderator():
    """Gibt einem Benutzer Moderator-Rechte oder entzieht sie"""
    if not current_user.is_admin:
        return jsonify({"success": False, "error": "Nur Admins können Moderatoren ernennen"}), 403
    
    data = request.get_json()
    user_id = data.get('user_id')
    is_moderator = data.get('is_moderator', True)
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({"success": False, "error": "Benutzer nicht gefunden"}), 404
    
    user.is_moderator = is_moderator
    db.session.commit()
    
    action = "erhalten" if is_moderator else "verloren"
    return jsonify({"success": True, "message": f"Benutzer {user.username} hat Moderator-Rechte {action}"})

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
    
    # Datenbank initialisieren
    with app.app_context():
        db.create_all()
        print("[INFO] Datenbank initialisiert")
    
    # Browser in separatem Thread öffnen
    # daemon=True bedeutet, dass der Thread beendet wird, wenn das Hauptprogramm endet
    browser_thread = threading.Thread(target=browser_oeffnen, daemon=True)
    browser_thread.start()
    
    # Server starten
    # debug=False für Produktion (verhindert Neustart bei Dateiänderungen)
    print("[INFO] Starte Server... (Strg+C zum Beenden)")
    app.run(host=HOST, port=PORT, debug=False, threaded=True)
