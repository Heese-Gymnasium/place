# Canvas Änderungen - Relevante Code-Stellen mit Erklärung

## 1. 🔧 CANVAS-INITIALISIERUNG (Zeilen ~290-305)

**Relevanz: KRITISCH** - Setzt die Canvas-Grundlagen

```javascript
function initCanvas() {
    // Canvas-Größe in tatsächlichen Bildschirm-Pixeln setzen
    canvas.width = CANVAS_WIDTH * PIXEL_SIZE;   // z.B. 50 * 10 = 500px
    canvas.height = CANVAS_HEIGHT * PIXEL_SIZE;
    
    // Bildglättung AUSSCHALTEN (wichtig für scharfe Pixel!)
    ctx.imageSmoothingEnabled = false;
    
    // Mit Weiß füllen (Standard-Hintergrund)
    ctx.fillStyle = '#FFFFFF';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
}
```

**Was passiert hier:**
- `PIXEL_SIZE = 10` bedeutet: Jeder logische Pixel wird 10×10 Bildschirm-Pixel groß
- `imageSmoothingEnabled = false` ist **ESSENTIELL** - ohne dieses bekommen Pixel weiche Ränder
- Die Canvas wird komplett weiß gefüllt (Startzustand)

**Wenn du die Canvas ändern möchtest, passiert HIER die Grundanpassung:**
- Canvas-Größe ändern? Hier anpassen
- Hintergrundfarbe anders? `#FFFFFF` ersetzen

---

## 2. 🎨 CUSTOM SHADER (Zeilen ~325-350)

**Relevanz: SEHR HOCH** - Bestimmt, wie jeder Pixel aussieht!

```javascript
function customShader(artX, artY, pixelData) {
    // Gib die tatsächliche Farbe des Pixels zurück
    return pixelData[Math.floor(artY)][artX];
}
```

**Was das bedeutet:**
- Diese Funktion wird **für JEDEN Pixel aufgerufen** (50×50 = 2500x mal)
- Input: `artX, artY` = Position des Pixels (z.B. 5, 10)
- Input: `pixelData` = Die ganze 2D-Matrix vom Server
- Output: Gibt die Farbe zurück (Hex-String wie `#FF0000`)

**WICHTIG: Das ist dein EINSTIEGSPUNKT für visuelle Effekte!**

**Beispiele für Änderungen:**
```javascript
// 1. Alle Pixel grün machen:
return "#00FF00";

// 2. Checkerboard-Muster:
if ((artX + artY) % 2 === 0) return "#000000";
return pixelData[Math.floor(artY)][artX];

// 3. Pixel dunkler machen (Gamma-Effekt):
const original = pixelData[Math.floor(artY)][artX];
const rgb = hexToRgb(original);
return rgbToHex(Math.floor(rgb.r * 0.7), Math.floor(rgb.g * 0.7), Math.floor(rgb.b * 0.7));
```

---

## 3. 🔄 VOLLSTÄNDIGES CANVAS-RENDERN (Zeilen ~365-410)

**Relevanz: KRITISCH** - Zeichnet alle Pixel auf den Bildschirm

```javascript
function renderFullCanvas(pixelData) {
    // Berechne Zoom/Pan-Bereich (Field of View)
    const fovWidth = fieldOfView.x2 - fieldOfView.x1;
    const fovHeight = fieldOfView.y2 - fieldOfView.y1;
    
    // Größe eines logischen Pixels auf dem Screen
    const screenPixelWidth = canvas.width / fovWidth;
    const screenPixelHeight = canvas.height / fovHeight;
    
    // NUR sichtbare Pixel rendern (Optimierung!)
    for (let y = startY; y < endY; y++) {
        for (let x = startX; x < endX; x++) {
            // Rufe customShader für diesen Pixel auf
            const color = customShader(x, y, pixelData);
            
            // Berechne Position auf Screen
            const screenX = (x - fieldOfView.x1) * screenPixelWidth;
            const screenY = (y - fieldOfView.y1) * screenPixelHeight;
            
            // ZEICHNE den Pixel!
            ctx.fillStyle = color;
            ctx.fillRect(screenX, screenY, screenPixelWidth, screenPixelHeight);
        }
    }
}
```

**Struktur & Ablauf:**

1. **Berechne sichtbaren Bereich** (wegen Zoom/Pan)
   - `fieldOfView.x1, y1` = Oben-Links
   - `fieldOfView.x2, y2` = Unten-Rechts

2. **Berechne Größe eines Pixels auf dem Screen**
   - Mit Zoom: Pixel werden größer/kleiner
   - `screenPixelWidth = canvas.width / fovWidth`
   - Wenn `fovWidth=5` und `canvas.width=500` → `screenPixelWidth=100px`

