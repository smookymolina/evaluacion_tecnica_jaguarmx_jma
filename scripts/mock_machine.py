# mock_machine.py
"""
Mock del módulo 'machine' de MicroPython para pruebas locales en PC (Windows/Linux/Mac).
"""

class Pin:
    IN = 0
    OUT = 1
    PULL_UP = 2

    def __init__(self, pin, mode=-1, pull=-1):
        self.pin = pin
        self.mode = mode
        self.pull = pull
        # Los pines de DIP switch con pull-up inician en 1 (no presionado)
        if pin in (0, 6, 7):
            self._val = 1
        else:
            self._val = 0

    def value(self, val=None):
        if val is not None:
            self._val = int(val)
        return self._val

class ADC:
    def __init__(self, pin_obj):
        self.pin = pin_obj.pin if hasattr(pin_obj, 'pin') else pin_obj
        # Valor default a la mitad
        self._val = 32768

    def read_u16(self):
        return self._val

    def set_mock_value(self, val):
        self._val = val

class WDT:
    def __init__(self, timeout=8000):
        self.timeout = timeout
        self.fed = False

    def feed(self):
        self.fed = True

def reset():
    print("[MOCK RESET] Microcontrolador reiniciado.")
