# UI-Elemente Guide - Vollständige Dokumentation

Umfassende Dokumentation aller HTML-Elemente, Buttons, Textfelder und UI-Komponenten der Pixel Canvas Anwendung.

---

## 📑 Inhaltsverzeichnis

1. [Header-Bereich](#1-header-bereich)
2. [Toolbar / Werkzeugleiste](#2-toolbar--werkzeugleiste)
3. [Canvas-Container](#3-canvas-container)
4. [Info-Panel](#4-info-panel)
5. [Modal-Dialoge (Admin)](#5-modal-dialoge-admin)
6. [Styling & CSS](#6-styling--css)
7. [JavaScript-Objekte](#7-javascript-objekte)
8. [Variationen & Anpassungen](#8-variationen--anpassungen)

---

## 1. 🎨 HEADER-BEREICH

### 1.1 Titel (H1-Element)

**HTML:**
```html
<header>
    <h1>🎨 Pixel Canvas</h1>
    <p class="subtitle">Klicke zum Malen | Scroll zum Zoomen | Rechts-Drag zum Verschieben</p>
</header>
```

**Funktionsweise:**
- `<h1>` = Haupt-Überschrift mit Emoji
- `.subtitle` = Hilfetext/Anleitung für Nutzer

**CSS:**
```css
h1 {
    font-size: 2.5rem;
    background: linear-gradient(90deg, #e94560, #f39c12, #1abc9c);
    -webkit-background-clip: text;
    background-clip: text;
    -webkit-text-fill-color: transparent;  /* Macht Text transparent für Gradient */
}

.subtitle {
    font-size: 1rem;
    color: #8892b0;
}
```

**Variationen:**

```html
<!-- Variation 1: Ohne Emoji -->
<h1>Pixel Canvas</h1>

<!-- Variation 2: Mit anderem Gradient -->
<h1 style="background: linear-gradient(90deg, #FF0000, #00FF00, #0000FF)">
    🎨 Pixel Canvas
</h1>

<!-- Variation 3: Mit Animation -->
<h1 style="animation: pulse 2s infinite">
    🎨 Pixel Canvas
</h1>
```

**JavaScript zum Ändern:**
```javascript
// Titel dynamisch ändern
document.querySelector('h1').textContent = '🖼️ Mein Kunstwerk';

// Untertitel ändern
document.querySelector('.subtitle').textContent = 'Neue Anleitung hier';
```

---

### 1.2 Header Container

**HTML-Struktur:**
```html
<header>
    <!-- Content hier -->
</header>
```

**CSS:**
```css
header {
    text-align: center;
    margin-bottom: 20px;
}
```

**Variationen:**

```css
/* Variation 1: Mit Hintergrund */
header {
    background: rgba(255, 255, 255, 0.05);
    padding: 20px;
    border-radius: 10px;
    margin-bottom: 20px;
}

/* Variation 2: Mit Border */
header {
    border-bottom: 2px solid rgba(233, 69, 96, 0.5);
    padding-bottom: 20px;
    margin-bottom: 20px;
}

/* Variation 3: Mit Box-Shadow */
header {
    box-shadow: 0 4px 10px rgba(0, 0, 0, 0.3);
    padding: 20px;
    margin-bottom: 20px;
}
```

---

## 2. 🎛️ TOOLBAR / WERKZEUGLEISTE

### 2.1 Toolbar Container

**HTML:**
```html
<div class="toolbar">
    <div class="toolbar-item">
        <!-- Items hier -->
    </div>
</div>
```

**CSS:**
```css
.toolbar {
    display: flex;
    align-items: center;
    gap: 20px;
    margin-bottom: 20px;
    padding: 15px 25px;
    background: rgba(255, 255, 255, 0.1);
    border-radius: 15px;
    backdrop-filter: blur(10px);
}

.toolbar-item {
    display: flex;
    align-items: center;
    gap: 10px;
}
```

**Funktionsweise:**
- `display: flex` = horizontale Anordnung
- `gap: 20px` = Abstand zwischen Items
- `backdrop-filter: blur(10px)` = Glasmorphismus-Effekt

**Variationen:**

```css
/* Variation 1: Vertikal (für mobile Geräte) */
.toolbar {
    flex-direction: column;
    align-items: stretch;
}

/* Variation 2: Mit fester Breite */
.toolbar {
    max-width: 500px;
    margin: 0 auto;
}

/* Variation 3: Dunkler Hintergrund */
.toolbar {
    background: rgba(0, 0, 0, 0.3);
    border: 1px solid rgba(255, 255, 255, 0.1);
}

/* Variation 4: Mit Shadow */
.toolbar {
    box-shadow: 0 8px 20px rgba(0, 0, 0, 0.4);
}
```

---

### 2.2 Color Picker (Farbwähler)

**HTML:**
```html
<div class="toolbar-item">
    <label for="color-picker">Farbe:</label>
    <input type="color" id="color-picker" value="#e94560" title="Farbe auswählen">
    <div class="color-preview" id="color-preview"></div>
</div>
```

**CSS:**
```css
#color-picker {
    width: 50px;
    height: 40px;
    border: none;
    border-radius: 8px;
    cursor: pointer;
    -webkit-appearance: none;
    padding: 0;
}

#color-picker::-webkit-color-swatch-wrapper {
    padding: 0;
}

#color-picker::-webkit-color-swatch {
    border: 2px solid #fff;
    border-radius: 6px;
}

.color-preview {
    width: 40px;
    height: 40px;
    border-radius: 8px;
    border: 2px solid #fff;
    background-color: #000000;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
}
```

**Funktionsweise:**
- `type="color"` = Browser-eigener Farbwähler
- `value="#e94560"` = Standard-Farbe (Rot)
- `.color-preview` = Visuelle Vorschau der ausgewählten Farbe

**JavaScript:**
```javascript
const colorPicker = document.getElementById('color-picker');
const colorPreview = document.getElementById('color-preview');

// Farb-Update Listener
colorPicker.addEventListener('input', function() {
    colorPreview.style.backgroundColor = colorPicker.value;
    console.log('Neue Farbe:', colorPicker.value);
});

// Farbe programmieren
colorPicker.value = '#FF0000';  // Rot
colorPreview.style.backgroundColor = '#FF0000';

// Farbe auslesen
const aktuellesFarbe = colorPicker.value;
```

**Variationen:**

```html
<!-- Variation 1: Ohne Label -->
<input type="color" id="color-picker" value="#e94560">

<!-- Variation 2: Mit größerer Größe -->
<input type="color" id="color-picker" style="width: 80px; height: 50px;">

<!-- Variation 3: Mit mehreren Farbwählern -->
<input type="color" id="primary-color" value="#e94560">
<input type="color" id="secondary-color" value="#1abc9c">
```

**JavaScript Variationen:**

```javascript
// Farbe validieren (Hex-Format)
function isValidHex(color) {
    return /^#[0-9A-F]{6}$/i.test(color);
}

// Farbe zu RGB konvertieren
function hexToRgb(hex) {
    const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
    return result ? {
        r: parseInt(result[1], 16),
        g: parseInt(result[2], 16),
        b: parseInt(result[3], 16)
    } : null;
}

// Farbe speichern (localStorage)
colorPicker.addEventListener('change', function() {
    localStorage.setItem('selectedColor', colorPicker.value);
});

// Gespeicherte Farbe laden
const savedColor = localStorage.getItem('selectedColor');
if (savedColor) {
    colorPicker.value = savedColor;
    colorPreview.style.backgroundColor = savedColor;
}
```

---

### 2.3 Status Indicator (Verbindungsstatus)

**HTML:**
```html
<div class="toolbar-item status">
    <span class="status-indicator" id="status-indicator"></span>
    <span id="status-text">Verbinde...</span>
</div>
```

**CSS:**
```css
.status {
    display: flex;
    align-items: center;
    gap: 8px;
}

.status-indicator {
    width: 12px;
    height: 12px;
    border-radius: 50%;
    background-color: #e74c3c;  /* Rot = Disconnected */
    animation: pulse 2s infinite;
}

.status-indicator.connected {
    background-color: #2ecc71;  /* Grün = Connected */
}

@keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.5; }
}
```

**Funktionsweise:**
- Rote LED = Getrennt/Connecting
- Grüne LED = Verbunden
- Animation = Pulsierender Effekt

**JavaScript:**
```javascript
const statusIndicator = document.getElementById('status-indicator');
const statusText = document.getElementById('status-text');

// Status: Verbunden
function setConnected() {
    statusIndicator.classList.add('connected');
    statusText.textContent = 'Verbunden';
    statusIndicator.style.animation = 'none';
}

// Status: Getrennt
function setDisconnected() {
    statusIndicator.classList.remove('connected');
    statusText.textContent = 'Getrennt';
    statusIndicator.style.animation = 'pulse 2s infinite';
}

// Status: Connecting
function setConnecting() {
    statusIndicator.classList.remove('connected');
    statusText.textContent = 'Verbinde...';
    statusIndicator.style.animation = 'pulse 2s infinite';
}
```

**Variationen:**

```css
/* Variation 1: Ohne Animation */
.status-indicator {
    animation: none;
}

/* Variation 2: Mit Text-Label */
.status-indicator::after {
    content: 'LIVE';
    margin-left: 5px;
    font-size: 0.8rem;
}

/* Variation 3: Größere LED */
.status-indicator {
    width: 20px;
    height: 20px;
}

/* Variation 4: Mit Icon statt LED */
.status-indicator {
    width: auto;
    height: auto;
    border-radius: 0;
    font-size: 1.2rem;
}
```

---

## 3. 📦 CANVAS-CONTAINER

### 3.1 Canvas Container

**HTML:**
```html
<div class="canvas-container">
    <canvas id="pixel-canvas"></canvas>
</div>
```

**CSS:**
```css
.canvas-container {
    box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5);
    border-radius: 10px;
    overflow: hidden;
    border: 3px solid rgba(255, 255, 255, 0.2);
}

#pixel-canvas {
    display: block;
    image-rendering: pixelated;
    image-rendering: crisp-edges;
    cursor: crosshair;
}
```

**Funktionsweise:**
- `overflow: hidden` = Inhalt wird nicht über Grenzen hinaus angezeigt
- `image-rendering: pixelated` = Scharfe Pixel-Kanten (wichtig!)
- `cursor: crosshair` = Fadenkreuz-Cursor über Canvas

**JavaScript:**
```javascript
const canvas = document.getElementById('pixel-canvas');
const ctx = canvas.getContext('2d');

// Canvas-Größe setzen
canvas.width = 500;
canvas.height = 500;

// Canvas leeren
ctx.clearRect(0, 0, canvas.width, canvas.height);

// Hintergrund füllen
ctx.fillStyle = '#FFFFFF';
ctx.fillRect(0, 0, canvas.width, canvas.height);
```

**Variationen:**

```css
/* Variation 1: Ohne Border */
.canvas-container {
    box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5);
    border-radius: 10px;
    overflow: hidden;
}

/* Variation 2: Mit farbiger Border */
.canvas-container {
    border: 3px solid #e94560;
}

/* Variation 3: Mit Shadow und Glow */
.canvas-container {
    box-shadow: 0 0 20px rgba(233, 69, 96, 0.5),
                0 20px 60px rgba(0, 0, 0, 0.5);
}

/* Variation 4: Responsive Canvas */
.canvas-container {
    max-width: 100%;
    aspect-ratio: 1;
}
```

---

## 4. 📊 INFO-PANEL

### 4.1 Info Panel Container

**HTML:**
```html
<div class="info-panel">
    <p class="coordinates">
        Position: <span id="coord-display">--, --</span> | 
        Canvas-Größe: {{ width }} × {{ height }} Pixel
    </p>
</div>
```

**CSS:**
```css
.info-panel {
    margin-top: 20px;
    padding: 15px 25px;
    background: rgba(255, 255, 255, 0.1);
    border-radius: 15px;
    backdrop-filter: blur(10px);
    text-align: center;
}

.coordinates {
    font-family: monospace;
    font-size: 1.1rem;
}
```

**Funktionsweise:**
- Zeigt aktuelle Mausposition über Canvas
- Zeigt Canvas-Dimensionen
- Monospace-Schrift für Koordinaten

**JavaScript:**
```javascript
const coordDisplay = document.getElementById('coord-display');

// Koordinaten aktualisieren
function updateCoordinates(x, y) {
    coordDisplay.textContent = `${x}, ${y}`;
}

// Koordinaten zurücksetzen
function resetCoordinates() {
    coordDisplay.textContent = '--, --';
}
```

**Variationen:**

```html
<!-- Variation 1: Mit mehr Informationen -->
<div class="info-panel">
    <p class="coordinates">
        Position: <span id="coord-display">--, --</span> | 
        Canvas: {{ width }} × {{ height }} |
        Zoom: <span id="zoom-level">1x</span>
    </p>
</div>

<!-- Variation 2: Mit Statistiken -->
<div class="info-panel">
    <p>Pixel gesetzt: <span id="pixel-count">0</span></p>
    <p>Position: <span id="coord-display">--, --</span></p>
</div>

<!-- Variation 3: Mit Progress Bar -->
<div class="info-panel">
    <p>Fortschritt: <span id="progress">0</span>%</p>
    <div style="width: 100%; height: 10px; background: rgba(255,255,255,0.1); border-radius: 5px;">
        <div id="progress-bar" style="height: 100%; width: 0%; background: #2ecc71; border-radius: 5px; transition: width 0.3s;"></div>
    </div>
</div>
```

**JavaScript Variationen:**

```javascript
// Zoom-Level anzeigen
let zoomLevel = 1;
document.getElementById('zoom-level').textContent = `${zoomLevel.toFixed(1)}x`;

// Pixel-Zähler
let pixelCount = 0;
function incrementPixelCount() {
    pixelCount++;
    document.getElementById('pixel-count').textContent = pixelCount;
}

// Progress Bar
function updateProgress(percentage) {
    document.getElementById('progress').textContent = percentage;
    document.getElementById('progress-bar').style.width = percentage + '%';
}
```

---

## 5. 🎭 MODAL-DIALOGE (ADMIN)

### 5.1 Admin Action Menu Modal

**JavaScript-Erstellung:**
```javascript
function showAdminActionMenu(coords) {
    // Modal erstellen
    const modal = document.createElement('div');
    modal.style.cssText = `
        position: fixed;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        background: rgba(26, 26, 46, 0.98);
        border: 2px solid rgba(233, 69, 96, 0.8);
        border-radius: 12px;
        padding: 30px;
        z-index: 10000;
        box-shadow: 0 10px 40px rgba(0, 0, 0, 0.7);
        backdrop-filter: blur(10px);
        min-width: 300px;
    `;

    // Titel hinzufügen
    const title = document.createElement('h2');
    title.textContent = 'Admin-Menü: Was möchtest du machen?';
    title.style.cssText = `
        color: #ffffff;
        margin-bottom: 20px;
        font-size: 1.2rem;
        text-align: center;
        background: linear-gradient(90deg, #e94560, #f39c12);
        -webkit-background-clip: text;
        background-clip: text;
        -webkit-text-fill-color: transparent;
    `;
    modal.appendChild(title);

    // Buttons Container
    const buttonsContainer = document.createElement('div');
    buttonsContainer.style.cssText = `
        display: flex;
        flex-direction: column;
        gap: 10px;
    `;

    // Button Definition
    const actions = [
        { id: 'pixel', label: '🎨 Pixel setzen', color: '#e94560' },
        { id: 'rectangle', label: '📦 Rechteck zeichnen', color: '#f39c12' },
        { id: 'circle', label: '⭕ Kreis zeichnen', color: '#1abc9c' },
        { id: 'line', label: '📍 Linie zeichnen', color: '#9b59b6' }
    ];

    // Buttons erstellen
    actions.forEach(action => {
        const button = document.createElement('button');
        button.textContent = action.label;
        button.style.cssText = `
            padding: 12px 16px;
            background: rgba(255, 255, 255, 0.1);
            border: 2px solid ${action.color};
            border-radius: 8px;
            color: #ffffff;
            font-size: 1rem;
            cursor: pointer;
            transition: all 0.3s ease;
        `;

        button.onmouseover = function() {
            this.style.background = action.color;
            this.style.boxShadow = `0 0 15px ${action.color}`;
        };

        button.onmouseout = function() {
            this.style.background = 'rgba(255, 255, 255, 0.1)';
            this.style.boxShadow = 'none';
        };

        button.onclick = function() {
            // Modal entfernen
            document.body.removeChild(modal);
            document.body.removeChild(overlay);
            // Aktion ausführen
            executeAdminAction(action.id, coords);
        };

        buttonsContainer.appendChild(button);
    });

    modal.appendChild(buttonsContainer);

    // Cancel Button
    const cancelButton = document.createElement('button');
    cancelButton.textContent = '❌ Abbrechen';
    cancelButton.style.cssText = `
        width: 100%;
        margin-top: 15px;
        padding: 10px;
        background: rgba(200, 50, 50, 0.2);
        border: 2px solid #e74c3c;
        border-radius: 8px;
        color: #e74c3c;
        cursor: pointer;
        font-size: 0.9rem;
        transition: all 0.3s ease;
    `;

    cancelButton.onclick = function() {
        document.body.removeChild(modal);
        document.body.removeChild(overlay);
    };

    modal.appendChild(cancelButton);

    // Overlay (Hintergrund-Dimming)
    const overlay = document.createElement('div');
    overlay.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: rgba(0, 0, 0, 0.6);
        z-index: 9999;
    `;

    overlay.onclick = function() {
        document.body.removeChild(modal);
        document.body.removeChild(overlay);
    };

    // DOM hinzufügen
    document.body.appendChild(overlay);
    document.body.appendChild(modal);
}
```

**Funktionsweise:**
- Modal wird dynamisch mit JavaScript erstellt
- Overlay dimmt den Hintergrund
- Buttons haben Hover-Effekte (Farbe wechselt)
- Klick außerhalb oder auf Cancel schließt Modal

**Variationen:**

```javascript
// Variation 1: Mit Animation
modal.style.animation = 'slideIn 0.3s ease';

const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from {
            opacity: 0;
            transform: translate(-50%, -60%);
        }
        to {
            opacity: 1;
            transform: translate(-50%, -50%);
        }
    }
`;
document.head.appendChild(style);

// Variation 2: Mit Keyboard Support (ESC zum Schließen)
document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') {
        // Modal schließen
    }
});

// Variation 3: Mit Sound-Effekt
const audio = new Audio('data:audio/wav;base64,...');
audio.play();
```

---

## 6. 🎨 STYLING & CSS

### 6.1 Global Styles

**Body:**
```css
body {
    background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
    min-height: 100vh;
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 20px;
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    color: #ffffff;
}
```

**Variationen:**

```css
/* Variation 1: Dunkler */
body {
    background: linear-gradient(135deg, #000000 0%, #1a1a1a 100%);
}

/* Variation 2: Heller */
body {
    background: linear-gradient(135deg, #ffffff 0%, #f0f0f0 100%);
    color: #333333;
}

/* Variation 3: Mit Pattern */
body {
    background: 
        repeating-linear-gradient(
            45deg,
            #1a1a2e,
            #1a1a2e 10px,
            #16213e 10px,
            #16213e 20px
        );
}

/* Variation 4: Mit Bild */
body {
    background: url('background.jpg') center/cover;
    background-attachment: fixed;
}
```

### 6.2 Reset Styles

```css
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}
```

**Funktionsweise:**
- Entfernt Standard-Browser-Abstände
- `box-sizing: border-box` = Größe inklusive Border/Padding

---

## 7. 💾 JAVASCRIPT-OBJEKTE

### 7.1 Field of View (FOV) Objekt

```javascript
let fieldOfView = {
    x1: 0,              // Linke Kante
    y1: 0,              // Obere Kante
    x2: CANVAS_WIDTH,   // Rechte Kante
    y2: CANVAS_HEIGHT   // Untere Kante
};

// FOV-Größe berechnen
const fovWidth = fieldOfView.x2 - fieldOfView.x1;
const fovHeight = fieldOfView.y2 - fieldOfView.y1;

// FOV-Position abrufen
const centerX = fieldOfView.x1 + (fovWidth / 2);
const centerY = fieldOfView.y1 + (fovHeight / 2);
```

### 7.2 Pan State

```javascript
let isPanning = false;
let panStartX = 0;
let panStartY = 0;
let panStartFOV = { x1: 0, y1: 0, x2: CANVAS_WIDTH, y2: CANVAS_HEIGHT };
```

### 7.3 Admin Mode

```javascript
let adminMode = false;  // Von außen setzbar

// Admin-Mode aktivieren
adminMode = true;

// Admin-Mode mit Query-Parameter
const params = new URLSearchParams(window.location.search);
if (params.get('admin') === 'true') {
    adminMode = true;
}

// Admin-Mode mit Token
function checkAdminToken(token) {
    return token === 'SECRET_ADMIN_TOKEN';
}
```

---

## 8. 🔄 VARIATIONEN & ANPASSUNGEN

### 8.1 Custom Color Palette

```javascript
// Vordefinierte Farben
const colorPalette = [
    { name: 'Rot', color: '#e94560' },
    { name: 'Orange', color: '#f39c12' },
    { name: 'Cyan', color: '#1abc9c' },
    { name: 'Blau', color: '#3498db' },
    { name: 'Lila', color: '#9b59b6' }
];

// Palette als Buttons rendern
function renderColorPalette() {
    const paletteContainer = document.createElement('div');
    paletteContainer.style.cssText = `
        display: flex;
        gap: 10px;
        margin: 10px 0;
    `;

    colorPalette.forEach(item => {
        const colorButton = document.createElement('button');
        colorButton.style.cssText = `
            width: 30px;
            height: 30px;
            background-color: ${item.color};
            border: 2px solid white;
            border-radius: 5px;
            cursor: pointer;
            title: ${item.name}
        `;

        colorButton.onclick = function() {
            document.getElementById('color-picker').value = item.color;
            document.getElementById('color-preview').style.backgroundColor = item.color;
        };

        paletteContainer.appendChild(colorButton);
    });

    return paletteContainer;
}
```

### 8.2 Responsive Design

```css
/* Mobile */
@media (max-width: 768px) {
    .toolbar {
        flex-direction: column;
        gap: 10px;
    }

    h1 {
        font-size: 1.8rem;
    }

    .canvas-container {
        max-width: 100%;
    }
}

/* Tablets */
@media (max-width: 1024px) {
    body {
        padding: 10px;
    }

    .toolbar-item {
        gap: 5px;
    }
}
```

### 8.3 Dark/Light Mode Toggle

```javascript
let isDarkMode = true;

function toggleDarkMode() {
    isDarkMode = !isDarkMode;
    
    if (isDarkMode) {
        document.body.style.background = 'linear-gradient(135deg, #1a1a2e 0%, #16213e 100%)';
        document.body.style.color = '#ffffff';
    } else {
        document.body.style.background = 'linear-gradient(135deg, #ffffff 0%, #f0f0f0 100%)';
        document.body.style.color = '#333333';
    }
    
    // LocalStorage speichern
    localStorage.setItem('darkMode', isDarkMode);
}

// Beim Laden wiederherstellen
const savedDarkMode = localStorage.getItem('darkMode') === 'true';
if (savedDarkMode !== isDarkMode) {
    toggleDarkMode();
}
```

### 8.4 Tastatur-Shortcuts

```javascript
// ESC = Modal schließen
// SPACE = Farbe zurücksetzen
// Z = Zoom zurücksetzen
// H = Hilfe anzeigen

document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') {
        // Alle Modals schließen
        document.querySelectorAll('[data-modal]').forEach(m => m.remove());
    }
    
    if (e.key === ' ') {
        e.preventDefault();
        // Zoom zurücksetzen
        fieldOfView = { x1: 0, y1: 0, x2: CANVAS_WIDTH, y2: CANVAS_HEIGHT };
        renderFullCanvas(localPixelData);
    }
    
    if (e.key === 'h' || e.key === 'H') {
        // Hilfe anzeigen
        showHelpModal();
    }
});
```

### 8.5 Accessibility Features

```html
<!-- ARIA Labels für Screen Reader -->
<div class="toolbar-item">
    <label for="color-picker" aria-label="Farbauswahl für Malwerkzeug">Farbe:</label>
    <input type="color" id="color-picker" 
           aria-label="Klicke um Farbe zu wählen"
           value="#e94560">
</div>

<!-- Semantic HTML -->
<button type="button" aria-label="Abbrechen">❌ Abbrechen</button>

<!-- Focus Styles -->
<style>
    button:focus {
        outline: 2px solid #fff;
        outline-offset: 2px;
    }
</style>
```

---

## 📋 ZUSAMMENFASSUNG: UI-Komponenten Matrix

| **Element** | **Typ** | **Funktionalität** | **Wichtigkeit** | **Customizable** |
|---|---|---|---|---|
| Header | Statisch | Titel & Anleitung | Medium | Ja |
| Color Picker | Input | Farbauswahl | Kritisch | Ja |
| Status Indicator | Dynamisch | Verbindungsstatus | Medium | Ja |
| Canvas | Dynamisch | Pixel-Rendering | Kritisch | Teilweise |
| Info Panel | Dynamisch | Koordinaten-Anzeige | Low | Ja |
| Admin Menu Modal | Dynamisch | Aktionsauswahl | High (Admin) | Ja |
| Toolbar | Container | Layout | Medium | Ja |

---

## 🔗 Weitere Ressourcen

- [MDN Web Docs - HTML](https://developer.mozilla.org/en-US/docs/Web/HTML)
- [MDN Web Docs - CSS](https://developer.mozilla.org/en-US/docs/Web/CSS)
- [MDN Web Docs - JavaScript DOM](https://developer.mozilla.org/en-US/docs/Web/API/Document_Object_Model)
- [Color Picker Reference](https://developer.mozilla.org/en-US/docs/Web/HTML/Element/input/color)
