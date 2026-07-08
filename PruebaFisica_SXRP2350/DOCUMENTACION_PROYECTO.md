# Documentación General del Proyecto
## Sistema de Extracción de Aire Caliente — Jaguar de México

Este documento explica **todo lo que se construyó**, **con qué tecnologías** y
**cuál es el objetivo** de cada pieza. Sirve como visión de conjunto (arquitectura)
del sistema completo: desde el sensor físico hasta la visualización en pantalla.

> Ing. Jair Molina Arce · Hardware: Seeed XIAO RP2350 · Prueba física.

---

## 1. Visión general

El sistema controla y monitorea un **extractor de aire caliente** industrial. Un
microcontrolador lee dos sensores de temperatura (interno/externo), decide cuándo
enfriar mediante una máquina de estados, y acciona compuertas y un ventilador. Toda
esa actividad se **transmite como telemetría** y se puede **visualizar y distribuir**
de dos formas complementarias:

1. **Dashboard web** — conexión directa por USB (Web Serial), visualización local.
2. **Puente Serial → MQTT** — publica la telemetría a un broker para monitoreo
   remoto / múltiples consumidores.

```
          ┌────────────────────────── HARDWARE ──────────────────────────┐
 NTC int ─┤                                                               │
 NTC ext ─┤   Seeed XIAO RP2350  (firmware C++: FSM + control + telemetría)│
 DIP sw  ─┤     │  acciona: puente H (compuertas) + MOSFET (ventilador)    │
          └─────┼─────────────────────────────────────────────────────────┘
                │ USB serial  "TLM ..."  (texto, 115200 bd, 1 Hz)
        ┌───────┴────────┐
        │                │
        ▼                ▼
 ┌─────────────┐   ┌──────────────────┐   MQTT/JSON   ┌────────────┐   ┌────────────┐
 │  Dashboard  │   │ serial_mqtt_     │ ───publish──► │   Broker   │──►│ subscriber │
 │  web (local)│   │ bridge.py (IoT)  │              │    MQTT     │   │ / otros    │
 └─────────────┘   └──────────────────┘              └────────────┘   └────────────┘
```

---

## 2. Componentes construidos

| # | Componente | Archivo(s) | Rol |
|---|------------|-----------|-----|
| 1 | **Firmware embebido** *(base existente)* | `src/main.cpp` | Control físico + emisión de telemetría |
| 2 | **Dashboard web** *(nuevo)* | `dashboard/index.html`, `dashboard/README.md` | Visualización local en tiempo real por USB |
| 3 | **Puente Serial → MQTT** *(nuevo)* | `bridge/serial_mqtt_bridge.py` | Distribución de telemetría a MQTT |
| 4 | **Suscriptor de prueba** *(nuevo)* | `bridge/mqtt_subscriber.py` | Verificación del flujo MQTT en consola |
| 5 | **Documentación** *(nuevo)* | `bridge/README.md`, este archivo | Guías de uso y arquitectura |

---

## 3. El "idioma" común: la línea de telemetría

Toda la cadena se apoya en un formato de texto que el firmware imprime **una vez por
segundo** (`main.cpp:556`):

```
[0000012345] TLM EST=IDLE INT=25.3C EXT=24.1C SP=50C VENT=OFF COMPUERTA=CERRADA AIN1=0 AIN2=0 EN=0
```

| Campo | Significado |
|-------|-------------|
| `[…]` | Tiempo de encendido (`millis()`) |
| `EST=` | Estado de la máquina de estados (INIT/READING/COOLING/IDLE/ERROR/LOCKOUT) |
| `INT=` / `EXT=` | Temperatura interna / externa en °C (sufijo `(OVR)` = override manual) |
| `SP=` | Setpoint activo (°C) |
| `VENT=` | Ventilador ON/OFF |
| `COMPUERTA=` | Posición: ABIERTA/CERRADA/ABRIENDO/CERRANDO |
| `AIN1/AIN2/EN` | GPIOs del puente H (diagnóstico) |

Tanto el dashboard como el puente Python **parsean esta misma línea** con expresiones
regulares. Es el contrato que une todo el sistema.

---

## 4. Componente 1 — Firmware embebido (base)

**Objetivo:** leer los sensores, decidir cuándo enfriar de forma segura y accionar
los actuadores, publicando su estado por serial.

