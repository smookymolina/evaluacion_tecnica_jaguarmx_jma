# Puente Serial → MQTT — Extracción de Aire Caliente

Bridge de IoT que lee la telemetría del **XIAO RP2350** por el puerto serial, la
normaliza a un **payload JSON de calidad industrial** y la publica en un **broker
MQTT**. Incluye un suscriptor de prueba para verificar el flujo en consola.

> Ing. Jair Molina Arce · Firmware `src/main.cpp` · Jaguar de México.

---

## 1. Estructura

```
bridge/
├── serial_mqtt_bridge.py   ← puente Serial → MQTT (con perfiles + reconexión)
├── mqtt_subscriber.py      ← suscriptor de prueba (consola)
├── requirements.txt        ← dependencias (pyserial, paho-mqtt)
└── README.md               ← este documento
```

---

## 2. Instalación

```bash
cd bridge
pip install -r requirements.txt
```

Dependencias: `pyserial>=3.5`, `paho-mqtt>=2.0` (compatible también con 1.x).

---

## 3. Ejecución rápida

```bash
# Publicar la telemetría del extractor (JAIR)
python serial_mqtt_bridge.py

# En otra terminal: ver lo que llega al broker
python mqtt_subscriber.py            # el extractor JAIR
```

Detén cualquiera de los dos con `Ctrl+C` (cierre ordenado).

---

## 4. Extractor

El sistema opera **un único extractor**, el perfil **JAIR**, con su puerto serial,
`device_id` y tópicos MQTT propios:

| Perfil | Puerto | device_id          | Tópico de telemetría          | Tópico de estado (LWT)          |
|--------|--------|--------------------|-------------------------------|---------------------------------|
| `JAIR` | `COM5` | `XIAO_RP2350_JAIR` | `jaguar/telemetry/data/jair`  | `jaguar/telemetry/status/jair`  |

Edita el puerto en las constantes `PROFILE` / `SERIAL_PORT` al inicio de
`serial_mqtt_bridge.py`.

> **Puertos por SO:** Windows `COM5` · Linux `/dev/ttyACM0` · macOS `/dev/cu.usbmodemXXXX`.

---

## 5. Configuración global

Al inicio de `serial_mqtt_bridge.py`:

| Variable | Valor por defecto | Descripción |
|----------|-------------------|-------------|
| `MQTT_HOST` | `10.146.0.87` | Broker MQTT del sistema (LAN) |
| `MQTT_PORT` | `1883` | Puerto MQTT |
| `MQTT_USERNAME` / `MQTT_PASSWORD` | `None` | Autenticación (si el broker la requiere) |
| `SERIAL_BAUD` | `115200` | Coincide con `Serial.begin(115200)` del firmware |
| `SERIAL_TIMEOUT_S` | `2.0` | Timeout de lectura serial |
| `TOPIC_DATA_ROOT` | `jaguar/telemetry/data` | Base del tópico de telemetría (`.../jair`) |
| `TOPIC_STATUS_ROOT` | `jaguar/telemetry/status` | Base del tópico de estado LWT (`.../jair`) |
| `MQTT_QOS` | `1` | Calidad de servicio (entrega al menos una vez) |
| `RECONNECT_DELAY_S` | `3.0` | Espera entre reintentos del puerto serial |

El suscriptor `mqtt_subscriber.py` tiene su propio bloque `MQTT_HOST`/`MQTT_PORT`
que **debe coincidir** con el del puente.

---

## 6. Flujo de datos

```
┌──────────────┐   USB serial    ┌─────────────────────┐   MQTT publish   ┌────────────┐
│  XIAO RP2350 │ ───"TLM ..."──► │ serial_mqtt_bridge  │ ───JSON/QoS1───► │   Broker   │
│  (firmware)  │   115200 bd     │  parseo + JSON      │  jaguar/.../<p>  │    MQTT    │
└──────────────┘                 └─────────────────────┘                  └─────┬──────┘
                                                                                │ subscribe
                                                                          ┌─────▼──────┐
                                                                          │ subscriber │
                                                                          │  / dashboard│
                                                                          └────────────┘
```

---

## 7. Parseo de la telemetría

El firmware emite **1 línea `TLM` por segundo** (`main.cpp:556-568`):

```
[0000012345] TLM EST=IDLE INT=25.3C EXT=24.1C SP=50C VENT=OFF COMPUERTA=CERRADA AIN1=0 AIN2=0 EN=0
```

