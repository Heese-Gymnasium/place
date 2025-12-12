/**
 * ================================================================
 * PIXEL CANVAS - CLIENTSEITIGES JAVASCRIPT
 * ================================================================
 * 
 * Dieses Script verwaltet:
 * - Die Canvas-Darstellung und Pixel-Rendering
 * - Benutzerinteraktionen (Klicks, Mausbewegungen)
 * - Server-Kommunikation über HTTP-Anfragen
 * - Regelmäßige Updates durch Polling
 */

// ================================================================
// KONSTANTEN UND KONFIGURATION
// ================================================================

// Canvas-Dimensionen vom Server (werden gesetzt durch initPixelCanvas)
let CANVAS_WIDTH = 50;
let CANVAS_HEIGHT = 50;

// Größe eines einzelnen Pixels auf dem Bildschirm (in CSS-Pixeln)
// Erhöht die Sichtbarkeit der einzelnen Pixel
const PIXEL_SIZE = 10;

// Polling-Intervall in Millisekunden für regelmäßige Updates
const POLL_INTERVAL = 200;

// ================================================================
// DOM-ELEMENTE REFERENZIEREN
// ================================================================

// Canvas und 2D-Kontext für Zeichenoperationen
let canvas = null;
let ctx = null;

// UI-Elemente
let colorPicker = null;
let colorPreview = null;
let statusIndicator = null;
let statusText = null;
let coordDisplay = null;

// Speichert den aktuellen lokalen Zustand der Pixel
let localPixelData = null;

// ================================================================
// ZOOM UND PAN VERWALTUNG
// ================================================================

// Field of View - definiert welcher Bereich der Pixel-Art sichtbar ist
let fieldOfView = {
    x1: 0,                  // Linke Kante
    y1: 0,                  // Obere Kante
    x2: CANVAS_WIDTH,       // Rechte Kante
    y2: CANVAS_HEIGHT       // Untere Kante
};

// Zoom-Faktor und Pan-Tracking
let isPanning = false;
let panStartX = 0;
let panStartY = 0;
let panStartFOV = { x1: 0, y1: 0, x2: CANVAS_WIDTH, y2: CANVAS_HEIGHT };

// Admin-Mode (kann von außen gesetzt werden, default: false)
let adminMode = false;

// ================================================================
// INITIALISIERUNG
// ================================================================

/**
 * Initialisiert die Canvas-Anwendung mit den gegebenen Dimensionen
 * @param {number} width - Canvas-Breite
 * @param {number} height - Canvas-Höhe
 */
function initPixelCanvas(width, height) {
    CANVAS_WIDTH = width;
    CANVAS_HEIGHT = height;
    
    // DOM-Elemente referenzieren
    canvas = document.getElementById('pixel-canvas');
    ctx = canvas.getContext('2d');
    colorPicker = document.getElementById('color-picker');
    colorPreview = document.getElementById('color-preview');
    statusIndicator = document.getElementById('status-indicator');
    statusText = document.getElementById('status-text');
    coordDisplay = document.getElementById('coord-display');
    
    // Field of View initialisieren
    fieldOfView = {
        x1: 0,
        y1: 0,
        x2: CANVAS_WIDTH,
        y2: CANVAS_HEIGHT
    };
    
    panStartFOV = { x1: 0, y1: 0, x2: CANVAS_WIDTH, y2: CANVAS_HEIGHT };
    
    // Canvas initialisieren
    initCanvas();
    
    // Event Listener setzen
    setupEventListeners();
    
    // Initiale Farb-Vorschau setzen
    colorPreview.style.backgroundColor = colorPicker.value;
    
    // Polling für Updates starten
    startPolling();
    
    console.log('[INFO] Pixel Canvas Anwendung gestartet');
}

// ================================================================
// CANVAS INITIALISIERUNG
// ================================================================

/**
 * Initialisiert die Canvas-Größe basierend auf den Pixel-Dimensionen.
 * Die Canvas wird größer als die logischen Pixel dargestellt,
 * um bessere Sichtbarkeit zu gewährleisten.
 */
function initCanvas() {
    // Canvas-Größe in tatsächlichen Bildschirm-Pixeln setzen
    canvas.width = CANVAS_WIDTH * PIXEL_SIZE;
    canvas.height = CANVAS_HEIGHT * PIXEL_SIZE;

    // Bildglättung deaktivieren für scharfe Pixel-Kanten
    ctx.imageSmoothingEnabled = false;

    // Canvas mit Weiß füllen (Standard-Hintergrund)
    ctx.fillStyle = '#FFFFFF';
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    console.log(`[INIT] Canvas: ${canvas.width}x${canvas.height}px (${CANVAS_WIDTH}x${CANVAS_HEIGHT} art pixels)`);
}

