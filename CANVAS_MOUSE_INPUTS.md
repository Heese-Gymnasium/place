# Canvas Mouse Input Analysis - Vollständige Übersicht

Detaillierte Erklärung aller Maus-Interaktionen in der aktuellen `index.html`.

---

## 🖱️ ÜBERSICHT: Alle Mouse Events

| **Event** | **Trigger** | **Funktion** | **Zeilen** |
|---|---|---|---|
| `wheel` | Mausrad scrollen | Zoom in/out | 572-625 |
| `mousedown` (Rechts/Mittel) | Rechts- oder Mittelklick | Pan starten | 627-635 |
| `contextmenu` | Rechtsklick-Menü | Menü unterdrücken | 637-640 |
| `mousemove` (document) | Maus bewegt (global) | Canvas panning | 647-675 |
| `mouseup` (document) | Maustaste loslassen | Pan beenden | 677-679 |
| `click` | Linksklick auf Canvas | Pixel zeichnen (Farbdialog) | 685-722 |
| `mousemove` (canvas) | Maus über Canvas | Koordinaten anzeigen | 725-739 |
| `mouseleave` | Maus verlässt Canvas | Koordinaten zurücksetzen | 743-746 |

---

## 1. 🔄 WHEEL EVENT - Zoom (Zeilen 572-625)

**Trigger:** Mausrad nach oben/unten

```javascript
canvas.addEventListener('wheel', function(event) {
    event.preventDefault();  // Standard-Scroll blockieren
    
    // Zoom-Faktor bestimmen
    const zoomFactor = event.deltaY > 0 ? 0.8 : 1.2;
    // deltaY > 0 = nach unten scrollen = ZOOM IN  (FOV wird kleiner = 0.8)
    // deltaY < 0 = nach oben scrollen = ZOOM OUT (FOV wird größer = 1.2)
```

### Schritt-für-Schritt Prozess:

**1. Mausrad erkannt**
```javascript
event.deltaY > 0 ? 0.8 : 1.2;
```
- Scroll nach unten (`deltaY > 0`): `zoomFactor = 0.8` → FOV wird 20% kleiner → ZOOM IN
- Scroll nach oben (`deltaY < 0`): `zoomFactor = 1.2` → FOV wird 20% größer → ZOOM OUT

**2. Mausposition auslesen**
```javascript
const rect = canvas.getBoundingClientRect();
const screenX = event.clientX - rect.left;
const screenY = event.clientY - rect.top;

const artCoordsBefore = inverseShader(screenX, screenY, canvas.width, canvas.height);
```
- `getBoundingClientRect()` gibt Canvas-Position auf dem Screen
- `event.clientX/Y` ist die absolute Mausposition
- `screenX/Y` ist die Mausposition **relativ zur Canvas**
- `inverseShader()` konvertiert das zur Pixel-Art-Koordinate (wird zum Zoom-Mittelpunkt)

**3. Neuen Field of View berechnen**
```javascript
const currentFovWidth = fieldOfView.x2 - fieldOfView.x1;
const currentFovHeight = fieldOfView.y2 - fieldOfView.y1;

const newFovWidth = currentFovWidth * zoomFactor;
const newFovHeight = currentFovHeight * zoomFactor;
```
- Alte FOV-Größe: z.B. `50 × 50` (ganze Canvas)
- Mit `zoomFactor = 0.8`: neue FOV = `40 × 40` (kleinerer Bereich = stärker gezoomt)

**4. Zoom-Grenzen anwenden**
```javascript
const boundedFovWidth = Math.max(1, Math.min(CANVAS_WIDTH, newFovWidth));
const boundedFovHeight = Math.max(1, Math.min(CANVAS_HEIGHT, newFovHeight));
```
- Minimum: `1` Pixel (maximal gezoomt)
- Maximum: `CANVAS_WIDTH/HEIGHT` (ausgezoomt)
- Verhindert zu krasses Zoomen

**5. Neuer FOV zentriert auf Mausposition**
```javascript
const fovCenterX = artCoordsBefore.x;
const fovCenterY = artCoordsBefore.y;

let newX1 = fovCenterX - (boundedFovWidth / 2);
let newY1 = fovCenterY - (boundedFovHeight / 2);
```
- Der Pixel unter der Maus bleibt unter der Maus
- Der neue FOV wird um diesen Punkt zentriert

