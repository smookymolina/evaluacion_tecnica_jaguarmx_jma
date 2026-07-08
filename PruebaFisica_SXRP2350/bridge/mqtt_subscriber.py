#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
=====================================================================
 mqtt_subscriber.py — Suscriptor de prueba (consola)
 Sistema de extracción de aire caliente — Jaguar de México
---------------------------------------------------------------------
 Se suscribe a la telemetría publicada por serial_mqtt_bridge.py y
 la imprime en consola de forma legible. Útil para verificar que el
 puente está publicando correctamente, sin necesidad de un dashboard.

 Uso:
   python mqtt_subscriber.py            # escucha el extractor (JAIR)
   python mqtt_subscriber.py JAIR       # explícito (mismo resultado)
=====================================================================
"""

import json
import sys
from datetime import datetime

import paho.mqtt.client as mqtt       # pip install paho-mqtt

# Consola de Windows (cp1252) no puede encodear los iconos (🔌🔥🌀):
# forzamos UTF-8 en stdout para evitar UnicodeEncodeError al imprimir.
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except (AttributeError, ValueError):  # Python < 3.7 o stream no reconfigurable
    pass

# =====================================================================
# CONFIGURACIÓN  (debe coincidir con serial_mqtt_bridge.py)
# =====================================================================
MQTT_HOST = "10.146.0.87"             # <-- mismo broker que el puente
MQTT_PORT = 1883
MQTT_USERNAME = None
MQTT_PASSWORD = None

TOPIC_DATA_ROOT   = "jaguar/telemetry/data"
TOPIC_STATUS_ROOT = "jaguar/telemetry/status"
PROFILES = ["JAIR"]

# Iconos por estado FSM para una lectura rápida en consola
_STATE_ICON = {
    "INIT": "⏳", "READING": "🔎", "COOLING": "🔥",
    "IDLE": "✅", "ERROR": "⚠️", "LOCKOUT": "⛔",
}


def _resolve_topics():
    """Devuelve (topic_data, topic_status) según el filtro de perfil de argv."""
    if len(sys.argv) > 1:
        prof = sys.argv[1].strip().upper()
        if prof not in PROFILES:
            print(f"Perfil desconocido: '{prof}'. Opciones: {', '.join(PROFILES)}")
            sys.exit(2)
        return (f"{TOPIC_DATA_ROOT}/{prof.lower()}",
                f"{TOPIC_STATUS_ROOT}/{prof.lower()}")
    return f"{TOPIC_DATA_ROOT}/#", f"{TOPIC_STATUS_ROOT}/#"


def build_client() -> mqtt.Client:
    try:
        client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    except AttributeError:  # paho-mqtt < 2.0
        client = mqtt.Client()
    if MQTT_USERNAME:
        client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
    client.reconnect_delay_set(min_delay=1, max_delay=30)
    return client


def main():
    topic_data, topic_status = _resolve_topics()
    client = build_client()

    def on_connect(cli, userdata, flags, reason_code, properties=None):
        if getattr(reason_code, "is_failure", reason_code != 0):
            print(f"[MQTT] conexión rechazada: {reason_code}")
            return
        print(f"[MQTT] conectado a {MQTT_HOST}:{MQTT_PORT}")
        cli.subscribe([(topic_data, 1), (topic_status, 1)])
        print(f"[MQTT] suscrito a  {topic_data}")
        print(f"[MQTT] suscrito a  {topic_status}\n")

    def on_message(cli, userdata, msg):
        now = datetime.now().strftime("%H:%M:%S")
        payload = msg.payload.decode("utf-8", errors="replace")

        # Mensajes de estado (online/offline) del LWT
        if "/status/" in msg.topic:
            print(f"{now}  🔌 [{msg.topic}]  {payload}")
            return

        try:
            d = json.loads(payload)
        except json.JSONDecodeError:
            print(f"{now}  ⁉️  [{msg.topic}]  {payload}")
            return

        s = d.get("sensors", {})
        a = d.get("actuators", {})
        est = d.get("state_machine", "?")
        icon = _STATE_ICON.get(est, "•")
        fan = "🌀ON" if a.get("fan_active") else "○OFF"
        print(
            f"{now}  {icon} {d.get('device_id','?'):22} "
            f"{est:8} INT={s.get('temperature_internal_c')}°C "
            f"EXT={s.get('temperature_external_c')}°C "
            f"SP={s.get('setpoint_c')}°C  "
            f"FAN={fan}  COMPUERTA={a.get('damper_state')}"
        )

    client.on_connect = on_connect
    client.on_message = on_message

    print("=" * 60)
    print(" Suscriptor de prueba — Jaguar de México")
    print(f" Broker: {MQTT_HOST}:{MQTT_PORT}")
    print("=" * 60)

    try:
        client.connect(MQTT_HOST, MQTT_PORT, 60)
        client.loop_forever()   # gestiona reconexiones automáticamente
    except KeyboardInterrupt:
        print("\nSuscriptor detenido. Adiós.")
    except Exception as exc:  # noqa: BLE001
        print(f"[ERROR] {exc}")
    finally:
        try:
            client.disconnect()
        except Exception:  # noqa: BLE001
            pass


if __name__ == "__main__":
    main()
