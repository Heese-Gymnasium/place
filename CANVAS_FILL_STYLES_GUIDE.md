# Canvas Fill & Style - Vollständiger Guide

Ein umfassendes Nachschlagewerk für alle Möglichkeiten, Canvas-Bereiche zu füllen und zu stylen.

---

## 1. 🎨 GRUNDLAGEN: ctx.fillStyle

**Was ist `fillStyle`?**
- Definiert die Farbe/das Muster für `fillRect()`, `fillText()`, `fill()` usw.
- Muss VOR der Zeichenfunktion gesetzt werden
- Bleibt aktiv, bis es überschrieben wird

### 1.1 Einfache Farben

```javascript
// Hex-Farbcode (wie in Pixel Canvas)
ctx.fillStyle = '#FFFFFF';        // Weiß
ctx.fillStyle = '#FF0000';        // Rot
ctx.fillStyle = '#00FF00';        // Grün
ctx.fillStyle = '#0000FF';        // Blau

// RGB-Notation
ctx.fillStyle = 'rgb(255, 0, 0)'; // Rot
ctx.fillStyle = 'rgb(0, 255, 0)'; // Grün

// RGBA-Notation (mit Transparenz!)
ctx.fillStyle = 'rgba(255, 0, 0, 0.5)';  // Halbdurchsichtiges Rot (50%)
ctx.fillStyle = 'rgba(0, 0, 0, 0.3)';    // 30% Deckkraft

// Named Colors
ctx.fillStyle = 'red';      // Benannte Farben
ctx.fillStyle = 'blue';
ctx.fillStyle = 'transparent';  // Transparent

// HSL-Notation (Farbton, Sättigung, Helligkeit)
ctx.fillStyle = 'hsl(0, 100%, 50%)';    // Rot
ctx.fillStyle = 'hsl(120, 100%, 50%)';  // Grün
ctx.fillStyle = 'hsl(240, 100%, 50%)';  // Blau
```

---

## 2. 🌈 GRADIENT (Farbverlauf)

### 2.1 Linear Gradient (Linearer Verlauf)

```javascript
// Gradient erstellen: von (x1,y1) zu (x2,y2)
const gradient = ctx.createLinearGradient(x1, y1, x2, y2);

// Farbstops hinzufügen (0.0 = Start, 1.0 = Ende)
gradient.addColorStop(0.0, '#FF0000');    // Start: Rot
gradient.addColorStop(0.5, '#FFFF00');    // Mitte: Gelb
gradient.addColorStop(1.0, '#0000FF');    // Ende: Blau

// Gradient als fillStyle verwenden
ctx.fillStyle = gradient;
ctx.fillRect(0, 0, canvas.width, canvas.height);
```

**Beispiel 1: Horizontaler Verlauf (links → rechts)**
```javascript
const grad = ctx.createLinearGradient(0, 0, 500, 0);
grad.addColorStop(0, '#FF0000');
grad.addColorStop(1, '#0000FF');
ctx.fillStyle = grad;
ctx.fillRect(0, 0, 500, 500);
```

**Beispiel 2: Vertikaler Verlauf (oben → unten)**
```javascript
const grad = ctx.createLinearGradient(0, 0, 0, 500);
grad.addColorStop(0, '#00FF00');
grad.addColorStop(1, '#FFFFFF');
ctx.fillStyle = grad;
ctx.fillRect(0, 0, 500, 500);
```

**Beispiel 3: Diagonaler Verlauf**
```javascript
const grad = ctx.createLinearGradient(0, 0, 500, 500);
grad.addColorStop(0, '#FF00FF');
grad.addColorStop(0.5, '#FFFF00');
grad.addColorStop(1, '#00FFFF');
ctx.fillStyle = grad;
ctx.fillRect(0, 0, 500, 500);
```

### 2.2 Radial Gradient (Kreis-Verlauf)

