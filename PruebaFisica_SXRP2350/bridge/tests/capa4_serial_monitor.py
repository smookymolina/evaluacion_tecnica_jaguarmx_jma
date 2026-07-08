#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
=====================================================================
 CAPA 4 — Monitor serial (¿el XIAO emite telemetría?), SIN MQTT
---------------------------------------------------------------------
 Abre el puerto serial y muestra las líneas 'TLM ...' que emite el
 firmware, sin tocar el broker. Sirve para confirmar que el hardware
 y el baudrate son correctos antes de meter MQTT en la ecuación.

 Uso:
   python capa4_serial_monitor.py            # usa COM5 @ 115200
   python capa4_serial_monitor.py COM6       # otro puerto
   python capa4_serial_monitor.py COM5 9600  # otro puerto y baudrate

 Alternativa equivalente sin este script:
   python -m serial.tools.miniterm COM5 115200
=====================================================================
"""
import sys
import time

import serial

SERIAL_PORT = sys.argv[1] if len(sys.argv) > 1 else "COM5"
SERIAL_BAUD = int(sys.argv[2]) if len(sys.argv) > 2 else 115200

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except (AttributeError, ValueError):
    pass

print("=" * 60)
print(f" CAPA 4 — Monitor serial  {SERIAL_PORT} @ {SERIAL_BAUD}")
print(" Espera líneas 'TLM ...' (1/seg). Ctrl+C para salir.")
print("=" * 60)

tlm_vistas = 0
try:
    with serial.Serial(SERIAL_PORT, SERIAL_BAUD, timeout=2.0) as ser:
        print(f"Puerto {SERIAL_PORT} abierto. Escuchando...\n")
        while True:
            raw = ser.readline()
            if not raw:
                continue
            line = raw.decode("utf-8", errors="replace").strip()
            if not line:
                continue
            marca = ""
            if " TLM " in line:
                tlm_vistas += 1
                marca = f"  <-- TLM #{tlm_vistas} OK"
            print(line + marca)
except serial.SerialException as exc:
    print(f"\n❌ No se pudo abrir {SERIAL_PORT}: {exc}")
    print("   Revisa el número de COM (Administrador de dispositivos) o")
    print("   cierra cualquier monitor serial que tenga el puerto ocupado.")
    sys.exit(1)
except KeyboardInterrupt:
    print(f"\nDetenido. Líneas TLM vistas: {tlm_vistas}")
    time.sleep(0.1)
