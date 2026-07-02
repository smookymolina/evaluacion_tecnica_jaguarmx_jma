# mock_time.py
"""
Mock del módulo 'time' de MicroPython para pruebas locales en PC (Windows/Linux/Mac).
"""

_current_time_ms = 1000

def sleep(seconds):
    global _current_time_ms
    _current_time_ms += int(seconds * 1000)

def sleep_ms(ms):
    global _current_time_ms
    _current_time_ms += ms

def ticks_ms():
    return _current_time_ms

def ticks_add(t, delta):
    return (t + delta) & 0x3FFFFFFF  # Emular wrapping de ticks en MicroPython si es necesario, o simple suma

def ticks_diff(t1, t2):
    # En MicroPython, ticks_diff(t1, t2) calcula t1 - t2 tomando en cuenta el wrapping
    # Para la simulación simplificada, hacemos resta directa
    diff = t1 - t2
    # Manejar wrapping si es necesario (generalmente no para periodos cortos)
    return diff
