"""
hbridge.py — Control del puente H TB6612FNG para actuador FIT0803
==================================================================
Sistema de extracción de aire caliente – Jaguar de México
Candidato: Ing. Jair Molina Arce

Hardware:
  Puente H: TB6612FNG (Toshiba)
  Actuador: FIT0803 (actuador lineal, rated 6V) — controla compuertas del sistema
            Nota: Jaguar especifica alimentación a 5V; a esa tensión la velocidad
            es aprox. 5.8 mm/s (vs 7 mm/s @ 6V), travel ~1.7s → ACTUATOR_TRAVEL_MS=3000
            incluye margen de seguridad generoso. Ajustar en sesión en vivo.

Mapa de señales:
  AIN1      → GPIO2   (dirección 1)
  AIN2      → GPIO1   (dirección 2)
  MOTOR_EN  → GPIO3   (habilitación del puente H / PWMA)

  STBY (pin TB6612FNG) → conectar a 3.3V en hardware (no controlado por GPIO).
  CRÍTICO: si STBY=LOW, el puente H queda en modo standby y no responde a AIN/EN.

Tabla de verdad TB6612FNG (canal A, usado para FIT0803):
  AIN1  AIN2  MOTOR_EN | Acción
  LOW   HIGH   HIGH    | Abrir compuertas  (motor gira hacia adelante)
  HIGH  LOW    HIGH    | Cerrar compuertas (motor gira en reversa)
  LOW   LOW    LOW     | Motor detenido (frenado / estado seguro)

Timing:
  FIT0803 @ 6V: velocidad 7 mm/s, stroke 10 mm → travel = 10/7 ≈ 1.43 s
  FIT0803 @ 5V: velocidad ~5.8 mm/s            → travel ≈ 1.72 s
  ACTUATOR_TRAVEL_MS = 3000 ms (margen ×1.75 sobre velocidad @ 5V)
  Ajustar con cronómetro durante la sesión en vivo.

WDT (Watchdog Timer):
  open_dampers() y close_dampers() bloquean el loop por ACTUATOR_TRAVEL_MS.
  Para evitar que el WDT expire durante el travel, esta clase acepta un
  callback wdt_feed via set_wdt_feed(). La FSM debe registrarlo al init.
  El sleep se divide en segmentos de WDT_FEED_INTERVAL_MS y alimenta el WDT
  entre segmentos. 3000 ms < 8000 ms WDT timeout, por lo que es safe incluso
  sin callback, pero el callback es best practice para sistemas industriales.

Nota de seguridad:
  En cualquier condición de error el motor se detiene inmediatamente.
  MOTOR_EN=LOW desactiva el puente H independientemente de AIN1/AIN2.
"""

from machine import Pin
import time

# ── Pines de control ─────────────────────────────────────────────────
PIN_AIN1     = 2    # GPIO2 — Dirección 1
PIN_AIN2     = 1    # GPIO1 — Dirección 2
PIN_MOTOR_EN = 3    # GPIO3 — Habilitación puente H

# ── Timing del actuador ──────────────────────────────────────────────
# FIT0803 @ 6V (rated): 7 mm/s × 10 mm stroke = 1.43 s
# FIT0803 @ 5V (Jaguar): ~5.8 mm/s × 10 mm    = 1.72 s
# Margen de seguridad ×1.75 → 3000 ms
# Ajustar durante la sesión en vivo con el hardware real.
ACTUATOR_TRAVEL_MS     = 3000   # ms de recorrido completo (conservador @ 5V)
ACTUATOR_STOP_DELAY_MS = 100    # Pequeño delay de estabilización antes de detener
WDT_FEED_INTERVAL_MS   = 500    # Intervalo de feed del WDT durante el travel


