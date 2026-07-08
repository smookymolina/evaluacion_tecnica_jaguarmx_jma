# Pruebas por capas — Puente Serial → MQTT

Scripts para verificar el sistema **de forma incremental**, de lo más simple
(sin broker ni hardware) a lo end-to-end. Si algo falla, la capa que se rompe
te dice **exactamente dónde** está el problema.

> Ejecuta todo desde esta carpeta `bridge/tests/`.
> Config esperada: broker **`10.146.0.87:1883`**, extractor **JAIR** en **COM5**,
> tópicos `jaguar/telemetry/data/jair` y `jaguar/telemetry/status/jair`.

| Capa | Qué prueba | ¿Necesita broker? | ¿Necesita XIAO? | Script |
|:----:|------------|:-----------------:|:---------------:|--------|
| 0 | Parseo `TLM` → JSON | ❌ | ❌ | `capa0_test_parse.py` |
| 1 | Dependencias instaladas | ❌ | ❌ | `capa1_check_deps.py` |
| 2 | Broker alcanzable (TCP) | ✅ | ❌ | `capa2_check_broker.ps1` |
| 3 | Broker + tópicos + suscriptor | ✅ | ❌ | `capa3_fake_publisher.py` |
| 4 | El XIAO emite telemetría | ❌ | ✅ | `capa4_serial_monitor.py` |
| 5 | Pipeline completo | ✅ | ✅ | *(usa el puente + suscriptor)* |

---

## Capa 0 — Parseo (offline)

Convierte una línea `TLM` real en JSON y valida cada campo (incluye override
`(OVR)`, mapeo de compuerta y descarte de líneas incompletas).

```bash
python capa0_test_parse.py
```
✔️ Éxito: imprime el JSON y `✅ CAPA 0 OK`.

---

## Capa 1 — Dependencias

```bash
python capa1_check_deps.py
```
✔️ Éxito: `pyserial` y `paho-mqtt` marcados con ✅.
✖️ Si falla: `pip install -r ../requirements.txt`.

---

## Capa 2 — Broker alcanzable (TCP)

Prueba de red pura (no publica nada). Es PowerShell porque usa `Test-NetConnection`:

```powershell
.\capa2_check_broker.ps1
```
✔️ Éxito: `TcpTestSucceeded : True` → el broker escucha y el firewall deja pasar.
✖️ Si falla: Mosquitto no corre en `10.146.0.87`, IP incorrecta, red distinta o
puerto 1883 bloqueado. No tiene sentido seguir a la Capa 3 hasta arreglar esto.

---

## Capa 3 — Broker + tópicos, SIN el XIAO

Verifica que el broker reparte y el suscriptor lee, usando un **publicador falso**
en vez del hardware. Necesitas **dos terminales**.

**Terminal A** (suscriptor, se queda escuchando):
```bash
python ../mqtt_subscriber.py
```

**Terminal B** (publica telemetría de prueba):
```bash
python capa3_fake_publisher.py          # un solo mensaje
python capa3_fake_publisher.py --loop   # 1 mensaje/seg, temperatura variable
```

✔️ Éxito: la Terminal A imprime algo como:
```
16:35:55  🔥 XIAO_RP2350_JAIR   COOLING  INT=62.4°C EXT=28.0°C SP=55.0°C  FAN=🌀ON  COMPUERTA=OPEN
```
Con esto sabes que **el broker está operativo** aunque aún no tengas el XIAO.

---

## Capa 4 — ¿El XIAO emite telemetría? (SIN MQTT)

Confirma que el firmware escupe líneas `TLM` por el puerto, antes de meter el broker.

```bash
python capa4_serial_monitor.py            # COM5 @ 115200
python capa4_serial_monitor.py COM6       # si el puerto es otro
```
✔️ Éxito: aparece una línea `... TLM EST=... INT=... <-- TLM #n OK` cada segundo.
✖️ Si falla al abrir: revisa el nº de COM (Administrador de dispositivos) o cierra
el monitor serial que tenga el puerto ocupado. Ajusta luego `SERIAL_PORT` en
`../serial_mqtt_bridge.py`.

Equivalente sin script: `python -m serial.tools.miniterm COM5 115200`.

---

## Capa 5 — Pipeline completo (end-to-end)

Con el XIAO conectado y el broker vivo, **dos terminales**:

```bash
# Terminal A — el puente real
python ../serial_mqtt_bridge.py     # verás:  PUB #1 [OK] COOLING INT=... 

# Terminal B — el suscriptor
python ../mqtt_subscriber.py        # verás la misma telemetría desde el broker
```
✔️ Éxito: cada `PUB #n [OK]` del puente aparece como una línea de telemetría en el
suscriptor. Todo el flujo XIAO → serial → puente → broker → suscriptor funciona.

---

## Diagnóstico rápido

| Falla en… | Causa probable |
|-----------|----------------|
| Capa 2 | Broker apagado / red / firewall (puerto 1883) |
| Capa 3 (pero 2 pasa) | Configuración de tópicos o del broker |
| Capa 4 | Firmware, baudrate o número de COM |
| Capa 5 (pero 3 y 4 pasan) | El puente: COM ocupado, baudrate, o el XIAO no emite `TLM` |

> Nota Windows: los scripts fuerzan salida UTF-8 para que los iconos (🔌🔥🌀) y los
> acentos no rompan la consola `cp1252`.