// ================================================================
// PIXEL-RENDERING FUNKTIONEN
// ================================================================


// ================================================================
// SHADER / MAPPING FUNCTION
// ================================================================

/**
 * YOUR CUSTOM SHADER FUNCTION
 * 
 * Diese Funktion wird für jeden Pixel aus der Pixel-Art aufgerufen.
 * Sie bestimmt, wie dieser Pixel gerendert wird.
 * 
 * BEISPIELE:
 * 
 * 1. Einfach: Gib die normale Farbe zurück
 *    return pixelData[artY][artX];
 * 
 * 2. Checkerboard: Alterniere zwischen zwei Farben
 *    if ((artX + artY) % 2 === 0) return "#000000";
 *    return pixelData[artY][artX];
 * 
 * 3. Alle Pixel grün:
 *    return "#00FF00";
 * 
 * @param {number} artX - X-Koordinate in der Pixel-Art (0-49)
 * @param {number} artY - Y-Koordinate in der Pixel-Art (0-49)
 * @param {Array<Array<string>>} pixelData - Die gesamte Pixel-Art Datenstruktur
 * @returns {string} - Farbe im Hex-Format (#RRGGBB)
 */
function customShader(artX, artY, pixelData) {
    // Gib die tatsächliche Farbe des Pixels zurück
    return pixelData[Math.floor(artY)][artX];
}

// ================================================================
// INVERSE SHADER - Für Mouse-Koordinaten
// ================================================================

/**
 * Inverse Shader-Funktion: Konvertiert Screen-Pixel in Pixel-Art-Koordinaten
 * unter Berücksichtigung des aktuellen Fensters.
 * 
 * @param {number} screenX - X-Koordinate auf dem Screen
 * @param {number} screenY - Y-Koordinate auf dem Screen
 * @param {number} screenWidth - Breite des Bildschirms in Pixeln
 * @param {number} screenHeight - Höhe des Bildschirms in Pixeln
 * @returns {Object} {x: number, y: number} - Koordinaten in der Pixel-Art
 */
function inverseShader(screenX, screenY, screenWidth, screenHeight) {
    const windowWidth = fieldOfView.x2 - fieldOfView.x1;
    const windowHeight = fieldOfView.y2 - fieldOfView.y1;

    // Inverse Formel:
    // artPixel[i, j] = int(screenPixel[x, y] / screenSize * (x2-x1)) + x1
    const artX = Math.floor((screenX / screenWidth) * windowWidth) + fieldOfView.x1;
    const artY = Math.floor((screenY / screenHeight) * windowHeight) + fieldOfView.y1;

    return { x: artX, y: artY };
}

/**
 * Rendert die gesamte Canvas basierend auf den empfangenen Pixel-Daten
 * und ruft für jeden Pixel den customShader auf.
 * Respektiert das aktuelle Field of View für Zoom und Pan.
 * 
 * @param {Array<Array<string>>} pixelData - 2D-Array mit Farbwerten
 */
function renderFullCanvas(pixelData) {
    // Berechne die Größe des sichtbaren Bereichs (FOV)
    const fovWidth = fieldOfView.x2 - fieldOfView.x1;
    const fovHeight = fieldOfView.y2 - fieldOfView.y1;

    // Berechne die Größe eines Pixel-Art-Pixels auf dem Screen
    const screenPixelWidth = canvas.width / fovWidth;
    const screenPixelHeight = canvas.height / fovHeight;

    // Nur Pixel rendern, die im FOV sichtbar sind
    const startX = Math.floor(fieldOfView.x1);
    const endX = Math.ceil(fieldOfView.x2);
    const startY = Math.floor(fieldOfView.y1);
    const endY = Math.ceil(fieldOfView.y2);

    // Durch alle sichtbaren Pixel iterieren
    for (let y = startY; y < endY; y++) {
        for (let x = startX; x < endX; x++) {
            // Nur rendern wenn Koordinaten gültig sind
            if (x >= 0 && x < pixelData[0].length && y >= 0 && y < pixelData.length) {
                // Rufe customShader auf für diesen Pixel
                const color = customShader(x, y, pixelData);

                // Berechne die Position auf dem Screen (relative zum FOV)
                const screenX = (x - fieldOfView.x1) * screenPixelWidth;
                const screenY = (y - fieldOfView.y1) * screenPixelHeight;

                // Zeichne den Pixel mit der berechneten Größe
                ctx.fillStyle = color;
                ctx.fillRect(
                    screenX,                // X-Position auf dem Screen
                    screenY,                // Y-Position auf dem Screen
                    screenPixelWidth,       // Breite des Pixels (skaliert mit Zoom)
                    screenPixelHeight       // Höhe des Pixels (skaliert mit Zoom)
                );
            }
        }
    }
}

