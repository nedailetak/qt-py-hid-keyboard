"""
QT Py RP2040 — 4-Button HID Keyboard
CircuitPython

Zapojení:
  GPIO0 - Button 0  (+ pull-up, druhý konec na GND)
  GPIO1 - Button 1
  GPIO2 - Button 2
  GPIO3 - Button 3

Požadované knihovny (do /lib):
  adafruit_hid/
  neopixel.mpy
"""

import time
import json
import board
import alarm
import digitalio
import neopixel
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
            "sleep": {"timeout_s": 30, "led_dim_s": 10},
            "led": {"brightness": 0.2, "color_idle": [0, 0, 50], "color_active": [0, 200, 0], "color_sleep": [0, 0, 0]},
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
    # Písmena A-Z
    if len(key_str) == 1 and key_str.isalpha():
        return getattr(Keycode, key_str, None)
    # Číslice 0-9
    if len(key_str) == 1 and key_str.isdigit():
        return getattr(Keycode, f"_{key_str}" if key_str == "0" else key_str, None)
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

def init_led(brightness):
    pixel = neopixel.NeoPixel(board.NEOPIXEL, 1, brightness=brightness, auto_write=True)
    return pixel

def set_led(pixel, color):
    pixel[0] = tuple(color)

# ─── Sleep / Wake ─────────────────────────────────────────────────────────────

def go_to_sleep(buttons, led):
    """Uspí zařízení. Probouzí se stiskem libovolného tlačítka."""
    set_led(led, [0, 0, 0])
    # Nastaví alarm na stisk tlačítka (falling edge = stisk při pull-up)
    pin_alarms = [alarm.pin.PinAlarm(pin=btn.id, value=False, pull=True) for btn in BUTTON_PINS]
    # Uvolnit piny před spaním
    for btn in buttons:
        btn.deinit()
    led.deinit()
    alarm.light_sleep_until_alarms(*pin_alarms)
    # Po probuzení — reinit
    new_buttons = init_buttons()
    cfg = load_config()
    new_led = init_led(cfg["led"]["brightness"])
    set_led(new_led, cfg["led"]["color_idle"])
    return new_buttons, new_led

# ─── Main loop ────────────────────────────────────────────────────────────────

def main():
    cfg = load_config()
    kbd = Keyboard(usb_hid.devices)
    buttons = init_buttons()
    led = init_led(cfg["led"]["brightness"])
    set_led(led, cfg["led"]["color_idle"])

    # Sestavení mapy tlačítko → keycode
    keycodes = {}
    for idx, btn_cfg in cfg["buttons"].items():
        kc = key_to_keycode(btn_cfg.get("key", ""))
        if kc is not None:
            keycodes[int(idx)] = kc
        else:
            print(f"Neznámý klíč pro tlačítko {idx}: {btn_cfg.get('key')}")

    timeout_s = cfg["sleep"]["timeout_s"]
    dim_s = cfg["sleep"]["led_dim_s"]
    last_activity = time.monotonic()
    dimmed = False

    print("QT Py HID Keyboard ready")

    while True:
        now = time.monotonic()
        elapsed = now - last_activity
        pressed_any = False

        for i, btn in enumerate(buttons):
            if not btn.value:  # stisknuto (pull-up → LOW = stisk)
                pressed_any = True
                kc = keycodes.get(i)
                if kc is not None:
                    set_led(led, cfg["led"]["color_active"])
                    kbd.press(kc)
                    while not btn.value:  # čekej na uvolnění
                        time.sleep(0.01)
                    kbd.release(kc)
                    set_led(led, cfg["led"]["color_idle"])
                    last_activity = time.monotonic()
                    dimmed = False
                time.sleep(0.05)  # debounce

        # LED dim před spaním
        if not dimmed and elapsed > (timeout_s - dim_s):
            set_led(led, [5, 5, 0])  # žlutá = brzy usne
            dimmed = True

        # Deep sleep
        if elapsed > timeout_s:
            print("Going to sleep...")
            buttons, led = go_to_sleep(buttons, led)
            last_activity = time.monotonic()
            dimmed = False
            cfg = load_config()  # reload config po probuzení

        time.sleep(0.01)

main()
