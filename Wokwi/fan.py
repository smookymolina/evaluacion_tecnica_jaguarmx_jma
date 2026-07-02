"""
fan.py — Control del ventilador MR1238E48B-FSR
================================================
Sistema de extracción de aire caliente – Jaguar de México
Candidato: Ing. Jair Molina Arce

Hardware:
  Ventilador: MR1238E48B-FSR  (48V DC, corriente nominal ~0.3A)
  Control:    MOSFET NMOS (ej. IRL520N) accionado por GPIO4

  GPIO4 (VENT) → R_gate (100Ω) → Gate MOSFET
                                   |
  Drain MOSFET → (-) Ventilador
  (+) Ventilador → 48V
  Source MOSFET → GND

  El GPIO no puede alimentar el ventilador 48V directamente.
  El MOSFET actúa como interruptor de potencia:
    GPIO4=HIGH → MOSFET ON  → Ventilador encendido
    GPIO4=LOW  → MOSFET OFF → Ventilador apagado

  Diodo flyback (1N4007) en paralelo con ventilador protege contra
  picos de tensión al apagarlo.

Nota de seguridad:
  El estado por defecto del GPIO en reset es LOW (ventilador apagado).
  Pull-down en gate MOSFET garantiza apagado si GPIO es alta impedancia.
"""

from machine import Pin

# ── Pin de control ───────────────────────────────────────────────────
PIN_VENT = 4    # GPIO4 — Control ventilador (via MOSFET)


class Fan:
    """
    Controla el encendido/apagado del ventilador MR1238E48B-FSR.

    Uso:
        fan = Fan()
        fan.on()          # Enciende ventilador
        fan.off()         # Apaga ventilador
        fan.is_on()       # True si el ventilador está encendido
    """

    def __init__(self):
        self._pin  = Pin(PIN_VENT, Pin.OUT)
        self._on   = False
        self.off()    # Estado seguro al inicializar

    def on(self):
        """Enciende el ventilador. GPIO4=HIGH → MOSFET ON."""
        if not self._on:
            self._pin.value(1)
            self._on = True

    def off(self):
        """Apaga el ventilador. GPIO4=LOW → MOSFET OFF."""
        self._pin.value(0)    # Siempre ejecutar para garantizar estado seguro
        self._on = False

    def is_on(self) -> bool:
        return self._on

    def gpio_value(self) -> int:
        return self._pin.value()

    def status_str(self) -> str:
        return f"VENT={'ON' if self._on else 'OFF'} GPIO4={self._pin.value()}"


# ── Instancia global ─────────────────────────────────────────────────
fan = Fan()