**6. Koordinaten innerhalb Canvas begrenzen**
```javascript
newX1 = Math.max(0, Math.min(CANVAS_WIDTH - boundedFovWidth, newX1));
newY1 = Math.max(0, Math.min(CANVAS_HEIGHT - boundedFovHeight, newY1));
```
- Verhindert, dass der sichtbare Bereich außerhalb der Canvas geht

**7. Field of View updaten und neurendern**
```javascript
fieldOfView.x1 = newX1;
fieldOfView.y1 = newY1;
fieldOfView.x2 = newX1 + boundedFovWidth;
fieldOfView.y2 = newY1 + boundedFovHeight;

renderFullCanvas(localPixelData);
```
- FOV wird auf die neue Größe gesetzt
- `renderFullCanvas()` zeichnet mit den neuen Koordinaten

### Beispiel: 10er Zoom
```
Anfang:
fieldOfView = {x1: 0, y1: 0, x2: 50, y2: 50}  // Ganze Canvas

User scrollt nach unten (ZOOM IN) mit Maus über Pixel (25, 25):
zoomFactor = 0.8
newFovWidth = 50 * 0.8 = 40

Neuer FOV zentriert auf (25, 25):
newX1 = 25 - (40 / 2) = 25 - 20 = 5
newY1 = 25 - (40 / 2) = 25 - 20 = 5

Result:
fieldOfView = {x1: 5, y1: 5, x2: 45, y2: 45}  // Bereich [5..45] sichtbar
```

---

## 2. 🖐️ MOUSEDOWN EVENT - Pan Start (Zeilen 627-635)

**Trigger:** Rechtsklick oder Mittelklick auf Canvas

```javascript
canvas.addEventListener('mousedown', function(event) {
    if (event.button === 2 || event.button === 1) {  // Welche Taste?
        // event.button: 0=Links, 1=Mittel, 2=Rechts
        
        isPanning = true;  // Pan-Mode aktivieren
        panStartX = event.clientX;  // Maus-Position speichern
        panStartY = event.clientY;
        panStartFOV = JSON.parse(JSON.stringify(fieldOfView));  // FOV Snapshot
        event.preventDefault();  // Standard-Verhalten blockieren
    }
});
```

### Was passiert hier:

**1. Button-Prüfung**
```javascript
event.button === 2 || event.button === 1
```
- `0` = Linksklick (wird hier ignoriert, das ist zum Zeichnen)
- `1` = Mittelklick → Pan starten
- `2` = Rechtsklick → Pan starten
- Nur diese zwei werden akzeptiert

**2. Pan-State initialisieren**
```javascript
isPanning = true;
```
- Flag wird gesetzt, damit `mousemove` Handler pan-Logik ausführt

**3. Startpunkte speichern**
```javascript
panStartX = event.clientX;
panStartY = event.clientY;
```
- Absolute Mausposition auf dem Screen
- Wird später in `mousemove` verwendet, um Delta zu berechnen

**4. FOV Snapshot**
```javascript
panStartFOV = JSON.parse(JSON.stringify(fieldOfView));
```
- **Wichtig:** `JSON.parse(JSON.stringify(...))` erstellt eine **tiefe Kopie**
- Ohne das würde die Referenz zum Objekt zeigen, das sich ständig ändert
- Speichert den FOV-Zustand **vor** dem Pan

**5. Event blockieren**
```javascript
event.preventDefault();
```
- Verhindert Browser-Standardverhalten (z.B. Text-Auswahl bei Drag)

---

## 3. 🚫 CONTEXTMENU EVENT - Rechtsklick-Menü blockieren (Zeilen 637-640)

**Trigger:** Rechtsklick erzeugt normalerweise ein Menü

```javascript
canvas.addEventListener('contextmenu', function(event) {
    event.preventDefault();  // Browser-Menü unterdrücken
});
```

**Warum?**
- Ohne das würde beim Rechtsklick das Browser-Kontextmenü erscheinen
- Würde Pan unterbrechen/störend wirken

---

## 4. 🎯 MOUSEMOVE EVENT (DOCUMENT) - Pan durchführen (Zeilen 647-675)