El puente extrae los campos con expresiones regulares y descarta las líneas que no
son telemetría (logs `FSM[...]`, banner de arranque, confirmaciones de comandos).

### Mapeos aplicados

| Firmware (español) | Payload (inglés) |
|--------------------|------------------|
| `COMPUERTA=ABIERTA`  | `damper_state: "OPEN"` |
| `COMPUERTA=CERRADA`  | `damper_state: "CLOSED"` |
| `COMPUERTA=ABRIENDO` | `damper_state: "OPENING"` |
| `COMPUERTA=CERRANDO` | `damper_state: "CLOSING"` |
| `VENT=ON` / `VENT=OFF` | `fan_active: true` / `false` |

---

## 8. Estructura del payload JSON

```json
{
  "timestamp": "2026-07-08T21:15:00Z",
  "device_id": "XIAO_RP2350_JAIR",
  "state_machine": "COOLING",
  "sensors": {
    "temperature_internal_c": 62.4,
    "temperature_external_c": 28.0,
    "setpoint_c": 55.0
  },
  "actuators": {
    "fan_active": true,
    "damper_state": "OPENING"
  },
  "diagnostics": {
    "uptime_ms": 98765,
    "override_internal": true,
    "override_external": false,
    "hbridge": { "ain1": 0, "ain2": 1, "stby": 1 }
  }
}
```

- `timestamp` — hora **UTC** del host en formato ISO-8601 (el firmware solo aporta
  `millis()`, disponible como `diagnostics.uptime_ms`).
- `diagnostics` — bloque extra de nivel industrial: uptime, overrides manuales
  activos y estado de los GPIOs del puente H TB6612FNG.

---

## 9. Robustez

| Escenario | Comportamiento |
|-----------|----------------|
| Broker MQTT caído al arrancar | Reintenta `connect` cada `RECONNECT_DELAY_S` hasta lograrlo |
| Broker cae en caliente | `paho-mqtt` reconecta automáticamente (backoff 1–30 s) con `loop_start()` |
| Puente cae inesperadamente | El broker publica `offline` vía **Last Will & Testament** en `jaguar/telemetry/status/jair` |
| USB desconectado / error serial | Cierra el puerto, espera y reintenta abrirlo sin tumbar el proceso |
| Línea serial corrupta | Se decodifica con `errors="replace"` y se ignora si no es telemetría |
| Línea `TLM` incompleta (glitch) | Se descarta con aviso; no reinicia el puerto ni tumba el proceso |
| `Ctrl+C` | Publica `offline`, cierra MQTT y el puerto de forma ordenada |

---

## 10. Tópicos MQTT publicados

| Tópico | Contenido | Retain |
|--------|-----------|:------:|
| `jaguar/telemetry/data/jair` | Payload JSON de telemetría (1 Hz) | No |
| `jaguar/telemetry/status/jair` | `online` / `offline` (LWT) | Sí |

Para escuchar todo con `mosquitto_sub`:

```bash
mosquitto_sub -h 10.146.0.87 -t 'jaguar/telemetry/#' -v
```

---

## 11. Ejemplo de logs en consola

**Puente:**
```
21:30:39  INFO     Perfil : JAIR  (Extractor — Nave Jair)
21:30:39  INFO     MQTT conectado a 10.146.0.87:1883 (perfil JAIR)
21:30:40  INFO     Puerto serial abierto. Escuchando telemetría...
21:30:41  INFO     PUB #1     [OK] COOLING  INT=62.4°C EXT=28.0°C SP=55°C FAN=True DAMPER=OPENING
```

**Suscriptor:**
```
21:30:41  🔥 XIAO_RP2350_JAIR   COOLING  INT=62.4°C EXT=28.0°C SP=55.0°C  FAN=🌀ON  COMPUERTA=OPENING
```

---

## 12. Solución de problemas

| Síntoma | Causa / solución |
|---------|------------------|
| `No module named 'paho'` / `'serial'` | Ejecuta `pip install -r requirements.txt` |
| `could not open port 'COM5'` | Puerto ocupado (cierra el monitor serial / dashboard) o número de COM incorrecto en `SERIAL_PORT` |
| Conecta a MQTT pero no publica | El XIAO no emite `TLM` (revisa firmware/baudrate) |
| El suscriptor no ve nada | `MQTT_HOST` distinto entre puente y suscriptor, o firewall bloqueando el 1883 |
| `Perfil desconocido` | El suscriptor solo acepta `JAIR` (o ejecútalo sin argumentos) |