class HBridge:
    """
    Controla el puente H TB6612FNG para el actuador lineal FIT0803.

    Interfaz pública:
        hb = HBridge()
        hb.open_dampers()    # Abre compuertas (FIT0803 extiende)
        hb.close_dampers()   # Cierra compuertas (FIT0803 retrae)
        hb.stop()            # Detiene motor (estado seguro)
        hb.is_stopped()      # True si el motor está detenido
    """

    # ── Estados internos ─────────────────────────────────────────────
    STATE_STOPPED = "STOPPED"
    STATE_OPENING = "OPENING"
    STATE_CLOSING = "CLOSING"

    def __init__(self):
        self._ain1     = Pin(PIN_AIN1,     Pin.OUT)
        self._ain2     = Pin(PIN_AIN2,     Pin.OUT)
        self._motor_en = Pin(PIN_MOTOR_EN, Pin.OUT)
        self._state    = self.STATE_STOPPED
        self._wdt_feed = None   # Callback opcional para alimentar el WDT durante travel
        self.stop()             # Garantizar estado seguro al inicializar

    def set_wdt_feed(self, callback):
        """
        Registra un callback para alimentar el WDT durante el travel del actuador.
        Llamar desde la FSM después de crear el WDT:
            hbridge.set_wdt_feed(wdt.feed)
        """
        self._wdt_feed = callback

    def _safe_sleep_ms(self, total_ms: int):
        """
        Sleep en segmentos de WDT_FEED_INTERVAL_MS, alimentando el WDT entre cada uno.
        Evita que el watchdog expire durante operaciones bloqueantes del actuador.
        """
        remaining = total_ms
        while remaining > 0:
            chunk = min(WDT_FEED_INTERVAL_MS, remaining)
            time.sleep_ms(chunk)
            remaining -= chunk
            if self._wdt_feed:
                self._wdt_feed()    # Alimentar WDT entre segmentos

    def stop(self):
        """
        Detiene el motor. Estado seguro: MOTOR_EN=LOW, AIN1=LOW, AIN2=LOW.
        Este es el estado de fallo seguro (fail-safe).
        """
        self._motor_en.value(0)    # Deshabilitar puente H primero
        self._ain1.value(0)
        self._ain2.value(0)
        self._state = self.STATE_STOPPED

    def open_dampers(self):
        """
        Abre las compuertas del sistema de extracción.
        AIN1=LOW, AIN2=HIGH, MOTOR_EN=HIGH
        El motor corre por ACTUATOR_TRAVEL_MS ms y luego se detiene.
        """
        if self._state == self.STATE_OPENING:
            return    # Ya está abriendo, no re-energizar

        # Configurar dirección ANTES de habilitar el puente H
        self._ain1.value(0)
        self._ain2.value(1)
        time.sleep_ms(10)          # Pequeño delay de estabilización
        self._motor_en.value(1)    # Habilitar puente H
        self._state = self.STATE_OPENING

        # Dejar correr el motor el tiempo de recorrido (con WDT feed intermedio)
        self._safe_sleep_ms(ACTUATOR_TRAVEL_MS)
        self.stop()

    def close_dampers(self):
        """
        Cierra las compuertas del sistema de extracción.
        AIN1=HIGH, AIN2=LOW, MOTOR_EN=HIGH
        El motor corre por ACTUATOR_TRAVEL_MS ms y luego se detiene.
        """
        if self._state == self.STATE_CLOSING:
            return    # Ya está cerrando, no re-energizar

        # Configurar dirección ANTES de habilitar el puente H
        self._ain1.value(1)
        self._ain2.value(0)
        time.sleep_ms(10)          # Pequeño delay de estabilización
        self._motor_en.value(1)    # Habilitar puente H
        self._state = self.STATE_CLOSING

        # Dejar correr el motor el tiempo de recorrido (con WDT feed intermedio)
        self._safe_sleep_ms(ACTUATOR_TRAVEL_MS)
        self.stop()

    def is_stopped(self) -> bool:
        return self._state == self.STATE_STOPPED

    @property
    def state(self) -> str:
        return self._state

    def gpio_status(self) -> dict:
        """Retorna el estado de los GPIOs para logging y debug."""
        return {
            "AIN1":     self._ain1.value(),
            "AIN2":     self._ain2.value(),
            "MOTOR_EN": self._motor_en.value(),
            "state":    self._state,
        }


# ── Instancia global ─────────────────────────────────────────────────
hbridge = HBridge()
