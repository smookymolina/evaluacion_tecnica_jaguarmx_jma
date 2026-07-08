#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
=====================================================================
 CAPA 0 — Prueba de parseo (offline: sin broker, sin hardware)
---------------------------------------------------------------------
 Verifica que serial_mqtt_bridge.parse_telemetry() convierte una línea
 'TLM ...' del firmware en el payload JSON esperado, y que descarta
 correctamente las líneas que no son telemetría o están incompletas.

 Uso:
   python capa0_test_parse.py
=====================================================================
"""
import json
import os
import sys

# Permite importar el módulo del puente desde la carpeta padre (bridge/)
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import serial_mqtt_bridge as b  # noqa: E402

# Consola Windows: UTF-8 para acentos/iconos
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except (AttributeError, ValueError):
    pass

OK, FAIL = "✅", "❌"
errores = 0


def check(nombre, cond):
    global errores
    print(f"  {OK if cond else FAIL}  {nombre}")
    if not cond:
        errores += 1


print("=" * 60)
print(" CAPA 0 — Parseo de telemetría (offline)")
print("=" * 60)

# 1) Línea completa con override interno y compuerta abriendo
line = ("[0000012345] TLM EST=COOLING INT=62.4C(OVR) EXT=28.0C SP=55C "
        "VENT=ON COMPUERTA=ABRIENDO AIN1=0 AIN2=1 EN=1")
p = b.parse_telemetry(line)
print("\n[1] Línea TLM completa:")
print(json.dumps(p, indent=2, ensure_ascii=False))
check("state_machine == COOLING", p["state_machine"] == "COOLING")
check("temp_int == 62.4", p["sensors"]["temperature_internal_c"] == 62.4)
check("temp_ext == 28.0", p["sensors"]["temperature_external_c"] == 28.0)
check("setpoint == 55.0", p["sensors"]["setpoint_c"] == 55.0)
check("fan_active True", p["actuators"]["fan_active"] is True)
check("damper OPENING (ABRIENDO→EN)", p["actuators"]["damper_state"] == "OPENING")
check("override_internal True", p["diagnostics"]["override_internal"] is True)
check("override_external False", p["diagnostics"]["override_external"] is False)
check("hbridge ain2==1", p["diagnostics"]["hbridge"]["ain2"] == 1)

# 2) Línea que NO es telemetría (banner / log FSM) → None
print("\n[2] Línea no-TLM (banner):")
check("banner devuelve None", b.parse_telemetry("===== Sistema =====") is None)
check("log FSM devuelve None",
      b.parse_telemetry("[0000000001] FSM[INIT] arranque") is None)

# 3) Línea TLM incompleta (falta INT) → payload con None (se descarta en el loop)
print("\n[3] Línea TLM incompleta (glitch USB):")
mal = ("[0000012345] TLM EST=COOLING EXT=28.0C SP=55C VENT=ON "
       "COMPUERTA=CERRADA AIN1=0 AIN2=0 EN=0")
pm = b.parse_telemetry(mal)
check("temp_int es None (se descartaría)",
      pm["sensors"]["temperature_internal_c"] is None)

print("\n" + "=" * 60)
if errores == 0:
    print(f" {OK} CAPA 0 OK — parseo correcto")
    sys.exit(0)
else:
    print(f" {FAIL} CAPA 0 con {errores} fallo(s)")
    sys.exit(1)