3. **Doppel-Schleife über alle Pixel**
   - Äußere Schleife: Y-Koordinaten
   - Innere Schleife: X-Koordinaten
   - **WICHTIG: Datenstruktur ist `pixelData[y][x]` (Y ZUERST!)**

4. **Rufe customShader auf** (deine visuelle Logik!)

5. **Zeichne ein Rechteck** für diesen Pixel
   - `ctx.fillRect(screenX, screenY, screenPixelWidth, screenPixelHeight)`

**Wenn du Canvas-Änderungen brauchst, hier anpassen:**
- Andere Zeichenmethode? (z.B. Kreis statt Rechteck)
- Pixelgrenzen zeichnen? (Hier ein schwarzes `strokeRect` hinzufügen)
- Transparenz? (Hier `ctx.globalAlpha = ...` setzen)

---

## 4. ⬅️➡️ INVERSE SHADER (Zeilen ~352-365)

**Relevanz: HOCH** - Konvertiert Maus-Klicks zu Pixel-Koordinaten

```javascript
function inverseShader(screenX, screenY, screenWidth, screenHeight) {
    const windowWidth = fieldOfView.x2 - fieldOfView.x1;
    const windowHeight = fieldOfView.y2 - fieldOfView.y1;
    
    // Inverse Mathematik: Screen → Pixel-Art
    const artX = Math.floor((screenX / screenWidth) * windowWidth) + fieldOfView.x1;
    const artY = Math.floor((screenY / screenHeight) * windowHeight) + fieldOfView.y1;
    
    return { x: artX, y: artY };
}
```

**Was passiert hier:**

Beispiel: Du klickst auf Position (100, 100) auf dem Screen
- `screenWidth = 500`, `screenHeight = 500`
- `windowWidth = 50` (ganze Canvas ist sichtbar, kein Zoom)
- `windowHeight = 50`

```
Rechnung:
artX = Math.floor((100 / 500) * 50) + 0
     = Math.floor(0.2 * 50) + 0
     = Math.floor(10) + 0
     = 10  ← Du hast Pixel (10, 10) geklickt!
```

**Mit Zoom/Pan:**
- `fieldOfView.x1 = 20` (nur rechts oben sichtbar)
- Dann wird `+ 20` addiert → Pixel-Koordinaten bleiben korrekt

**Kritische Stellen für Canvas-Änderungen:**
- Funktioniert die Maus-Interaktion nach deinen Shader-Änderungen?
- Hier musst du nicht ändern, WENN der customShader einfach nur Farbe ändert

---

## 5. 📥 PIXEL-DATEN LADEN (Zeilen ~465-480)

**Relevanz: HOCH** - Holt Daten vom Server und aktualisiert Canvas

```javascript
async function loadCanvasData() {
    try {
        const response = await fetch('/api/canvas');  // HTTP GET
        if (response.ok) {
            const data = await response.json();        // {width, height, pixels: [...]}
            updateChangedPixels(data.pixels);          // Render die Pixel!
            
            // UI-Status: Verbunden
            statusIndicator.classList.add('connected');
            statusText.textContent = 'Verbunden';
        }
    } catch (error) {
        // Fehler: Zeige Getrennt-Status
        statusIndicator.classList.remove('connected');
    }
}
```

**Datenfluss:**
1. **Fetch** → Server antwortet mit vollständiger Pixel-Matrix
2. **Parse JSON** → `data.pixels` ist 2D-Array
3. **updateChangedPixels()** → Ruft `renderFullCanvas()` auf
4. **Visuelle Aktualisierung!**

**Polling-Intervall (Zeile ~440):**
```javascript
const POLL_INTERVAL = 200;  // Alle 200ms neu laden
setInterval(loadCanvasData, POLL_INTERVAL);
```

---

## 6. 📤 PIXEL SENDEN (Zeilen ~483-510)

**Relevanz: MITTEL** - Sendet deine Änderung zum Server

```javascript
async function sendPixelUpdate(x, y, color) {
    const response = await fetch('/api/pixel', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ x, y, color })  // Wichtig: x, y, color!
    });
    
    if (response.ok) {
        // Sofort lokal aktualisieren (UI-Feedback)
        if (localPixelData) {
            localPixelData[y][x] = color;  // BEACHTE: [y][x] nicht [x][y]!
        }
    }
}
```

**Wichtige Details:**
- **Koordinaten:** `x` horizontal, `y` vertikal
- **Array-Zugriff:** `localPixelData[y][x]` ← Y ZUERST!
- **Farbe:** Hex-Format `#RRGGBB` (z.B. `#FF0000` = rot)

---

## 7. 🖱️ MAUS-KLICK HANDLER (Zeilen ~590-630)

**Relevanz: HOCH** - Reagiert auf deine Klicks