| Tecnología | Objetivo (por qué se usó) |
|------------|---------------------------|
| **Seeed XIAO RP2350** | MCU compacto con ADC de 12 bits y USB nativo para leer NTC y emitir telemetría |
| **C++ (Arduino / PlatformIO)** | Control determinista en tiempo real del hardware |
| **Máquina de estados (FSM)** | Lógica de control segura: enfriar solo cuando corresponde; ir a *safe state* ante fallos |
| **Filtro trimmed-mean + ecuación Beta** | Convertir el ruido del ADC en una temperatura estable y precisa |
| **Watchdog por hardware** | Reiniciar el sistema si el firmware se cuelga (seguridad industrial) |
| **TB6612FNG (puente H) + FIT0803** | Abrir/cerrar las compuertas mecánicas |
| **MOSFET NMOS + MR1238E48B** | Conmutar el ventilador de 48 V desde un GPIO de 3.3 V |

> Este componente ya existía; el resto del proyecto se construyó **alrededor** de su
> salida de telemetría.

---

## 5. Componente 2 — Dashboard web

**Objetivo:** ofrecer una interfaz visual premium que se conecta directamente al
dispositivo por USB (sin instalar nada) para monitoreo y demostración en vivo.

| Tecnología | Objetivo (por qué se usó) |
|------------|---------------------------|
| **HTML5 + CSS3** | Estructura y estética *glassmorphism* (dark mode, gradientes, blur) |
| **Animaciones CSS** | Dinamismo: aspas del ventilador girando, fondo aurora, transiciones de color |
| **JavaScript Vanilla (ES6+)** | Lógica de parseo y actualización de la UI sin frameworks ni build |
| **Web Serial API** | Leer/escribir el puerto COM (115200 bd) **desde el navegador**, sin backend |
| **Tipografías Inter / JetBrains Mono** | UI moderna + números monoespaciados legibles |
| **Diseño responsivo (CSS Grid)** | Adaptación a distintos tamaños de pantalla (4/2/1 columnas) |

**Qué muestra:** temperaturas con color dinámico frío→caliente, estado de compuertas
(rejilla animada), ventilador (aspas girando), estado de la FSM, setpoint, GPIOs y
una consola de telemetría en vivo. Incluye **control manual** (comandos `SET:`,
`TEMP:`, `EXT:`) para forzar condiciones sin calentar el sensor físicamente.

**Ventaja clave:** un solo archivo (`index.html`), se abre con doble clic, sin
servidor ni dependencias. Requiere Chrome/Edge de escritorio.

📄 Detalle completo: `dashboard/README.md`.

---

## 6. Componente 3 — Puente Serial → MQTT

**Objetivo:** llevar la telemetría del cable USB al mundo de red, transformándola en
un **JSON estandarizado** que cualquier sistema (nube, base de datos, otro dashboard)
pueda consumir vía MQTT.

| Tecnología | Objetivo (por qué se usó) |
|------------|---------------------------|
| **Python 3** | Lenguaje ágil para *glue code* de integración IoT |
| **pyserial** | Leer el puerto serial del XIAO con timeouts y recuperación ante desconexión USB |
| **paho-mqtt** | Cliente MQTT con **reconexión automática** al broker y *Last Will & Testament* |
| **MQTT (protocolo)** | Estándar de mensajería IoT ligero: 1 productor → N consumidores |
| **JSON** | Formato de payload universal, legible y fácil de integrar |
| **Expresiones regulares (`re`)** | Extraer los campos de la línea `TLM` de forma robusta |
| **Perfiles configurables** | Un mismo script sirve para varios extractores (cada uno con su COM, `device_id` y tópico) |

**Payload JSON de calidad industrial:**

```json
{
  "timestamp": "2026-07-08T21:15:00Z",
  "device_id": "XIAO_RP2350_JAIR",
  "state_machine": "COOLING",
  "sensors":   { "temperature_internal_c": 62.4, "temperature_external_c": 28.0, "setpoint_c": 55.0 },
  "actuators": { "fan_active": true, "damper_state": "OPENING" },
  "diagnostics": { "uptime_ms": 98765, "override_internal": true, "override_external": false,
                   "hbridge": { "ain1": 0, "ain2": 1, "stby": 1 } }
}
```