**Trigger:** Maus bewegt sich (global, nicht nur auf Canvas)

```javascript
document.addEventListener('mousemove', function(event) {
    if (!isPanning) return;  // Nur wenn Pan aktiv ist
    
    // Maus-Delta berechnen
    const deltaX = event.clientX - panStartX;
    const deltaY = event.clientY - panStartY;
```

### Schritt-für-Schritt:

**1. Pan-Check**
```javascript
if (!isPanning) return;
```
- Nichts tun, wenn kein Pan läuft
- Hört auf `document` statt nur `canvas`, um auch außerhalb zu reagieren

**2. Maus-Movement berechnen**
```javascript
const deltaX = event.clientX - panStartX;
const deltaY = event.clientY - panStartY;
```
- Wie viele Screen-Pixel hat sich die Maus bewegt?
- Beispiel: Maus von (100, 100) zu (150, 120)
  - `deltaX = 150 - 100 = 50px`
  - `deltaY = 120 - 100 = 20px`

**3. Screen-Pixel in Pixel-Art-Pixel konvertieren**
```javascript
const fovWidth = fieldOfView.x2 - fieldOfView.x1;
const fovHeight = fieldOfView.y2 - fieldOfView.y1;

const pixelSize = canvas.width / fovWidth;
const artDeltaX = deltaX / pixelSize;
const artDeltaY = deltaY / pixelSize;
```

**Beispiel:**
```
canvas.width = 500px (Bildschirm-Pixel)
fovWidth = 50 (Pixel-Art-Pixel sichtbar)
pixelSize = 500 / 50 = 10px pro Pixel-Art-Pixel

Wenn User 50px draggt:
artDeltaX = 50 / 10 = 5 Pixel-Art-Pixel
```

**4. Field of View verschieben**
```javascript
fieldOfView.x1 = Math.max(0, Math.min(CANVAS_WIDTH - fovWidth, panStartFOV.x1 - artDeltaX));
fieldOfView.y1 = Math.max(0, Math.min(CANVAS_HEIGHT - fovHeight, panStartFOV.y1 - artDeltaY));
fieldOfView.x2 = fieldOfView.x1 + fovWidth;
fieldOfView.y2 = fieldOfView.y1 + fovHeight;
```

**Breaking it down:**
```javascript
panStartFOV.x1 - artDeltaX
// Wenn panStartFOV.x1 = 10 und artDeltaX = 5:
// 10 - 5 = 5  (FOV bewegt sich nach links)
```

Grenzen:
- `Math.max(0, ...)` - nicht unter 0
- `Math.min(CANVAS_WIDTH - fovWidth, ...)` - nicht über rechte Kante
- Verhindert Pan außerhalb der Canvas

**5. Neurendern**
```javascript
if (localPixelData) {
    renderFullCanvas(localPixelData);
}
```
- Zeichnet mit neuem FOV (neue sichtbare Bereich)

---

## 5. ⬆️ MOUSEUP EVENT - Pan beenden (Zeilen 677-679)

**Trigger:** Maustaste wird losgelassen

```javascript
document.addEventListener('mouseup', function() {
    isPanning = false;  // Pan-Mode deaktivieren
});
```

**Was passiert:**
- `isPanning` wird auf `false` gesetzt
- Nächstes `mousemove` Event tut nichts mehr (wegen der `if (!isPanning) return` Prüfung)

---

## 6. 🎨 CLICK EVENT - Pixel zeichnen (Zeilen 685-722)

**Trigger:** Linksklick auf Canvas

```javascript
canvas.addEventListener('click', function(event) {
    const coords = getPixelCoordinates(event);
    
    if (coords.x >= 0 && coords.x < CANVAS_WIDTH && 
        coords.y >= 0 && coords.y < CANVAS_HEIGHT) {
```

### Schritt-für-Schritt:

**1. Koordinaten umwandeln**
```javascript
const coords = getPixelCoordinates(event);
```
- Nutzt `inverseShader()` um Screen-Koordinaten in Pixel-Art-Koordinaten zu konvertieren
- Berücksichtigt aktuellen FOV (Zoom/Pan)

