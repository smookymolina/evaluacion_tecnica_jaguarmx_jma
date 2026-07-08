#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
=====================================================================
 CAPA 3 — Publicador falso (broker + tópicos, SIN el XIAO)
---------------------------------------------------------------------
 Simula al XIAO publicando telemetría en el broker, para verificar el
 flujo broker → suscriptor sin necesidad del hardware.

 Cómo usar (dos terminales):
   Terminal A:   python ../mqtt_subscriber.py
   Terminal B:   python capa3_fake_publisher.py           # 1 mensaje
                 python capa3_fake_publisher.py --loop     # 1 msg/seg, temp variable

 Si el suscriptor imprime la línea 🔥 XIAO_RP2350_JAIR ... → CAPA 3 OK.
=====================================================================
"""
import json
import math
import sys
import time

import paho.mqtt.client as mqtt

# --- Config (debe coincidir con serial_mqtt_bridge.py) ---------------
MQTT_HOST = "10.146.0.87"
MQTT_PORT = 1883
TOPIC_DATA = "jaguar/telemetry/data/jair"
TOPIC_STATUS = "jaguar/telemetry/status/jair"
DEVICE_ID = "XIAO_RP2350_JAIR"

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except (AttributeError, ValueError):
    pass


def build_client():
    try:
        return mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    except AttributeError:  # paho < 2.0
        return mqtt.Client()


def make_payload(t: float) -> dict:
    """Telemetría de prueba; con --loop la temp interna oscila alrededor de 60°C."""
    temp_int = round(60.0 + 5.0 * math.sin(t / 5.0), 1)
    cooling = temp_int > 56.0
    return {
        "device_id": DEVICE_ID,
        "state_machine": "COOLING" if cooling else "IDLE",
        "sensors": {
            "temperature_internal_c": temp_int,
            "temperature_external_c": 28.0,
            "setpoint_c": 55.0,
        },
        "actuators": {
            "fan_active": cooling,
            "damper_state": "OPEN" if cooling else "CLOSED",
        },
    }


def main():
    loop = "--loop" in sys.argv[1:]
    c = build_client()
    c.connect(MQTT_HOST, MQTT_PORT, 60)
    c.loop_start()
    c.publish(TOPIC_STATUS, "online", qos=1, retain=True)

    print(f"Publicando en {TOPIC_DATA} @ {MQTT_HOST}:{MQTT_PORT}"
          + ("  (Ctrl+C para parar)" if loop else ""))
    n = 0
    try:
        t0 = time.time()
        while True:
            body = json.dumps(make_payload(time.time() - t0), separators=(",", ":"))
            r = c.publish(TOPIC_DATA, body, qos=1)
            r.wait_for_publish()
            n += 1
            print(f"  PUB #{n}  rc={r.rc}  {body}")
            if not loop:
                break
            time.sleep(1.0)
    except KeyboardInterrupt:
        print("\nDetenido.")
    finally:
        c.publish(TOPIC_STATUS, "offline", qos=1, retain=True)
        time.sleep(0.3)
        c.loop_stop()
        c.disconnect()


if __name__ == "__main__":
    main()