- Traduce los términos del firmware (español) a claves estándar en inglés:
  `CERRADA→CLOSED`, `ABRIENDO→OPENING`, `VENT=ON→fan_active:true`.
- Añade un `timestamp` UTC ISO-8601 y un bloque `diagnostics` extra.

**Sistema de perfiles:** cada extractor físico es un perfil en el diccionario
`PROFILES` (puerto COM + ubicación); el `device_id` y el tópico se derivan del
nombre. Se selecciona por línea de comandos:

```bash
python serial_mqtt_bridge.py JAIR
```

> Actualmente configurado con el perfil **JAIR**. Para añadir más extractores basta
> con agregar entradas al diccionario `PROFILES` (ej. `ELIAS`, `RODOLFO`, `CARLOS`…),
> cada una con su puerto COM correspondiente.

**Robustez:** reintenta la conexión al broker y la apertura del puerto serial sin
tumbar el proceso; publica `offline` automáticamente si el puente cae (LWT); cierre
ordenado con `Ctrl+C`.

📄 Detalle completo: `bridge/README.md`.

---

## 7. Componente 4 — Suscriptor de prueba

**Objetivo:** comprobar que el puente publica correctamente **sin necesidad de un
dashboard ni broker propio**, imprimiendo en consola lo que llega al broker.

| Tecnología | Objetivo |
|------------|----------|
| **Python 3 + paho-mqtt** | Suscribirse al broker y recibir los mensajes |
| **JSON parsing** | Interpretar el payload y mostrarlo legible con iconos por estado |

```bash
python mqtt_subscriber.py          # escucha todos los extractores
python mqtt_subscriber.py JAIR     # solo un extractor
```

---

## 8. Resumen de tecnologías y su objetivo

| Capa | Tecnología | Objetivo |
|------|------------|----------|
| **Hardware** | Seeed XIAO RP2350 | Adquisición de sensores y control de actuadores |
| **Hardware** | TB6612FNG, FIT0803, MOSFET, MR1238E48B | Accionar compuertas y ventilador |
| **Firmware** | C++ / Arduino / PlatformIO | Control en tiempo real + telemetría |
| **Firmware** | FSM, watchdog, filtro trimmed-mean | Seguridad y precisión de medición |
| **Frontend** | HTML5, CSS3, animaciones | Interfaz visual premium (glassmorphism) |
| **Frontend** | JavaScript Vanilla ES6+ | Lógica de UI y parseo, sin build |
| **Frontend** | Web Serial API | Conexión USB directa desde el navegador |
| **IoT** | Python 3 | Integración / *glue code* |
| **IoT** | pyserial | Lectura robusta del puerto serial |
| **IoT** | paho-mqtt | Publicación MQTT con reconexión y LWT |
| **IoT** | MQTT + JSON | Distribución estándar de telemetría |
| **IoT** | Expresiones regulares | Parseo del formato `TLM` |

---

## 9. Cómo ejecutar todo el sistema

**Opción A — Dashboard local (USB directo):**
1. Cargar `src/main.cpp` en el XIAO RP2350.
2. Abrir `dashboard/index.html` en Chrome/Edge → **Conectar Dispositivo Serial**.

**Opción B — Telemetría vía MQTT:**
1. `cd bridge && pip install -r requirements.txt`
2. `python serial_mqtt_bridge.py JAIR` (publica al broker).
3. En otra terminal: `python mqtt_subscriber.py` (verifica el flujo).

> Nota: el dashboard (Web Serial) y el puente (pyserial) **no pueden usar el puerto
> COM al mismo tiempo** — un único proceso puede abrirlo. Elige una opción a la vez,
> salvo que dispongas de varios dispositivos.

---

## 10. Estructura del repositorio (piezas de este trabajo)

```
PruebaFisica_SXRP2350/
├── src/
│   └── main.cpp                  # Firmware (base existente)
├── dashboard/
│   ├── index.html               # Dashboard web (Web Serial)
│   └── README.md                # Documentación del dashboard
├── bridge/
│   ├── serial_mqtt_bridge.py    # Puente Serial → MQTT (perfiles)
│   ├── mqtt_subscriber.py       # Suscriptor de prueba
│   ├── requirements.txt         # Dependencias Python
│   └── README.md                # Documentación del puente
└── DOCUMENTACION_PROYECTO.md    # Este documento (visión general)
```
