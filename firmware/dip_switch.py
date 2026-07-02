"""
dip_switch.py — Módulo de lectura del DIP switch de configuración
==================================================================
Sistema de extracción de aire caliente – Jaguar de México
Candidato: Ing. Jair Molina Arce

DIP Switch de 3 posiciones con pull-up interno (lógica invertida):
  Pin HIGH (no presionado) = bit 0
  Pin LOW  (presionado)    = bit 1

Mapa de GPIOs:
  SW1 → GPIO6  (bit 0, LSB)
  SW2 → GPIO8  (bit 1)
  SW3 → GPIO0  (bit 2, MSB)

Tabla de setpoints (°C):
  SW3 SW2 SW1 | Setpoint
   0   0   0  |  40°C
   0   0   1  |  45°C
   0   1   0  |  50°C
   0   1   1  |  55°C
   1   0   0  |  60°C
   1   0   1  |  65°C
   1   1   0  |  70°C
   1   1   1  |  75°C
"""

from machine import Pin

# ── Pines del DIP switch ─────────────────────────────────────────────
PIN_SW1 = 6    # GPIO6  — Bit 0 (LSB)
PIN_SW2 = 7    # GPIO7  — Bit 1
PIN_SW3 = 0    # GPIO0  — Bit 2 (MSB)

# ── Tabla de setpoints ───────────────────────────────────────────────
SETPOINT_TABLE = {
    0b000: 40,
    0b001: 45,
    0b010: 50,
    0b011: 55,
    0b100: 60,
    0b101: 65,
    0b110: 70,
    0b111: 75,
}

DEFAULT_SETPOINT = 40    # Valor por defecto si la lectura falla

# ── Histéresis del control ───────────────────────────────────────────
# El sistema activa enfriamiento cuando temp > setpoint + HYST
# y lo desactiva cuando temp < setpoint - HYST
# Esto evita chattering (conmutación rápida) alrededor del umbral.
HYSTERESIS_C = 1.0       # ±1°C de histéresis


class DIPSwitch:
    """
    Lee el DIP switch de 3 posiciones y retorna el setpoint de temperatura.
    Los pines usan pull-up interno; lógica invertida (LOW = activado = bit=1).

    Uso:
        dip = DIPSwitch()
        setpoint = dip.read_setpoint()   # e.g. 60
        hyst_hi  = dip.threshold_high()  # e.g. 61.0 (activar enfriamiento)
        hyst_lo  = dip.threshold_low()   # e.g. 59.0 (desactivar enfriamiento)
    """

    def __init__(self):
        # Pull-up interno habilitado; lógica: value()==0 → switch ON → bit=1
        self._sw1 = Pin(PIN_SW1, Pin.IN, Pin.PULL_UP)
        self._sw2 = Pin(PIN_SW2, Pin.IN, Pin.PULL_UP)
        self._sw3 = Pin(PIN_SW3, Pin.IN, Pin.PULL_UP)

    def _read_bits(self) -> int:
        """
        Lee los 3 bits del DIP switch.
        Lógica invertida: pin=0 (presionado) → bit=1
        """
        bit0 = 1 - self._sw1.value()   # SW1 → LSB
        bit1 = 1 - self._sw2.value()   # SW2
        bit2 = 1 - self._sw3.value()   # SW3 → MSB
        return (bit2 << 2) | (bit1 << 1) | bit0

    def read_setpoint(self) -> int:
        """
        Retorna el setpoint de temperatura en °C según la posición del DIP.
        Siempre retorna un valor válido (usa DEFAULT si hay error).
        """
        code = self._read_bits()
        return SETPOINT_TABLE.get(code, DEFAULT_SETPOINT)

    def threshold_high(self) -> float:
        """
        Umbral de activación: temperatura a partir de la cual se activa enfriamiento.
        = setpoint + HYSTERESIS
        """
        return float(self.read_setpoint()) + HYSTERESIS_C

    def threshold_low(self) -> float:
        """
        Umbral de desactivación: temperatura por debajo de la cual se apaga enfriamiento.
        = setpoint - HYSTERESIS
        """
        return float(self.read_setpoint()) - HYSTERESIS_C

    def status_str(self) -> str:
        """Representación de texto para logging serial."""
        code = self._read_bits()
        sp   = self.read_setpoint()
        return f"DIP=0b{code:03b} SP={sp}°C ±{HYSTERESIS_C}°C"


# ── Instancia global ─────────────────────────────────────────────────
dip = DIPSwitch()
