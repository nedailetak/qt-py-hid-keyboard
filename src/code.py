"""
QT Py RP2040 — 4-Button HID Keyboard
CircuitPython

Zapojení:
  A0 - Button 0  (pull-up, druhý konec na GND)
  A1 - Button 1
  A2 - Button 2
  A3 - Button 3
  TX - LED + rezistor (cca 330Ω) na GND

Požadované knihovny (do /lib):
  adafruit_hid/
"""

import time
import json
import board
import alarm
import digitalio
import usb_hid
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keycode import Keycode

# ─── Config ──────────────────────────────────────────────────────────────────

def load_config():
    try:
        with open("/config.json") as f:
            return json.load(f)
    except Exception as e:
        print("Config error:", e)
        return {
            "buttons": {
                "0": {"key": "a"},
                "1": {"key": "b"},
                "2": {"key": "c"},
                "3": {"key": "d"},
            },
            "sleep": {"timeout_s": 30, "blink_warn_s": 10},
            "led": {"pin": "TX"},
        }

def key_to_keycode(key_str):
    """Převede string ('a', 'F1', 'SPACE', ...) na Keycode."""
    key_str = key_str.upper()
    mapping = {
        "SPACE": Keycode.SPACE,
        "ENTER": Keycode.ENTER,
        "ESCAPE": Keycode.ESCAPE,
        "TAB": Keycode.TAB,
        "BACKSPACE": Keycode.BACKSPACE,
        "DELETE": Keycode.DELETE,
        "UP": Keycode.UP_ARROW,
        "DOWN": Keycode.DOWN_ARROW,
        "LEFT": Keycode.LEFT_ARROW,
        "RIGHT": Keycode.RIGHT_ARROW,
        "F1": Keycode.F1, "F2": Keycode.F2, "F3": Keycode.F3, "F4": Keycode.F4,
        "F5": Keycode.F5, "F6": Keycode.F6, "F7": Keycode.F7, "F8": Keycode.F8,
        "F9": Keycode.F9, "F10": Keycode.F10, "F11": Keycode.F11, "F12": Keycode.F12,
    }
    if key_str in mapping:
        return mapping[key_str]
    if len(key_str) == 1 and key_str.isalpha():
        return getattr(Keycode, key_str, None)
    if len(key_str) == 1 and key_str.isdigit():
        return getattr(Keycode, key_str, None)
    return None

# ─── Hardware init ────────────────────────────────────────────────────────────

BUTTON_PINS = [board.A0, board.A1, board.A2, board.A3]

def init_buttons():
    buttons = []
    for pin in BUTTON_PINS:
        btn = digitalio.DigitalInOut(pin)
        btn.direction = digitalio.Direction.INPUT
        btn.pull = digitalio.Pull.UP
        buttons.append(btn)
    return buttons

def init_led(pin_name="TX"):
    pin = getattr(board, pin_name, board.TX)
    led = digitalio.DigitalInOut(pin)
    led.direction = digitalio.Direction.OUTPUT
    led.value = True  # zapnout při startu
    return led

# ─── LED stavy ───────────────────────────────────────────────────────────────
# Stavy jsou signalizovány blikáním:
#   Idle:       svítí trvale
#   Stisk:      krátký záblesk (řeší se přímo v hlavní smyčce)
#   Brzy usne:  rychlé blikání (varování)
#   Sleep:      vypnuto

def blink(led, times=1, on_ms=50, off_ms=50):
    for _ in range(times):
        led.value = False
        time.sleep(off_ms / 1000)
        led.value = True
        time.sleep(on_ms / 1000)

# ─── Sleep / Wake ─────────────────────────────────────────────────────────────

def go_to_sleep(buttons, led):
    """Uspí zařízení. Probouzí se stiskem libovolného tlačítka."""
    led.value = False
    pin_alarms = [alarm.pin.PinAlarm(pin=p, value=False, pull=True) for p in BUTTON_PINS]
    for btn in buttons:
        btn.deinit()
    led.deinit()
    alarm.light_sleep_until_alarms(*pin_alarms)
    # Po probuzení — reinit
    cfg = load_config()
    new_buttons = init_buttons()
    new_led = init_led(cfg["led"].get("pin", "TX"))
    new_led.value = True
    return new_buttons, new_led

# ─── Main loop ────────────────────────────────────────────────────────────────

def main():
    cfg = load_config()
    kbd = Keyboard(usb_hid.devices)
    buttons = init_buttons()
    led = init_led(cfg["led"].get("pin", "TX"))

    keycodes = {}
    for idx, btn_cfg in cfg["buttons"].items():
        kc = key_to_keycode(btn_cfg.get("key", ""))
        if kc is not None:
            keycodes[int(idx)] = kc
        else:
            print(f"Neznámý klíč pro tlačítko {idx}: {btn_cfg.get('key')}")

    timeout_s = cfg["sleep"]["timeout_s"]
    blink_warn_s = cfg["sleep"]["blink_warn_s"]
    last_activity = time.monotonic()
    warning_active = False

    # Bliknutí při startu — signalizace ready
    blink(led, times=3, on_ms=80, off_ms=80)
    led.value = True  # idle = svítí

    print("QT Py HID Keyboard ready")

    while True:
        now = time.monotonic()
        elapsed = now - last_activity

        for i, btn in enumerate(buttons):
            if not btn.value:  # stisknuto
                kc = keycodes.get(i)
                if kc is not None:
                    # Krátký záblesk při stisku
                    led.value = False
                    kbd.press(kc)
                    while not btn.value:
                        time.sleep(0.01)
                    kbd.release(kc)
                    led.value = True
                    last_activity = time.monotonic()
                    warning_active = False
                time.sleep(0.05)  # debounce

        # Varování před spaním — rychlé blikání
        if elapsed > (timeout_s - blink_warn_s):
            if not warning_active:
                warning_active = True
            # Bliká každou sekundu
            led.value = (int(elapsed * 4) % 2 == 0)

        # Sleep
        if elapsed > timeout_s:
            print("Going to sleep...")
            buttons, led = go_to_sleep(buttons, led)
            last_activity = time.monotonic()
            warning_active = False
            cfg = load_config()
            timeout_s = cfg["sleep"]["timeout_s"]
            blink_warn_s = cfg["sleep"]["blink_warn_s"]

        time.sleep(0.01)

main()
