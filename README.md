# QT Py HID Keyboard

4-tlačítkový HID makro-keyboard na Adafruit QT Py RP2040 (CircuitPython).

## Hardware

- **Board:** Adafruit QT Py RP2040
- **Tlačítka:** 4× momentary switch — GPIO A0–A3 + GND
- **LED:** jednoduchá LED + rezistor ~330Ω na pin TX (konfigurovatelné)
- **Připojení:** USB-C OTG kabel → Android/iPhone

## Zapojení

```
Button 0 → A0 + GND
Button 1 → A1 + GND
Button 2 → A2 + GND
Button 3 → A3 + GND
LED      → TX → 330Ω → GND
```
Interní pull-up rezistory jsou použity — žádné externí součástky pro tlačítka nejsou potřeba.

## Instalace

1. Nainstaluj **CircuitPython** na QT Py RP2040:
   https://circuitpython.org/board/adafruit_qtpy_rp2040/

2. Zkopíruj do kořene CIRCUITPY disku:
   - `src/code.py` → `/code.py`
   - `config.json` → `/config.json`

3. Doinstaluj knihovny do `/lib`:
   - `adafruit_hid/` (z Adafruit CircuitPython Bundle)

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
    "blink_warn_s": 10
  },
  "led": {
    "pin": "TX"
  }
}
```

### Podporované klávesy

- Písmena: `"a"` – `"z"`
- Funkční: `"F1"` – `"F12"`
- Speciální: `"SPACE"`, `"ENTER"`, `"ESCAPE"`, `"TAB"`, `"BACKSPACE"`, `"DELETE"`
- Šipky: `"UP"`, `"DOWN"`, `"LEFT"`, `"RIGHT"`

## LED stavy

| Stav LED | Význam |
|----------|--------|
| Svítí trvale | Idle — čeká na stisk |
| 3× bliknutí při startu | Zařízení ready |
| Záblesk při stisku | Klávesa odeslána |
| Rychlé blikání | Brzy usne (posledních 10s) |
| Vypnuto | Sleep |

## Sleep / Wake

- Po **30 sekundách** nečinnosti přejde do light sleep
- **Probuzení:** stiskem libovolného tlačítka
- Timeout a dim čas jsou konfigurovatelné v `config.json`
