#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
=====================================================================
 CAPA 1 — Verificación de dependencias (offline)
---------------------------------------------------------------------
 Comprueba que pyserial y paho-mqtt están instalados e importables.

 Uso:
   python capa1_check_deps.py
 Si falla:
   pip install -r ../requirements.txt
=====================================================================
"""
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except (AttributeError, ValueError):
    pass

print("=" * 60)
print(" CAPA 1 — Dependencias")
print("=" * 60)

faltan = []
try:
    import serial  # noqa: F401
    print("  ✅  pyserial      :", serial.__version__)
except ImportError as e:
    print("  ❌  pyserial      :", e)
    faltan.append("pyserial")

try:
    import paho.mqtt as pm  # noqa: F401
    print("  ✅  paho-mqtt     :", getattr(pm, "__version__", "instalado"))
except ImportError as e:
    print("  ❌  paho-mqtt     :", e)
    faltan.append("paho-mqtt")

print("=" * 60)
if not faltan:
    print(" ✅ CAPA 1 OK — dependencias presentes")
    sys.exit(0)
print(f" ❌ Faltan: {', '.join(faltan)}")
print("    Instala con:  pip install -r ../requirements.txt")
sys.exit(1)
