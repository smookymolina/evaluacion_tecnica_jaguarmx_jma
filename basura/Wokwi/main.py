# archivo: main.py  (reemplaza completamente el archivo anterior)
"""
main.py — Entry point del firmware
====================================
Sistema de extracción de aire caliente — Jaguar de México
Candidato: Ing. Jair Molina Arce

Plataformas:
  Simulación : Raspberry Pi Pico (RP2040) — plantilla Wokwi Jaguar
               https://wokwi.com/projects/468207977283145729
  Hardware   : Seeed XIAO RP2350 — sesión en vivo

MicroPython estándar — sin librerías externas.

Carga al MCU (mpremote):
  mpremote connect auto fs cp firmware/*.py :/
  mpremote connect auto reset

Estructura del firmware:
  main.py       — punto de entrada (este archivo)
  fsm.py        — máquina de estados principal (ThermalFSM)
  adc_ntc.py    — lectura de sensores NTC + conversión Beta (GP26, GP27)
  dip_switch.py — lectura DIP switch 3-bit y setpoint (GP0, GP6, GP7)
  hbridge.py    — control TB6612FNG para FIT0803 (GP1, GP2, GP3)
  fan.py        — control MOSFET ventilador MR1238E48B-FSR (GP4)
"""

import sys
import time
from machine import reset

# ── Metadatos del build ───────────────────────────────────────────────
_VERSION   = "1.0.0"
_CANDIDATO = "Ing. Jair Molina Arce"
_FECHA     = "2026-06-30"
_PROYECTO  = "Evaluacion Tecnica — Jaguar de Mexico"


def _banner():
    """
    Imprime banner de identificación en consola serial al arrancar.
    Permite verificar versión y candidato en logs de campo.
    """
    sep = "=" * 54
    print()
    print(sep)
    print("  Sistema de Extraccion de Aire Caliente")
    print("  Gabinete de Telecomunicaciones")
    print("  {}".format(_PROYECTO))
    print("  Candidato : {}".format(_CANDIDATO))
    print("  Version   : {}   Fecha: {}".format(_VERSION, _FECHA))
    try:
        # sys.version puede no estar disponible en todas las builds de MicroPython
        print("  MicroPython: {}".format(sys.version.split(";")[0].strip()))
    except Exception:
        print("  MicroPython: (version no disponible)")
    print(sep)
    print()


def main():
    """
    Función principal. Secuencia de arranque:
      1. Imprimir banner
      2. Importar módulo FSM (detecta archivos faltantes)
      3. Instanciar ThermalFSM (activa WDT)
      4. Ejecutar loop bloqueante run_forever()
      5. En caso de excepción fatal: safe state + reset

    El loop principal a 1 Hz y la compensación de tiempo se gestionan
    internamente en ThermalFSM.run_forever(). Este archivo solo orquesta
    el arranque y maneja la capa de excepciones más externa.
    """
    _banner()

    # Pequeño delay de estabilización de fuente de alimentación
    # (evita lecturas ADC inestables en el primer ciclo)
    time.sleep_ms(300)

    # ── Importar módulo FSM ───────────────────────────────────────────
    # Separar errores de importación (archivo faltante) de errores de ejecución
    try:
        from fsm import ThermalFSM
        print("[BOOT] Modulos del firmware cargados correctamente")
    except ImportError as e:
        print("[CRITICO] Modulo no encontrado: {}".format(e))
        print("[CRITICO] Verificar que todos los .py estan en el MCU")
        print("[CRITICO] Reset en 2 s...")
        time.sleep(2)
        reset()
        return   # Por si reset() no se ejecuta inmediatamente

    # ── Instanciar FSM ────────────────────────────────────────────────
    # ThermalFSM.__init__() activa el WDT y lo registra con hbridge.
    # A partir de aquí el WDT debe alimentarse dentro de 8 s o el MCU reseteará.
    try:
        fsm = ThermalFSM(enable_watchdog=True)
        print("[BOOT] FSM instanciada — WDT activo ({} ms)".format(8000))
    except Exception as e:
        print("[CRITICO] Error al inicializar FSM: {}".format(e))
        print("[CRITICO] Reset en 5 s...")
        time.sleep(5)
        reset()
        return

    # ── Loop principal bloqueante ─────────────────────────────────────
    # run_forever() no retorna en condiciones normales.
    # La gestion del tiempo (1 Hz + compensacion) ocurre internamente en la FSM.
    try:
        fsm.run_forever()

    except KeyboardInterrupt:
        # Solo alcanzable en sesion REPL/debug; en produccion no ocurre.
        print("\n[MAIN] Detenido por usuario (Ctrl+C) — activando safe state")
        _safe_state_emergencia()
        print("[MAIN] Sistema detenido. WDT expirara en ~8 s.")

    except Exception as e:
        # Excepcion que escapo del loop de run_forever() sin ser capturada
        # por step() — no deberia ocurrir, pero es la ultima linea de defensa.
        print("\n[CRITICO] Excepcion fatal no capturada: {}".format(e))
        _safe_state_emergencia()
        print("[CRITICO] Reset en 5 s...")
        time.sleep(5)
        reset()


def _safe_state_emergencia():
    """
    Aplica safe state directamente sin pasar por la FSM.
    Solo para casos en que la FSM no esta disponible o no responde.
    """
    try:
        from fan     import fan
        from hbridge import hbridge
        fan.off()
        hbridge.stop()
        print("[MAIN] Safe state aplicado: ventilador OFF, motor detenido")
    except Exception as e:
        print("[MAIN] No se pudo aplicar safe state: {}".format(e))


# ── Entry point ───────────────────────────────────────────────────────
# MicroPython ejecuta main.py automaticamente al encender.
main()