/**
 * Konvertiert Hex-Farbe zu RGB
 */
function hexToRgb(hex) {
    const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
    return result ? {
        r: parseInt(result[1], 16),
        g: parseInt(result[2], 16),
        b: parseInt(result[3], 16)
    } : { r: 255, g: 255, b: 255 };
}

/**
 * Aktualisiert nur geänderte Pixel (effizienter als vollständiges Neurendern).
 * 
 * @param {Array<Array<string>>} newData - Neue Pixel-Daten vom Server
 */
function updateChangedPixels(newData) {
    if (!localPixelData) {
        renderFullCanvas(newData);
        localPixelData = JSON.parse(JSON.stringify(newData));
        return;
    }

    // Einfach alles neurendern - mehr Sicherheit
    renderFullCanvas(newData);
    localPixelData = JSON.parse(JSON.stringify(newData));
}

// ================================================================
// SERVER-KOMMUNIKATION
// ================================================================

/**
 * Lädt die aktuellen Canvas-Daten vom Server.
 * Verwendet fetch API für asynchrone HTTP-Anfragen.
 */
async function loadCanvasData() {
    try {
        const response = await fetch('/api/canvas');
        if (response.ok) {
            const data = await response.json();
            updateChangedPixels(data.pixels);

            // Status auf "Verbunden" setzen
            statusIndicator.classList.add('connected');
            statusText.textContent = 'Verbunden';
        }
    } catch (error) {
        console.error('[FEHLER] Konnte Canvas-Daten nicht laden:', error);
        statusIndicator.classList.remove('connected');
        statusText.textContent = 'Getrennt';
    }
}

/**
 * Sendet eine Pixel-Änderung an den Server.
 * 
 * @param {number} x - X-Koordinate des Pixels
 * @param {number} y - Y-Koordinate des Pixels
 * @param {string} color - Neue Farbe im Hex-Format
 */
async function sendPixelUpdate(x, y, color) {
    try {
        const response = await fetch('/api/pixel', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ x, y, color })
        });

        if (response.ok) {
            // Lokal sofort aktualisieren für schnelle Reaktion
            if (localPixelData) {
                localPixelData[y][x] = color;
            }
            console.log(`[PIXEL] Aktualisiert: (${x}, ${y}) -> ${color}`);
        }
    } catch (error) {
        console.error('[FEHLER] Konnte Pixel nicht aktualisieren:', error);
    }
}

/**
 * Startet das regelmäßige Polling für Updates.
 * Holt in festgelegten Intervallen den aktuellen Zustand vom Server.
 */
function startPolling() {
    // Initiales Laden der Canvas-Daten
    loadCanvasData();

    // Regelmäßiges Polling starten
    setInterval(loadCanvasData, POLL_INTERVAL);
    console.log(`[INFO] Polling gestartet (Intervall: ${POLL_INTERVAL}ms)`);
}

// ================================================================
// BENUTZERINTERAKTIONEN
// ================================================================

/**
 * Konvertiert Canvas-Koordinaten (Bildschirm-Pixel) in 
 * Pixel-Art-Koordinaten unter Berücksichtigung des aktuellen Zooms und Pan.
 * 
 * @param {MouseEvent} event - Maus-Event mit Koordinaten
 * @returns {Object} - Objekt mit x und y Koordinaten in der Pixel-Art
 */
function getPixelCoordinates(event) {
    // Canvas-Position relativ zum Viewport ermitteln
    const rect = canvas.getBoundingClientRect();

    // Mausposition relativ zur Canvas berechnen
    const screenX = event.clientX - rect.left;
    const screenY = event.clientY - rect.top;

    // Konvertiere Screen-Koordinaten zu Pixel-Art-Koordinaten
    const artCoords = inverseShader(screenX, screenY, canvas.width, canvas.height);

    return artCoords;
}

/**
 * Öffnet ein Admin-Aktionsmenü zur Auswahl der Zeichnaktion
 * Optionen: Pixel setzen, Rechteck zeichnen, Kreis zeichnen, etc.
 */