```javascript
// Gradient von Kreis 1 zu Kreis 2
// createRadialGradient(x1, y1, r1, x2, y2, r2)
const gradient = ctx.createRadialGradient(250, 250, 10, 250, 250, 200);

gradient.addColorStop(0, '#FFFFFF');  // Innen: Weiß
gradient.addColorStop(1, '#000000');  // Außen: Schwarz

ctx.fillStyle = gradient;
ctx.fillRect(0, 0, 500, 500);
```

**Beispiel: Sonnen-Effekt**
```javascript
const grad = ctx.createRadialGradient(250, 250, 0, 250, 250, 250);
grad.addColorStop(0, '#FFFF00');      // Gelb in der Mitte
grad.addColorStop(0.5, '#FF6600');    // Orange
grad.addColorStop(1, '#FF0000');      // Rot außen

ctx.fillStyle = grad;
ctx.fillRect(0, 0, 500, 500);
```

### 2.3 Conic Gradient (Winkel-Verlauf)

```javascript
// Winkel-Verlauf um einen Punkt
const gradient = ctx.createConicGradient(0, 250, 250);
// Parameter: (startWinkel, centerX, centerY)

gradient.addColorStop(0, 'red');
gradient.addColorStop(0.25, 'yellow');
gradient.addColorStop(0.5, 'green');
gradient.addColorStop(0.75, 'blue');
gradient.addColorStop(1, 'red');

ctx.fillStyle = gradient;
ctx.fillRect(0, 0, 500, 500);
```

---

## 3. 🖼️ PATTERNS (Muster/Texturen)

```javascript
// Pattern erstellen aus Bild/Canvas
const pattern = ctx.createPattern(imageElement, repetition);

// repetition kann sein:
// 'repeat'       - Wiederhole in alle Richtungen (Standard)
// 'repeat-x'     - Nur horizontal
// 'repeat-y'     - Nur vertikal
// 'no-repeat'    - Nur einmal
```

**Beispiel 1: Schachbrett-Muster (programmiert)**
```javascript
// Kleine Canvas für Muster erstellen
const patternCanvas = document.createElement('canvas');
patternCanvas.width = 20;
patternCanvas.height = 20;

const pctx = patternCanvas.getContext('2d');

// Schachbrett-Felder
pctx.fillStyle = '#000000';
pctx.fillRect(0, 0, 10, 10);
pctx.fillRect(10, 10, 10, 10);

pctx.fillStyle = '#FFFFFF';
pctx.fillRect(10, 0, 10, 10);
pctx.fillRect(0, 10, 10, 10);

// Pattern daraus erstellen
const pattern = ctx.createPattern(patternCanvas, 'repeat');
ctx.fillStyle = pattern;
ctx.fillRect(0, 0, canvas.width, canvas.height);
```

**Beispiel 2: Streifen-Muster**
```javascript
const patternCanvas = document.createElement('canvas');
patternCanvas.width = 10;
patternCanvas.height = 100;

const pctx = patternCanvas.getContext('2d');
pctx.fillStyle = '#FF0000';
pctx.fillRect(0, 0, 5, 100);
pctx.fillStyle = '#0000FF';
pctx.fillRect(5, 0, 5, 100);

const pattern = ctx.createPattern(patternCanvas, 'repeat');
ctx.fillStyle = pattern;
ctx.fillRect(0, 0, canvas.width, canvas.height);
```

---

## 4. 📦 FILL-FUNKTIONEN (Wie wird gefüllt?)

### 4.1 fillRect() - Rechteck (STANDARD)

```javascript
ctx.fillStyle = '#FF0000';
ctx.fillRect(x, y, width, height);

// Beispiel: Rechteck von (50, 50) mit Größe 100×100
ctx.fillRect(50, 50, 100, 100);
```

### 4.2 fillText() - Text füllen

```javascript
ctx.fillStyle = '#000000';
ctx.font = '30px Arial';
ctx.fillText('Hallo!', 100, 50);

// Mit Maximale Breite
ctx.fillText('Sehr langer Text', 0, 50, 200);  // Max 200px breit
```