**2. Grenzen prüfen**
```javascript
if (coords.x >= 0 && coords.x < CANVAS_WIDTH && 
    coords.y >= 0 && coords.y < CANVAS_HEIGHT) {
```
- Nur wenn Klick auf valide Pixel-Koordinaten

**3. Temporären Farbwähler erstellen**
```javascript
const colorInput = document.createElement('input');
colorInput.type = 'color';
colorInput.value = colorPicker.value;  // Aktuelle Farbe als Vorgabe
colorInput.click();  // Browser-Farbdialog öffnen
```
- `document.createElement('input')` erstellt unsichtbares Input-Element
- `type='color'` öffnet systemeigenen Farbdialog
- `.click()` triggert den Dialog sofort

**4. Auf Farbauswahl reagieren**
```javascript
colorInput.addEventListener('change', function() {
    const selectedColor = colorInput.value;
    sendPixelUpdate(coords.x, coords.y, selectedColor);
    colorPicker.value = selectedColor;
    colorPreview.style.backgroundColor = selectedColor;
});
```
- Bei Farbauswahl: `sendPixelUpdate()` an Server
- Hauppfarben-Picker wird auch aktualisiert
- Color Preview wird gesetzt

**5. Aufräumen**
```javascript
setTimeout(function() {
    colorInput.remove();
}, 1000);
```
- Nach 1 Sekunde wird das temporäre Input-Element gelöscht
- Verhindert Memory Leaks

### Wichtig: Warum `document` Event Listeners?

**`mousemove` und `mouseup` hören auf `document`, nicht auf `canvas`:**

```javascript
document.addEventListener('mousemove', ...)  // Global
canvas.addEventListener('mousemove', ...)    // Nur über Canvas
document.addEventListener('mouseup', ...)    // Global
```

**Warum?**
- User kann Pan starten auf Canvas, dann Maus rausbewegen
- Ohne `document`-Listener würde Pan stoppen sobald Maus Canvas verlässt
- Mit `document`-Listener: Pan funktioniert überall auf der Seite

---

## 7. 📍 MOUSEMOVE EVENT (CANVAS) - Koordinaten anzeigen (Zeilen 725-739)

**Trigger:** Maus bewegt sich über Canvas

```javascript
canvas.addEventListener('mousemove', function(event) {
    if (!isPanning) {  // Nur wenn nicht panning
        const coords = getPixelCoordinates(event);
        
        if (coords.x >= 0 && coords.x < CANVAS_WIDTH && 
            coords.y >= 0 && coords.y < CANVAS_HEIGHT) {
            coordDisplay.textContent = `${coords.x}, ${coords.y}`;
        } else {
            coordDisplay.textContent = '--, --';
        }
    }
});
```

**Was passiert:**
- Wenn nicht gepannt: Zeige aktuelle Koordinaten
- Wenn gepannt: Zeige nichts (störend beim Panning)
- Out-of-bounds Koordinaten: Zeige `--,  --`

---

## 8. 🚪 MOUSELEAVE EVENT - Koordinaten zurücksetzen (Zeilen 743-746)

**Trigger:** Maus verlässt Canvas

```javascript
canvas.addEventListener('mouseleave', function() {
    coordDisplay.textContent = '--, --';
});
```

**Was passiert:**
- Koordinaten-Anzeige wird zurückgesetzt
- UI-Feedback dass Maus nicht mehr über Canvas ist

---

## 📊 KOORDINATEN-UMWANDLUNG: inverseShader()

Diese Funktion ist kritisch für alle Mouse Events:

```javascript
function inverseShader(screenX, screenY, screenWidth, screenHeight) {
    const windowWidth = fieldOfView.x2 - fieldOfView.x1;
    const windowHeight = fieldOfView.y2 - fieldOfView.y1;
    
    const artX = Math.floor((screenX / screenWidth) * windowWidth) + fieldOfView.x1;
    const artY = Math.floor((screenY / screenHeight) * windowHeight) + fieldOfView.y1;
    
    return { x: artX, y: artY };
}
```

### Formel Erklärung:

```
INPUT:
  screenX = 100 (Maus-X auf Screen)
  screenWidth = 500 (Canvas-Breite in Bildschirm-Pixeln)
  fieldOfView = {x1: 10, x2: 40, ...}  (sichtbarer Bereich mit Zoom)

RECHNUNG:
  windowWidth = 40 - 10 = 30  (30 Pixel-Art-Pixel sichtbar)
  
  normalisiert = 100 / 500 = 0.2  (20% von Canvas-Breite)
  relative_pos = 0.2 * 30 = 6  (6 Pixel-Art-Pixel von FOV-Anfang)
  
  artX = 6 + 10 = 16  (6 + FOV-Offset)

OUTPUT:
  x: 16  (Pixel-Art-Koordinate in originaler Canvas)
```

### Mit Zoom-Beispiel:

```
Ohne Zoom (FOV = gesamte Canvas):
  fieldOfView = {x1: 0, x2: 50, y1: 0, y2: 50}
  Klick bei (50% Screen-Position) = Pixel 25 Pixel-Art

Mit 2x Zoom (nur Viertel sichtbar):
  fieldOfView = {x1: 10, x2: 35, y1: 10, y2: 35}
  Klick bei (50% Screen-Position) = Pixel 22 Pixel-Art
  → Weil FOV nur [10..35] ist, mittelpunkt = 22.5 ≈ 22
```

---

## 🔄 EVENT REIHENFOLGE: Typisches Szenario

### Szenario 1: User zeichnet einen Pixel

```
1. user klickt auf Canvas
   → click event
   → getPixelCoordinates() nutzt inverseShader()
   → Farbdialog öffnet
   
2. user wählt Farbe
   → colorInput.addEventListener('change') triggert
   → sendPixelUpdate() sendet an Server
   → localPixelData wird sofort aktualisiert
   → Nächster Poll zeigt neue Farbe
```

### Szenario 2: User zoomed und pannt

```
1. wheel event
   → zoomFactor berechnet
   → neuer FOV berechnet
   → renderFullCanvas()
   
2. mousedown mit Rechtsklick
   → isPanning = true
   → panStartX/Y speichern
   → panStartFOV speichern
   
3. mousemove (während Drag)
   → deltaX/Y berechnet
   → neuer FOV berechnet
   → renderFullCanvas()
   
4. mouseup
   → isPanning = false
   → mousemove macht jetzt nichts mehr
```

### Szenario 3: Mouse über Canvas mit Koordinaten-Anzeige

```
1. mousemove über Canvas
   → !isPanning = true
   → getPixelCoordinates()
   → coordDisplay.textContent = "x, y"
   
2. mouseleave Canvas
   → coordDisplay.textContent = "--, --"
```

---

## ⚠️ WICHTIGE HINWEISE

### getPixelCoordinates() vs inverseShader()

Beide machen das gleiche:

```javascript
function getPixelCoordinates(event) {
    const rect = canvas.getBoundingClientRect();
    const screenX = event.clientX - rect.left;
    const screenY = event.clientY - rect.top;
    
    return inverseShader(screenX, screenY, canvas.width, canvas.height);
}
```

- `getPixelCoordinates()` ist ein Wrapper
- Nutzt intern `inverseShader()`
- Konvertiert `event.clientX/Y` zu Canvas-relativ

### Pan und Koordinaten-Anzeige

```javascript
if (!isPanning) {  // Koordinaten nur ohne Pan
    coordDisplay.textContent = `${coords.x}, ${coords.y}`;
}
```

- Verhindert, dass Koordinaten flackern während Panning
- Verbessert User Experience

### Context Menu Prevention

```javascript
canvas.addEventListener('contextmenu', event.preventDefault());
```

- Notwendig für Rechtsklick-Panning
- Browser-Kontextmenü würde Pan unterbrechen

---

## 📋 SCHNELLE REFERENZ

| **Aktion** | **Events** | **Ergebnis** |
|---|---|---|
| Scroll Rad | `wheel` | Zoom in/out, FOV ändert sich |
| Rechtsklick + Drag | `mousedown` → `mousemove` → `mouseup` | Pan, FOV verschiebt sich |
| Linksklick | `click` | Farbdialog, `sendPixelUpdate()` |
| Maus über Canvas | `mousemove` | Koordinaten aktualisieren |
| Maus verlässt | `mouseleave` | Koordinaten zurücksetzen |