```javascript
canvas.addEventListener('click', function(event) {
    // 1. Konvertiere Screen-Koordinaten → Pixel-Art-Koordinaten
    const coords = getPixelCoordinates(event);
    
    // 2. Grenzprüfung
    if (coords.x >= 0 && coords.x < CANVAS_WIDTH && 
        coords.y >= 0 && coords.y < CANVAS_HEIGHT) {
        
        // 3. Öffne Farbwähler
        const colorInput = document.createElement('input');
        colorInput.type = 'color';
        colorInput.value = colorPicker.value;
        colorInput.click();  // ← System-Farbdialog!
        
        // 4. Bei Farbauswahl: Sende Update
        colorInput.addEventListener('change', function() {
            sendPixelUpdate(coords.x, coords.y, colorInput.value);
        });
    }
});
```

**Ablauf:**
1. Du klickst → `click` Event
2. Konvertiere Maus-Position zu Pixel-Koordinaten (mit `inverseShader`)
3. Prüfe ob Koordinaten gültig (in Canvas-Grenzen)
4. Öffne Browser-Farbwähler
5. Nach Auswahl → `sendPixelUpdate()` mit Server

---

## 8. 🔍 KOORDINATEN-ANZEIGE (Zeilen ~635-660)

**Relevanz: NIEDRIG** - Nur UI-Feedback

```javascript
canvas.addEventListener('mousemove', function(event) {
    if (!isPanning) {
        const coords = getPixelCoordinates(event);
        if (coords.x >= 0 && coords.x < CANVAS_WIDTH && 
            coords.y >= 0 && coords.y < CANVAS_HEIGHT) {
            coordDisplay.textContent = `${coords.x}, ${coords.y}`;
        }
    }
});
```

**Was es macht:**
- Wenn Maus über Canvas → Zeige aktuelle Pixel-Koordinaten
- Bei Maus weg → Reset zu `--,  --`

---

## 9. 🔎 ZOOM & PAN (Zeilen ~510-590)

**Relevanz: MITTEL** - Verändert das sichtbare Fenster

### Zoom (Mausrad):
```javascript
canvas.addEventListener('wheel', function(event) {
    // Zoom-Faktor: scroll down = 0.8 (rein), scroll up = 1.2 (raus)
    const zoomFactor = event.deltaY > 0 ? 0.8 : 1.2;
    
    // Berechne neuen Field of View
    const newFovWidth = currentFovWidth * zoomFactor;
    const newFovHeight = currentFovHeight * zoomFactor;
    
    // Grenzwerte: min 1 Pixel, max volle Canvas
    const boundedFovWidth = Math.max(1, Math.min(CANVAS_WIDTH, newFovWidth));
    
    // Zoom zentriert auf Mausposition
    fieldOfView.x1 = fovCenterX - (boundedFovWidth / 2);
    // ... usw
});
```

### Pan (Rechtsklick + Drag):
```javascript
canvas.addEventListener('mousedown', function(event) {
    if (event.button === 2) {  // Rechtsklick
        isPanning = true;
        panStartX = event.clientX;
    }
});

document.addEventListener('mousemove', function(event) {
    if (isPanning) {
        // Berechne Maus-Delta
        const deltaX = event.clientX - panStartX;
        
        // Konvertiere in Pixel-Art-Delta
        const artDeltaX = deltaX / pixelSize;
        
        // Verschiebe FOV
        fieldOfView.x1 = panStartFOV.x1 - artDeltaX;
    }
});
```

**Field of View (FOV) - Das Fenster:**
```
fieldOfView = {
    x1: 0,     // Linke Kante des sichtbaren Bereichs
    y1: 0,     // Obere Kante
    x2: 50,    // Rechte Kante
    y2: 50     // Untere Kante
}

Wenn kein Zoom:   FOV = komplette Canvas (0-50)
Bei 2x Zoom:      FOV = nur Viertel (z.B. 10-35)
```

---

## 📊 ZUSAMMENFASSUNG: Welche Stelle für welche Änderung?

| **Canvas-Änderung** | **Zu bearbeitende Stelle** | **Linie** |
|---|---|---|
| Farbeffekt (Shader) | `customShader()` | 325-350 |
| Größe des Canvas | `initCanvas()` + PIXEL_SIZE | 290-305 + 315 |
| Hintergrundfarbe | `initCanvas()` fillStyle | 301 |
| Zeichenmethode (Kreis statt Quadrat) | `renderFullCanvas()` in fillRect | 405 |
| Pixelgrenzen | `renderFullCanvas()` + strokeRect | 405 |
| Zoom/Pan-Verhalten | `wheel` + `mousemove` Events | 510-590 |
| Maus-Interaktion | Klick-Handler | 593-630 |
| Polling-Häufigkeit | `POLL_INTERVAL` | 440 |