### 4.3 fill() - Pfad füllen

```javascript
ctx.beginPath();
ctx.moveTo(100, 100);
ctx.lineTo(200, 100);
ctx.lineTo(150, 200);
ctx.closePath();

ctx.fillStyle = '#00FF00';
ctx.fill();  // Füllt das Dreieck
```

### 4.4 Arc/Circle - Kreis füllen

```javascript
ctx.beginPath();
ctx.arc(centerX, centerY, radius, startAngle, endAngle);
ctx.fillStyle = '#0000FF';
ctx.fill();

// Beispiel: Kreis im Mittelpunkt
ctx.beginPath();
ctx.arc(250, 250, 50, 0, Math.PI * 2);
ctx.fillStyle = 'red';
ctx.fill();
```

### 4.5 Ellipse - Ellipse füllen

```javascript
ctx.beginPath();
ctx.ellipse(x, y, radiusX, radiusY, rotation, startAngle, endAngle);
ctx.fillStyle = '#FF00FF';
ctx.fill();

// Beispiel: Ellipse
ctx.beginPath();
ctx.ellipse(250, 250, 100, 50, 0, 0, Math.PI * 2);
ctx.fillStyle = 'purple';
ctx.fill();
```

### 4.6 clearRect() - Bereich leeren (Löschen)

```javascript
// Bereich mit transparent füllen
ctx.clearRect(x, y, width, height);

// Beispiel: Rechteck löschen
ctx.clearRect(50, 50, 100, 100);
```

### 4.7 fillPolygon() - Polygon (Vieleck)

```javascript
function fillPolygon(points) {
    ctx.beginPath();
    ctx.moveTo(points[0].x, points[0].y);
    for (let i = 1; i < points.length; i++) {
        ctx.lineTo(points[i].x, points[i].y);
    }
    ctx.closePath();
    ctx.fill();
}

// Verwendung: 5er-Stern
const starPoints = [
    {x: 250, y: 0},
    {x: 310, y: 190},
    {x: 500, y: 190},
    {x: 345, y: 310},
    {x: 405, y: 500},
    {x: 250, y: 380},
    {x: 95, y: 500},
    {x: 155, y: 310},
    {x: 0, y: 190},
    {x: 190, y: 190}
];

ctx.fillStyle = '#FFD700';  // Gold
fillPolygon(starPoints);
```

---

## 5. 🎯 KOMBINATIONEN & SPEZIALEFFEKTE

### 5.1 Transparenz mit globalAlpha

```javascript
ctx.globalAlpha = 0.5;  // 50% Transparenz für alles folgende
ctx.fillStyle = '#FF0000';
ctx.fillRect(0, 0, 100, 100);

ctx.globalAlpha = 0.2;  // 20% Transparenz
ctx.fillRect(100, 0, 100, 100);

ctx.globalAlpha = 1.0;  // Zurück zu 100% (normal)
```

### 5.2 Blending Modes (Überblendungsmodi)

```javascript
// globalCompositeOperation bestimmt wie neue Zeichnungen sich mit bestehenden mischen
ctx.globalCompositeOperation = 'source-over';  // Standard (neue oben)
ctx.globalCompositeOperation = 'multiply';     // Multiplizieren
ctx.globalCompositeOperation = 'screen';       // Screen
ctx.globalCompositeOperation = 'overlay';      // Overlay
ctx.globalCompositeOperation = 'lighten';      // Aufhellen
ctx.globalCompositeOperation = 'darken';       // Abdunkeln
ctx.globalCompositeOperation = 'color-dodge';  // Dodge
ctx.globalCompositeOperation = 'color-burn';   // Burn

// Beispiel: Additives Blending
ctx.globalCompositeOperation = 'lighter';
ctx.fillStyle = 'rgba(255, 0, 0, 0.5)';
ctx.fillRect(0, 0, 100, 100);

ctx.fillStyle = 'rgba(0, 0, 255, 0.5)';
ctx.fillRect(50, 50, 100, 100);  // Überlagert = Magenta
```

