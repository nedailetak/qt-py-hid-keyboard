# QT Py HID Keyboard

4-tlačítkový HID makro-keyboard na Adafruit QT Py RP2040 (CircuitPython).

## Hardware

- **Board:** Adafruit QT Py RP2040
- **Tlačítka:** 4× momentary switch — GPIO A0–A3 + GND
- **Připojení:** USB-C OTG kabel → Android/iPhone

## Zapojení

```
Button 0 → A0 + GND
Button 1 → A1 + GND
Button 2 → A2 + GND
Button 3 → A3 + GND
```
Interní pull-up rezistory jsou použity — žádné externí součástky nejsou potřeba.

## Instalace

1. Nainstaluj **CircuitPython** na QT Py RP2040:
   https://circuitpython.org/board/adafruit_qtpy_rp2040/

2. Zkopíruj do kořene CIRCUITPY disku:
   - `src/code.py` → `/code.py`
   - `config.json` → `/config.json`

3. Doinstaluj knihovny do `/lib`:
   - `adafruit_hid/` (z Adafruit CircuitPython Bundle)
   - `neopixel.mpy`

## Konfigurace (config.json)

```json
{
  "buttons": {
    "0": {"key": "a", "label": "Button 0"},
    "1": {"key": "b", "label": "Button 1"},
    "2": {"key": "c", "label": "Button 2"},
    "3": {"key": "d", "label": "Button 3"}
  },
  "sleep": {
    "timeout_s": 30,
    "led_dim_s": 10
  },
  "led": {
    "brightness": 0.2,
    "color_idle": [0, 0, 50],
    "color_active": [0, 200, 0],
    "color_sleep": [0, 0, 0]
  }
}
```

### Podporované klávesy

- Písmena: `"a"` – `"z"`
- Funkční: `"F1"` – `"F12"`
- Speciální: `"SPACE"`, `"ENTER"`, `"ESCAPE"`, `"TAB"`, `"BACKSPACE"`, `"DELETE"`
- Šipky: `"UP"`, `"DOWN"`, `"LEFT"`, `"RIGHT"`

## LED stavy

| Barva | Stav |
|-------|------|
| 🔵 Modrá | Idle — čeká na stisk |
| 🟢 Zelená | Klávesa stisknuta |
| 🟡 Žlutá | Brzy usne (posledních 10s) |
| ⚫ Vypnuto | Sleep |

## Sleep / Wake

- Po **30 sekundách** nečinnosti přejde do light sleep
- **Probuzení:** stiskem libovolného tlačítka
- Timeout a dim čas jsou konfigurovatelné v `config.json`
