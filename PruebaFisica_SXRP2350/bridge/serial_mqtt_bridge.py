#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
=====================================================================
 serial_mqtt_bridge.py — Puente Serial → MQTT (calidad industrial)
 Sistema de extracción de aire caliente — Jaguar de México
 Candidato: Ing. Jair Molina Arce
---------------------------------------------------------------------
 Lee la telemetría emitida por el firmware del XIAO RP2350 por el
 puerto serial (línea "TLM ..." a 1 Hz), la normaliza a un payload
 JSON industrial y la publica en un broker MQTT.

 - Reconexión automática al broker (paho-mqtt loop_start + retry).
 - Reintento/recuperación del puerto serial (pyserial).
 - Logs limpios por cada publicación.
=====================================================================
"""

import json
import logging
import re
import signal
import sys
import time
from datetime import datetime, timezone

import serial                         # pip install pyserial
import paho.mqtt.client as mqtt       # pip install paho-mqtt

# =====================================================================
# CONFIGURACIÓN GLOBAL  (edítala aquí)
# =====================================================================
# --- Broker MQTT -----------------------------------------------------
MQTT_HOST = "10.146.0.87"   # Broker MQTT del sistema (LAN)
MQTT_PORT = 1883
MQTT_USERNAME = None        # None si el broker no requiere autenticación
MQTT_PASSWORD = None
MQTT_KEEPALIVE = 60

# --- Serial (parámetros comunes) -------------------------------------
SERIAL_BAUD = 115200
SERIAL_TIMEOUT_S = 2.0      # timeout de lectura (s)

# --- Tópicos ---------------------------------------------------------
TOPIC_DATA_ROOT   = "jaguar/telemetry/data"     # telemetría:  TOPIC_DATA_ROOT/<perfil>
TOPIC_STATUS_ROOT = "jaguar/telemetry/status"   # LWT online/offline: TOPIC_STATUS_ROOT/<perfil>
MQTT_QOS = 1                            # entrega al menos una vez
MQTT_RETAIN = False

# --- Comportamiento --------------------------------------------------
RECONNECT_DELAY_S = 3.0     # espera entre reintentos del puerto serial

# =====================================================================
# PERFIL DE EXTRACTOR
# ---------------------------------------------------------------------
# El sistema opera un único extractor: JAIR. Su puerto serial, device_id
# y tópicos MQTT se derivan de aquí.
#
#   Puertos:  Windows "COM5"  |  Linux "/dev/ttyACM0"  |  macOS "/dev/cu.usbmodemXXXX"
# =====================================================================
PROFILE = "JAIR"
SERIAL_PORT = "COM5"
LOCATION = "Extractor — Nave Jair"

DEVICE_ID = f"XIAO_RP2350_{PROFILE}"
TOPIC_BASE = f"{TOPIC_DATA_ROOT}/{PROFILE.lower()}"
TOPIC_STATUS = f"{TOPIC_STATUS_ROOT}/{PROFILE.lower()}"

# =====================================================================
# LOGGING
# =====================================================================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-7s  %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("bridge")

# =====================================================================
# PARSEO DE TELEMETRÍA
# ---------------------------------------------------------------------
# Formato emitido por el firmware (main.cpp, 1 línea/segundo):
#   [0000012345] TLM EST=IDLE INT=25.3C EXT=24.1C SP=50C VENT=OFF \
#                COMPUERTA=CERRADA AIN1=0 AIN2=0 EN=0
# La temperatura puede llevar el sufijo "(OVR)" (override manual):
#   INT=62.4C(OVR)
# =====================================================================
_RE = {
    "uptime_ms": re.compile(r"\[(\d+)\]"),
    "state":     re.compile(r"EST=(\w+)"),
    "temp_int":  re.compile(r"INT=(-?\d+\.?\d*)C"),
    "temp_ext":  re.compile(r"EXT=(-?\d+\.?\d*)C"),
    "setpoint":  re.compile(r"SP=(\d+)C"),
    "fan":       re.compile(r"VENT=(ON|OFF)"),
    "damper":    re.compile(r"COMPUERTA=(\w+)"),
    "ain1":      re.compile(r"AIN1=(\d)"),
    "ain2":      re.compile(r"AIN2=(\d)"),
    "en":        re.compile(r"EN=(\d)"),
    "ovr_int":   re.compile(r"INT=[^ ]*\(OVR\)"),
    "ovr_ext":   re.compile(r"EXT=[^ ]*\(OVR\)"),
}

# Mapa de estado de compuerta: firmware (español) → payload (inglés)
_DAMPER_MAP = {
    "ABIERTA":  "OPEN",
    "CERRADA":  "CLOSED",
    "ABRIENDO": "OPENING",
    "CERRANDO": "CLOSING",
}


def parse_telemetry(line: str):
    """Convierte una línea 'TLM ...' en un payload JSON industrial.

    Devuelve un dict listo para publicar, o None si la línea no es
    telemetría (p. ej. logs 'FSM[...]' o el banner de arranque).
    """
    if " TLM " not in line:
        return None

    def _num(key, cast=float):
        m = _RE[key].search(line)
        return cast(m.group(1)) if m else None

    def _str(key):
        m = _RE[key].search(line)
        return m.group(1) if m else None

    damper_raw = _str("damper")
    fan_raw = _str("fan")

    payload = {
        "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "device_id": DEVICE_ID,
        "state_machine": _str("state"),
        "sensors": {
            "temperature_internal_c": _num("temp_int"),
            "temperature_external_c": _num("temp_ext"),
            "setpoint_c": _num("setpoint"),
        },
        "actuators": {
            "fan_active": (fan_raw == "ON"),
            "damper_state": _DAMPER_MAP.get(damper_raw, damper_raw),
        },
        "diagnostics": {
            "uptime_ms": _num("uptime_ms", int),
            "override_internal": bool(_RE["ovr_int"].search(line)),
            "override_external": bool(_RE["ovr_ext"].search(line)),
            "hbridge": {
                "ain1": _num("ain1", int),
                "ain2": _num("ain2", int),
                "stby": _num("en", int),
            },
        },
    }
    return payload


# =====================================================================
# CLIENTE MQTT — con reconexión automática
# =====================================================================
def build_mqtt_client() -> mqtt.Client:
    # Compatibilidad paho-mqtt 1.x / 2.x
    try:
        client = mqtt.Client(
            mqtt.CallbackAPIVersion.VERSION2,
            client_id=DEVICE_ID,
            clean_session=True,
        )
    except AttributeError:  # paho-mqtt < 2.0
        client = mqtt.Client(client_id=DEVICE_ID, clean_session=True)

    if MQTT_USERNAME:
        client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)

    # Last Will & Testament: si el puente cae, el broker publica "offline"
    client.will_set(TOPIC_STATUS, payload="offline", qos=MQTT_QOS, retain=True)

    # Reintentos automáticos de conexión (backoff exponencial de paho)
    client.reconnect_delay_set(min_delay=1, max_delay=30)

    def on_connect(cli, userdata, flags, reason_code, properties=None):
        if getattr(reason_code, "is_failure", reason_code != 0):
            log.error("MQTT conexión rechazada: %s", reason_code)
        else:
            log.info("MQTT conectado a %s:%s (perfil %s)", MQTT_HOST, MQTT_PORT, PROFILE)
            cli.publish(TOPIC_STATUS, "online", qos=MQTT_QOS, retain=True)

    def on_disconnect(cli, userdata, *args):
        # firma varía entre paho 1.x/2.x; args[-1] suele ser reason_code
        log.warning("MQTT desconectado — reintentando automáticamente...")

    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    return client


def connect_mqtt(client: mqtt.Client):
    """Conecta al broker y arranca el hilo de red (loop_start).

    loop_start() gestiona los reintentos internamente; aquí solo
    aseguramos el primer connect sin abortar si el broker no responde.
    """
    while not _stop:
        try:
            client.connect(MQTT_HOST, MQTT_PORT, MQTT_KEEPALIVE)
            client.loop_start()
            return
        except Exception as exc:  # noqa: BLE001
            log.error("No se pudo conectar a MQTT (%s). Reintento en %.0fs",
                      exc, RECONNECT_DELAY_S)
            time.sleep(RECONNECT_DELAY_S)


# =====================================================================
# BUCLE PRINCIPAL — lectura serial → publicación MQTT
# =====================================================================
_stop = False


def _handle_signal(signum, frame):
    global _stop
    _stop = True
    log.info("Señal recibida (%s) — cerrando...", signum)


def serial_reader_loop(client: mqtt.Client):
    """Abre el puerto serial y publica cada línea de telemetría.

    Ante cualquier error del puerto (desconexión USB, permiso, etc.)
    espera y reintenta abrir el puerto sin tumbar el proceso.
    """
    published = 0
    while not _stop:
        try:
            log.info("Abriendo puerto serial %s @ %d baudios...", SERIAL_PORT, SERIAL_BAUD)
            with serial.Serial(SERIAL_PORT, SERIAL_BAUD, timeout=SERIAL_TIMEOUT_S) as ser:
                log.info("Puerto serial abierto. Escuchando telemetría...")
                while not _stop:
                    try:
                        raw = ser.readline()
                    except serial.SerialException as exc:
                        log.error("Error de lectura serial: %s", exc)
                        break  # salir del inner-loop → reintenta abrir el puerto

                    if not raw:
                        continue  # timeout sin datos: sigue esperando

                    try:
                        line = raw.decode("utf-8", errors="replace").strip()
                    except Exception:  # noqa: BLE001
                        continue
                    if not line:
                        continue

                    payload = parse_telemetry(line)
                    if payload is None:
                        continue  # línea de log FSM / banner: se ignora

                    # Descartar telemetría incompleta (glitch USB / línea cortada):
                    # evita que un None reviente el log y fuerce reabrir el puerto.
                    s_chk = payload["sensors"]
                    if (payload["state_machine"] is None
                            or s_chk["temperature_internal_c"] is None
                            or s_chk["temperature_external_c"] is None
                            or s_chk["setpoint_c"] is None):
                        log.warning("Línea TLM incompleta, se descarta: %s", line)
                        continue

                    body = json.dumps(payload, separators=(",", ":"))
                    result = client.publish(TOPIC_BASE, body, qos=MQTT_QOS, retain=MQTT_RETAIN)

                    published += 1
                    s = payload["sensors"]
                    a = payload["actuators"]
                    status = "OK" if result.rc == mqtt.MQTT_ERR_SUCCESS else f"ERR({result.rc})"
                    log.info(
                        "PUB #%-5d [%s] %-8s INT=%.1f°C EXT=%.1f°C SP=%s°C FAN=%s DAMPER=%s",
                        published, status, payload["state_machine"],
                        s["temperature_internal_c"], s["temperature_external_c"],
                        s["setpoint_c"], a["fan_active"], a["damper_state"],
                    )

        except serial.SerialException as exc:
            log.error("No se pudo abrir %s: %s", SERIAL_PORT, exc)
        except Exception as exc:  # noqa: BLE001
            log.exception("Error inesperado en el bucle serial: %s", exc)

        if not _stop:
            log.info("Reintentando puerto serial en %.0fs...", RECONNECT_DELAY_S)
            time.sleep(RECONNECT_DELAY_S)


def main():
    signal.signal(signal.SIGINT, _handle_signal)
    signal.signal(signal.SIGTERM, _handle_signal)

    log.info("=" * 60)
    log.info(" Puente Serial → MQTT — Jaguar de México")
    log.info(" Perfil : %s  (%s)", PROFILE, LOCATION)
    log.info(" Device : %s", DEVICE_ID)
    log.info(" Serial : %s @ %d", SERIAL_PORT, SERIAL_BAUD)
    log.info(" MQTT   : %s:%s  →  %s", MQTT_HOST, MQTT_PORT, TOPIC_BASE)
    log.info("=" * 60)

    client = build_mqtt_client()
    connect_mqtt(client)

    try:
        serial_reader_loop(client)
    finally:
        log.info("Publicando estado 'offline' y cerrando MQTT...")
        try:
            client.publish(TOPIC_STATUS, "offline", qos=MQTT_QOS, retain=True)
            time.sleep(0.3)
            client.loop_stop()
            client.disconnect()
        except Exception:  # noqa: BLE001
            pass
        log.info("Puente detenido. Adiós.")


if __name__ == "__main__":
    main()