### 5.3 Schatten

```javascript
ctx.shadowColor = '#000000';
ctx.shadowBlur = 10;
ctx.shadowOffsetX = 5;
ctx.shadowOffsetY = 5;

ctx.fillStyle = '#FF0000';
ctx.fillRect(100, 100, 100, 100);  // Hat Schatten

// Schatten ausmachen
ctx.shadowColor = 'transparent';
```

### 5.4 Clip Region (Bereich begrenzen)

```javascript
ctx.beginPath();
ctx.arc(250, 250, 100, 0, Math.PI * 2);
ctx.clip();  // Nur noch inner vom Kreis sichtbar

ctx.fillStyle = 'red';
ctx.fillRect(0, 0, 500, 500);  // Wird als Kreis angezeigt!
```

---

## 6. ⚙️ FORTGESCHRITTENE TECHNIKEN

### 6.1 ImageData - Pixel direkt manipulieren

```javascript
// Alle Pixel auslesen
const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
const data = imageData.data;  // Array: [R, G, B, A, R, G, B, A, ...]

// Beispiel: Alles rot machen
for (let i = 0; i < data.length; i += 4) {
    data[i] = 255;      // Rot
    data[i + 1] = 0;    // Grün
    data[i + 2] = 0;    // Blau
    data[i + 3] = 255;  // Alpha
}

// Zurück auf Canvas
ctx.putImageData(imageData, 0, 0);
```

### 6.2 Texturen mit Bildern

```javascript
// Bild laden
const img = new Image();
img.src = 'mein-bild.png';
img.onload = function() {
    const pattern = ctx.createPattern(img, 'repeat');
    ctx.fillStyle = pattern;
    ctx.fillRect(0, 0, canvas.width, canvas.height);
};
```

### 6.3 Canvas als Texture nutzen

```javascript
// Offscreen Canvas erstellen
const offscreenCanvas = document.createElement('canvas');
offscreenCanvas.width = 50;
offscreenCanvas.height = 50;

const offCtx = offscreenCanvas.getContext('2d');
offCtx.fillStyle = '#FF0000';
offCtx.arc(25, 25, 20, 0, Math.PI * 2);
offCtx.fill();

// Als Pattern nutzen
const pattern = ctx.createPattern(offscreenCanvas, 'repeat');
ctx.fillStyle = pattern;
ctx.fillRect(0, 0, 500, 500);
```

### 6.4 Noise Pattern (Rauschen)

```javascript
function createNoisePattern(width, height) {
    const noiseCanvas = document.createElement('canvas');
    noiseCanvas.width = width;
    noiseCanvas.height = height;
    
    const nctx = noiseCanvas.getContext('2d');
    const imageData = nctx.createImageData(width, height);
    const data = imageData.data;
    
    for (let i = 0; i < data.length; i += 4) {
        const gray = Math.random() * 255;
        data[i] = gray;      // R
        data[i + 1] = gray;  // G
        data[i + 2] = gray;  // B
        data[i + 3] = 255;   // A
    }
    
    nctx.putImageData(imageData, 0, 0);
    return nctx.createPattern(noiseCanvas, 'repeat');
}

ctx.fillStyle = createNoisePattern(100, 100);
ctx.fillRect(0, 0, 500, 500);
```

---

## 7. 🎓 PRAKTISCHE BEISPIELE FÜR PIXEL CANVAS

### Beispiel 1: Farbverlauf-Effekt in customShader

```javascript
function customShader(artX, artY, pixelData) {
    const baseColor = pixelData[Math.floor(artY)][artX];
    
    // Farbverlauf je nach Position
    const hue = (artX / CANVAS_WIDTH * 360);
    const brightness = (artY / CANVAS_HEIGHT * 100);
    
    return `hsl(${hue}, 100%, ${brightness}%)`;
}
```

### Beispiel 2: Pixel mit Outline in renderFullCanvas