function showAdminActionMenu(coords) {
    // Erstelle Modal-Dialog
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

    // Titel
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

    // Action Buttons
    const actions = [
        { id: 'pixel', label: 'Pixel setzen', color: '#e94560' },
        { id: 'rectangle', label: 'Rechteck zeichnen', color: '#f39c12' },
        { id: 'circle', label: 'Kreis zeichnen', color: '#1abc9c' },
        { id: 'line', label: 'Linie zeichnen', color: '#9b59b6' }
    ];

    const buttonsContainer = document.createElement('div');
    buttonsContainer.style.cssText = `
        display: flex;
        flex-direction: column;
        gap: 10px;
    `;

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

        button.onmouseover = function () {
            this.style.background = action.color;
            this.style.boxShadow = `0 0 15px ${action.color}`;
        };

        button.onmouseout = function () {
            this.style.background = 'rgba(255, 255, 255, 0.1)';
            this.style.boxShadow = 'none';
        };

        button.onclick = function () {
            document.body.removeChild(modal);
            document.body.removeChild(overlay);
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

    cancelButton.onmouseover = function () {
        this.style.background = 'rgba(231, 76, 60, 0.3)';
        this.style.boxShadow = '0 0 10px rgba(231, 76, 60, 0.5)';
    };

    cancelButton.onmouseout = function () {
        this.style.background = 'rgba(200, 50, 50, 0.2)';
        this.style.boxShadow = 'none';
    };

    cancelButton.onclick = function () {
        document.body.removeChild(modal);
        document.body.removeChild(overlay);
    };

    modal.appendChild(cancelButton);

    // Hintergrund-Overlay (Dimming)
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

    overlay.onclick = function () {
        document.body.removeChild(modal);
        document.body.removeChild(overlay);
    };

    document.body.appendChild(overlay);
    document.body.appendChild(modal);
}

/**
 * Führt die ausgewählte Admin-Aktion aus
 */
function executeAdminAction(actionType, coords) {
    switch (actionType) {
        case 'pixel':
            showColorPickerForAction('pixel', coords);
            break;
        case 'rectangle':
            showColorPickerForAction('rectangle', coords);
            break;
        case 'circle':
            showColorPickerForAction('circle', coords);
            break;
        case 'line':
            showColorPickerForAction('line', coords);
            break;
        default:
            console.log('Unbekannte Aktion:', actionType);
    }
}

/**
 * Zeigt den Farbwähler für die ausgewählte Aktion
 */
function showColorPickerForAction(actionType, coords) {
    // Erstelle Modal-Overlay
    const overlay = document.createElement('div');
    overlay.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: rgba(0, 0, 0, 0.6);
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 10001;
    `;

    // Erstelle Dialog-Box
    const dialog = document.createElement('div');
    dialog.style.cssText = `
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
        border: 2px solid rgba(255, 255, 255, 0.2);
        border-radius: 15px;
        padding: 30px;
        box-shadow: 0 20px 60px rgba(0, 0, 0, 0.8);
        backdrop-filter: blur(10px);
        text-align: center;
        min-width: 300px;
        animation: slideIn 0.3s ease-out;
    `;

    // Titel
    const title = document.createElement('h2');
    title.textContent = 'Pixel-Farbe wählen';
    title.style.cssText = `
        color: #ffffff;
        margin-bottom: 20px;
        font-size: 1.3rem;
        background: linear-gradient(90deg, #e94560, #f39c12);
        -webkit-background-clip: text;
        background-clip: text;
        -webkit-text-fill-color: transparent;
    `;
    dialog.appendChild(title);

    // Info-Text
    const infoText = document.createElement('p');
    infoText.textContent = `Position: ${coords.x}, ${coords.y}`;
    infoText.style.cssText = `
        color: #8892b0;
        margin-bottom: 20px;
        font-size: 0.9rem;
    `;
    dialog.appendChild(infoText);

    // Farbwähler-Container
    const colorContainer = document.createElement('div');
    colorContainer.style.cssText = `
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 15px;
        margin-bottom: 25px;
        padding: 20px;
        background: rgba(255, 255, 255, 0.05);
        border-radius: 10px;
    `;

    // Farbwähler Input
    const colorInput = document.createElement('input');
    colorInput.type = 'color';
    colorInput.value = colorPicker.value;
    colorInput.style.cssText = `
        width: 80px;
        height: 60px;
        border: none;
        border-radius: 8px;
        cursor: pointer;
        -webkit-appearance: none;
        padding: 0;
    `;

    // Farbvorschau
    const colorPreviewDialog = document.createElement('div');
    colorPreviewDialog.style.cssText = `
        width: 60px;
        height: 60px;
        border-radius: 8px;
        border: 2px solid #fff;
        background-color: ${colorInput.value};
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
    `;

    // Update Vorschau bei Farbwahl
    colorInput.addEventListener('input', function () {
        colorPreviewDialog.style.backgroundColor = colorInput.value;
    });

    colorContainer.appendChild(colorInput);
    colorContainer.appendChild(colorPreviewDialog);
    dialog.appendChild(colorContainer);

    // Buttons-Container
    const buttonContainer = document.createElement('div');
    buttonContainer.style.cssText = `
        display: flex;
        gap: 12px;
        justify-content: center;
    `;

    // Bestätigungs-Knopf
    const confirmBtn = document.createElement('button');
    confirmBtn.textContent = '✓ Bestätigen';
    confirmBtn.style.cssText = `
        flex: 1;
        padding: 12px 24px;
        background: linear-gradient(90deg, #2ecc71, #27ae60);
        color: white;
        border: none;
        border-radius: 8px;
        font-size: 1rem;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(46, 204, 113, 0.3);
    `;

    confirmBtn.addEventListener('mouseover', function () {
        confirmBtn.style.transform = 'translateY(-2px)';
        confirmBtn.style.boxShadow = '0 6px 20px rgba(46, 204, 113, 0.5)';
    });

    confirmBtn.addEventListener('mouseout', function () {
        confirmBtn.style.transform = 'translateY(0)';
        confirmBtn.style.boxShadow = '0 4px 15px rgba(46, 204, 113, 0.3)';
    });

    // Abbruch-Knopf
    const cancelBtn = document.createElement('button');
    cancelBtn.textContent = '✕ Abbrechen';
    cancelBtn.style.cssText = `
        flex: 1;
        padding: 12px 24px;
        background: linear-gradient(90deg, #e74c3c, #c0392b);
        color: white;
        border: none;
        border-radius: 8px;
        font-size: 1rem;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(231, 76, 60, 0.3);
    `;

    cancelBtn.addEventListener('mouseover', function () {
        cancelBtn.style.transform = 'translateY(-2px)';
        cancelBtn.style.boxShadow = '0 6px 20px rgba(231, 76, 60, 0.5)';
    });

    cancelBtn.addEventListener('mouseout', function () {
        cancelBtn.style.transform = 'translateY(0)';
        cancelBtn.style.boxShadow = '0 4px 15px rgba(231, 76, 60, 0.3)';
    });

    // Bestätigungs-Handler
    const handleConfirm = function () {
        const selectedColor = colorInput.value;

        // Pixel-Update an Server senden
        performAdminAction(actionType, coords, selectedColor);

        // Hauptfarbwähler aktualisieren
        colorPicker.value = selectedColor;
        colorPreview.style.backgroundColor = selectedColor;

        // Cleanup
        closeDialog();
    };

    // Abbruch-Handler
    const handleCancel = function () {
        closeDialog();
    };

    // Dialog schließen
    const closeDialog = function () {
        confirmBtn.removeEventListener('click', handleConfirm);
        cancelBtn.removeEventListener('click', handleCancel);
        overlay.removeEventListener('click', handleOverlayClick);
        document.body.removeChild(overlay);
    };

    // Klick auf Overlay schließt auch den Dialog
    const handleOverlayClick = function (e) {
        if (e.target === overlay) {
            handleCancel();
        }
    };

    confirmBtn.addEventListener('click', handleConfirm);
    cancelBtn.addEventListener('click', handleCancel);
    overlay.addEventListener('click', handleOverlayClick);

    buttonContainer.appendChild(confirmBtn);
    buttonContainer.appendChild(cancelBtn);
    dialog.appendChild(buttonContainer);

    overlay.appendChild(dialog);
    document.body.appendChild(overlay);

    // Focus auf Bestätigungs-Knopf
    confirmBtn.focus();
}

/**
 * Führt die tatsächliche Zeichenaktion aus
 */
function performAdminAction(actionType, startCoords, color) {
    switch (actionType) {
        case 'pixel':
            // Einfach einen Pixel setzen
            sendPixelUpdate(startCoords.x, startCoords.y, color);
            console.log(`[ADMIN] Pixel gesetzt bei (${startCoords.x}, ${startCoords.y})`);
            break;

        case 'rectangle':
            // Platzhalter: Rechteck zeichnen (Implementierung folgt)
            console.log(`[ADMIN] Rechteck ab (${startCoords.x}, ${startCoords.y}) - Implementierung folgt`);
            alert('Rechteck-Zeichnen: Feature folgt in Kürze!');
            break;

        case 'circle':
            // Platzhalter: Kreis zeichnen (Implementierung folgt)
            console.log(`[ADMIN] Kreis ab (${startCoords.x}, ${startCoords.y}) - Implementierung folgt`);
            alert('Kreis-Zeichnen: Feature folgt in Kürze!');
            break;

        case 'line':
            // Platzhalter: Linie zeichnen (Implementierung folgt)
            console.log(`[ADMIN] Linie ab (${startCoords.x}, ${startCoords.y}) - Implementierung folgt`);
            alert('Linie-Zeichnen: Feature folgt in Kürze!');
            break;
    }
}

/**
 * Klick-Handler für die Canvas.
 * Admins: Zeigt Aktionsmenü
 * Normale Benutzer: Direkt Pixel setzen mit aktueller Farbe
 */
/**
 * Zeigt einen Dialog mit Farbwähler und Bestätigungs-Knöpfen
 */
function showColorPickerDialog(coords) {
    // Erstelle Modal-Overlay
    const overlay = document.createElement('div');
    overlay.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: rgba(0, 0, 0, 0.6);
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 10001;
    `;

    // Erstelle Dialog-Box
    const dialog = document.createElement('div');
    dialog.style.cssText = `
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
        border: 2px solid rgba(255, 255, 255, 0.2);
        border-radius: 15px;
        padding: 30px;
        box-shadow: 0 20px 60px rgba(0, 0, 0, 0.8);
        backdrop-filter: blur(10px);
        text-align: center;
        min-width: 300px;
        animation: slideIn 0.3s ease-out;
    `;

    // Titel
    const title = document.createElement('h2');
    title.textContent = 'Pixel-Farbe wählen';
    title.style.cssText = `
        color: #ffffff;
        margin-bottom: 20px;
        font-size: 1.3rem;
        background: linear-gradient(90deg, #e94560, #f39c12);
        -webkit-background-clip: text;
        background-clip: text;
        -webkit-text-fill-color: transparent;
    `;
    dialog.appendChild(title);

    // Info-Text
    const infoText = document.createElement('p');
    infoText.textContent = `Position: ${coords.x}, ${coords.y}`;
    infoText.style.cssText = `
        color: #8892b0;
        margin-bottom: 20px;
        font-size: 0.9rem;
    `;
    dialog.appendChild(infoText);

    // Farbwähler-Container
    const colorContainer = document.createElement('div');
    colorContainer.style.cssText = `
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 15px;
        margin-bottom: 25px;
        padding: 20px;
        background: rgba(255, 255, 255, 0.05);
        border-radius: 10px;
    `;

    // Farbwähler Input
    const colorInput = document.createElement('input');
    colorInput.type = 'color';
    colorInput.value = colorPicker.value;
    colorInput.style.cssText = `
        width: 80px;
        height: 60px;
        border: none;
        border-radius: 8px;
        cursor: pointer;
        -webkit-appearance: none;
        padding: 0;
    `;

    // Farbvorschau
    const colorPreviewDialog = document.createElement('div');
    colorPreviewDialog.style.cssText = `
        width: 60px;
        height: 60px;
        border-radius: 8px;
        border: 2px solid #fff;
        background-color: ${colorInput.value};
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
    `;

    // Update Vorschau bei Farbwahl
    colorInput.addEventListener('input', function () {
        colorPreviewDialog.style.backgroundColor = colorInput.value;
    });

    colorContainer.appendChild(colorInput);
    colorContainer.appendChild(colorPreviewDialog);
    dialog.appendChild(colorContainer);

    // Buttons-Container
    const buttonContainer = document.createElement('div');
    buttonContainer.style.cssText = `
        display: flex;
        gap: 12px;
        justify-content: center;
    `;

    // Bestätigungs-Knopf
    const confirmBtn = document.createElement('button');
    confirmBtn.textContent = '✓ Bestätigen';
    confirmBtn.style.cssText = `
        flex: 1;
        padding: 12px 24px;
        background: linear-gradient(90deg, #2ecc71, #27ae60);
        color: white;
        border: none;
        border-radius: 8px;
        font-size: 1rem;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(46, 204, 113, 0.3);
    `;

    confirmBtn.addEventListener('mouseover', function () {
        confirmBtn.style.transform = 'translateY(-2px)';
        confirmBtn.style.boxShadow = '0 6px 20px rgba(46, 204, 113, 0.5)';
    });

    confirmBtn.addEventListener('mouseout', function () {
        confirmBtn.style.transform = 'translateY(0)';
        confirmBtn.style.boxShadow = '0 4px 15px rgba(46, 204, 113, 0.3)';
    });

    // Abbruch-Knopf
    const cancelBtn = document.createElement('button');
    cancelBtn.textContent = '✕ Abbrechen';
    cancelBtn.style.cssText = `
        flex: 1;
        padding: 12px 24px;
        background: linear-gradient(90deg, #e74c3c, #c0392b);
        color: white;
        border: none;
        border-radius: 8px;
        font-size: 1rem;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(231, 76, 60, 0.3);
    `;

    cancelBtn.addEventListener('mouseover', function () {
        cancelBtn.style.transform = 'translateY(-2px)';
        cancelBtn.style.boxShadow = '0 6px 20px rgba(231, 76, 60, 0.5)';
    });

    cancelBtn.addEventListener('mouseout', function () {
        cancelBtn.style.transform = 'translateY(0)';
        cancelBtn.style.boxShadow = '0 4px 15px rgba(231, 76, 60, 0.3)';
    });

    // Bestätigungs-Handler
    const handleConfirm = function () {
        const selectedColor = colorInput.value;

        // Pixel-Update an Server senden
        sendPixelUpdate(coords.x, coords.y, selectedColor);

        // Hauptfarbwähler aktualisieren
        colorPicker.value = selectedColor;
        colorPreview.style.backgroundColor = selectedColor;

        // Cleanup
        closeDialog();
    };

    // Abbruch-Handler
    const handleCancel = function () {
        closeDialog();
    };

    // Dialog schließen
    const closeDialog = function () {
        confirmBtn.removeEventListener('click', handleConfirm);
        cancelBtn.removeEventListener('click', handleCancel);
        overlay.removeEventListener('click', handleOverlayClick);
        document.body.removeChild(overlay);
    };

    // Klick auf Overlay schließt auch den Dialog
    const handleOverlayClick = function (e) {
        if (e.target === overlay) {
            handleCancel();
        }
    };

    confirmBtn.addEventListener('click', handleConfirm);
    cancelBtn.addEventListener('click', handleCancel);
    overlay.addEventListener('click', handleOverlayClick);

    buttonContainer.appendChild(confirmBtn);
    buttonContainer.appendChild(cancelBtn);
    dialog.appendChild(buttonContainer);

    overlay.appendChild(dialog);
    document.body.appendChild(overlay);

    // Focus auf Bestätigungs-Knopf
    confirmBtn.focus();
}

// ================================================================
// EVENT LISTENERS
// ================================================================

function setupEventListeners() {
    /**
     * Maus-Rad Event - Zoom in/out
     * Scroll down = Zoom in (increment x1/y1, decrement x2/y2)
     * Scroll up = Zoom out (decrement x1/y1, increment x2/y2)
     */
    canvas.addEventListener('wheel', function (event) {
        event.preventDefault();

        // Zoom-Faktor basierend auf Scroll-Richtung
        // Scroll down (deltaY > 0) = Zoom in (smaller FOV) = zoom factor > 1
        // Scroll up (deltaY < 0) = Zoom out (larger FOV) = zoom factor < 1
        const zoomFactor = event.deltaY > 0 ? 0.8 : 1.2;

        // Mausposition auf Canvas
        const rect = canvas.getBoundingClientRect();
        const screenX = event.clientX - rect.left;
        const screenY = event.clientY - rect.top;

        // Pixel-Art-Koordinaten unter Maus vor dem Zoom
        const artCoordsBefore = inverseShader(screenX, screenY, canvas.width, canvas.height);

        // Berechne neue Field of View mit Zoom
        const currentFovWidth = fieldOfView.x2 - fieldOfView.x1;
        const currentFovHeight = fieldOfView.y2 - fieldOfView.y1;

        const newFovWidth = currentFovWidth * zoomFactor;
        const newFovHeight = currentFovHeight * zoomFactor;

        // Begrenzte Zoom-Grenzen (mindestens 1 Pixel, maximal volle Größe)
        const boundedFovWidth = Math.max(1, Math.min(CANVAS_WIDTH, newFovWidth));
        const boundedFovHeight = Math.max(1, Math.min(CANVAS_HEIGHT, newFovHeight));

        // Zentrum des Zooms ist die Mausposition
        const fovCenterX = artCoordsBefore.x;
        const fovCenterY = artCoordsBefore.y;

        // Neue Grenzen berechnen (zentriert auf Mausposition)
        let newX1 = fovCenterX - (boundedFovWidth / 2);
        let newY1 = fovCenterY - (boundedFovHeight / 2);

        // Bounds clamping
        newX1 = Math.max(0, Math.min(CANVAS_WIDTH - boundedFovWidth, newX1));
        newY1 = Math.max(0, Math.min(CANVAS_HEIGHT - boundedFovHeight, newY1));

        fieldOfView.x1 = newX1;
        fieldOfView.y1 = newY1;
        fieldOfView.x2 = newX1 + boundedFovWidth;
        fieldOfView.y2 = newY1 + boundedFovHeight;

        // Canvas neu rendern mit neuem Zoom
        if (localPixelData) {
            renderFullCanvas(localPixelData);
        }

        console.log(`[ZOOM] FOV: (${fieldOfView.x1.toFixed(1)}, ${fieldOfView.y1.toFixed(1)}) - (${fieldOfView.x2.toFixed(1)}, ${fieldOfView.y2.toFixed(1)})`);
    });

    /**
     * Mouse Down - Starte Panning
     */
    canvas.addEventListener('mousedown', function (event) {
        if (event.button === 2 || event.button === 1) { // Rechtsklick oder Mittelklick
            isPanning = true;
            panStartX = event.clientX;
            panStartY = event.clientY;
            panStartFOV = JSON.parse(JSON.stringify(fieldOfView));
            event.preventDefault();
        }
    });

    /**
     * Context Menu - Deaktiviere Rechtsklick-Popup auf der Canvas
     */
    canvas.addEventListener('contextmenu', function (event) {
        event.preventDefault();
    });

    /**
     * Mouse Move - Pan die Canvas
     */
    document.addEventListener('mousemove', function (event) {
        if (!isPanning) return;

        // Berechne wie viel die Maus sich bewegt hat
        const deltaX = event.clientX - panStartX;
        const deltaY = event.clientY - panStartY;

        // Konvertiere Pixel-Bewegung in Pixel-Art-Bewegung
        const fovWidth = fieldOfView.x2 - fieldOfView.x1;
        const fovHeight = fieldOfView.y2 - fieldOfView.y1;

        const pixelSize = canvas.width / fovWidth;
        const artDeltaX = deltaX / pixelSize;
        const artDeltaY = deltaY / pixelSize;

        // Neue Field of View mit Pan
        fieldOfView.x1 = Math.max(0, Math.min(CANVAS_WIDTH - fovWidth, panStartFOV.x1 - artDeltaX));
        fieldOfView.y1 = Math.max(0, Math.min(CANVAS_HEIGHT - fovHeight, panStartFOV.y1 - artDeltaY));
        fieldOfView.x2 = fieldOfView.x1 + fovWidth;
        fieldOfView.y2 = fieldOfView.y1 + fovHeight;

        // Canvas neu rendern mit neuem Pan
        if (localPixelData) {
            renderFullCanvas(localPixelData);
        }
    });

    /**
     * Mouse Up - Beende Panning
     */
    document.addEventListener('mouseup', function () {
        isPanning = false;
    });

    canvas.addEventListener('click', function (event) {
        const coords = getPixelCoordinates(event);

        // Sicherstellen, dass Koordinaten innerhalb der Grenzen liegen
        if (coords.x >= 0 && coords.x < CANVAS_WIDTH &&
            coords.y >= 0 && coords.y < CANVAS_HEIGHT) {

            if (adminMode === true) {
                // Admin: Zeige Aktionsmenü
                showAdminActionMenu(coords);
            }
            else {
                // Zeige Dialog mit Farbwähler und Knöpfen
                showColorPickerDialog(coords);
            }
        }
    });

    /**
     * Mausbewegung über der Canvas.
     * Aktualisiert die Koordinaten-Anzeige.
     */
    canvas.addEventListener('mousemove', function (event) {
        if (!isPanning) {  // Nur koordinaten anzeigen wenn nicht panning
            const coords = getPixelCoordinates(event);

            // Koordinaten in der Anzeige aktualisieren
            if (coords.x >= 0 && coords.x < CANVAS_WIDTH &&
                coords.y >= 0 && coords.y < CANVAS_HEIGHT) {
                coordDisplay.textContent = `${coords.x}, ${coords.y}`;
            } else {
                coordDisplay.textContent = '--, --';
            }
        }
    });

    /**
     * Maus verlässt die Canvas.
     * Setzt die Koordinaten-Anzeige zurück.
     */
    canvas.addEventListener('mouseleave', function () {
        coordDisplay.textContent = '--, --';
    });

    // ================================================================
    // FARBAUSWAHL-FUNKTIONEN
    // ================================================================

    /**
     * Aktualisiert die Farb-Vorschau bei Änderung des Color Pickers.
     */
    colorPicker.addEventListener('input', function () {
        colorPreview.style.backgroundColor = colorPicker.value;
    });
}