```javascript
function renderFullCanvas(pixelData) {
    // ... bestehendes Code ...
    
    for (let y = startY; y < endY; y++) {
        for (let x = startX; x < endX; x++) {
            const color = customShader(x, y, pixelData);
            
            const screenX = (x - fieldOfView.x1) * screenPixelWidth;
            const screenY = (y - fieldOfView.y1) * screenPixelHeight;
            
            // Fülle Pixel
            ctx.fillStyle = color;
            ctx.fillRect(screenX, screenY, screenPixelWidth, screenPixelHeight);
            
            // Zeichne Outline
            ctx.strokeStyle = 'rgba(0, 0, 0, 0.3)';
            ctx.lineWidth = 1;
            ctx.strokeRect(screenX, screenY, screenPixelWidth, screenPixelHeight);
        }
    }
}
```

### Beispiel 3: Checker-Pattern im Hintergrund

```javascript
function initCanvas() {
    canvas.width = CANVAS_WIDTH * PIXEL_SIZE;
    canvas.height = CANVAS_HEIGHT * PIXEL_SIZE;
    
    ctx.imageSmoothingEnabled = false;
    
    // Erstelle Checker-Pattern für Transparenz-Indikation
    const checkerSize = 10;
    for (let y = 0; y < canvas.height; y += checkerSize) {
        for (let x = 0; x < canvas.width; x += checkerSize) {
            const isWhite = ((x / checkerSize) + (y / checkerSize)) % 2 === 0;
            ctx.fillStyle = isWhite ? '#FFFFFF' : '#EEEEEE';
            ctx.fillRect(x, y, checkerSize, checkerSize);
        }
    }
}
```

### Beispiel 4: Gradient-Hintergrund mit Shadow

```javascript
function initCanvas() {
    canvas.width = CANVAS_WIDTH * PIXEL_SIZE;
    canvas.height = CANVAS_HEIGHT * PIXEL_SIZE;
    
    ctx.imageSmoothingEnabled = false;
    
    // Linearer Gradient
    const gradient = ctx.createLinearGradient(0, 0, 0, canvas.height);
    gradient.addColorStop(0, '#1a1a2e');
    gradient.addColorStop(1, '#16213e');
    
    ctx.fillStyle = gradient;
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    
    // Optional: Schatten-Overlay
    ctx.globalAlpha = 0.1;
    ctx.fillStyle = '#000000';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    ctx.globalAlpha = 1.0;
}
```

---

## 📋 KURZREFERENZ: Häufige Kombinationen

| **Effekt** | **Code** | **Verwendung** |
|---|---|---|
| Einfache Farbe | `ctx.fillStyle = '#FF0000'; ctx.fillRect(...)` | Standard |
| Mit Transparenz | `ctx.fillStyle = 'rgba(255,0,0,0.5)'; ctx.fillRect(...)` | Semi-transparent |
| H-Gradient | `ctx.createLinearGradient(0,0,w,0)` | Farbverlauf links→rechts |
| V-Gradient | `ctx.createLinearGradient(0,0,0,h)` | Farbverlauf oben→unten |
| Radial | `ctx.createRadialGradient(cx,cy,r1,cx,cy,r2)` | Strahlend |
| Muster | `ctx.createPattern(canvas/img, 'repeat')` | Wiederholtes Muster |
| Kreis | `ctx.arc(...); ctx.fill()` | Rund |
| Mit Outline | `ctx.fill(); ctx.stroke()` | Umriss |
| Mit Schatten | `ctx.shadowColor/Blur/Offset` | 3D-Effekt |
| Blend Mode | `ctx.globalCompositeOperation = '...'` | Überblendung |

---

## 🔗 Weitere Ressourcen

- [MDN Canvas API](https://developer.mozilla.org/en-US/docs/Web/API/Canvas_API)
- [Canvas Cheatsheet](https://www.cheatsheetcode.com/canvas/)
- [Color Stop Reference](https://developer.mozilla.org/en-US/docs/Web/API/CanvasGradient/addColorStop)
