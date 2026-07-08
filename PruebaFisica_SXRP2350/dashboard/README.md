# Dashboard de Telemetría — Extracción de Aire Caliente

Panel de control web para visualizar en tiempo real la telemetría del sistema de
extracción de aire caliente **Jaguar de México**, ejecutándose sobre el
microcontrolador **Seeed XIAO RP2350** y conectado por **USB (Web Serial API)**.

> Ing. Jair Molina Arce · Firmware `src/main.cpp` · Estética *glassmorphism* dark mode.

---

## 1. Descripción general

El dashboard es un **único archivo autónomo** (`index.html`): no requiere build,
servidor, ni dependencias externas más allá de las fuentes de Google (con
degradación elegante si no hay internet). Se abre directamente en el navegador y
usa la **Web Serial API** para leer el puerto `COM` del XIAO RP2350 a **115200
baudios**, parseando la línea de telemetría que el firmware emite cada segundo.

```
dashboard/
├── index.html   ← el dashboard completo (HTML + CSS + JS en un solo archivo)
└── README.md    ← este documento
```

---

## 2. Requisitos

| Requisito | Detalle |
|-----------|---------|
| Navegador | **Chrome** o **Edge** de escritorio (con soporte de Web Serial API) |
| Sistema   | Windows / macOS / Linux |
| Hardware  | Seeed XIAO RP2350 con el firmware `src/main.cpp` cargado |
| Baudrate  | **115200** (fijo, coincide con `Serial.begin(115200)` del firmware) |

> ⚠️ **Firefox y Safari no soportan Web Serial API.** El dashboard lo detecta
> automáticamente y muestra un aviso en el panel de control.

---

## 3. Puesta en marcha

1. Carga el firmware `src/main.cpp` en el XIAO RP2350 (PlatformIO / Arduino IDE).
2. Conecta el XIAO por USB al equipo.
3. **Cierra cualquier monitor serial** que tenga tomado el puerto (el Serial
   Monitor de PlatformIO/Arduino IDE, PuTTY, etc.). Un solo proceso puede abrir
   el puerto a la vez.
4. Abre `dashboard/index.html` en Chrome/Edge (doble clic funciona: Web Serial
   opera en contexto `file://`).
5. Pulsa **🔌 Conectar Dispositivo Serial** y selecciona el puerto `COM` del
   dispositivo en el diálogo del navegador.
6. La telemetría comenzará a fluir en menos de 1 segundo.

Para **desconectar**, pulsa el mismo botón (ahora "⏹ Desconectar").

---

## 4. Protocolo de telemetría

El firmware imprime **una línea `TLM` por ciclo (1 Hz)** con este formato exacto
(ver `main.cpp:556-568`):

```
[0000012345] TLM EST=IDLE INT=25.3C EXT=24.1C SP=50C VENT=OFF COMPUERTA=CERRADA AIN1=0 AIN2=0 EN=0
```

### Campos parseados

| Campo        | Regex                    | Significado |
|--------------|--------------------------|-------------|
| `[…]`        | `\[(\d+)\]`              | Timestamp `millis()` → se muestra como *uptime* |
| `EST=`       | `EST=(\w+)`              | Estado de la FSM |
| `INT=`       | `INT=(-?\d+\.?\d*)C`     | Temperatura interna (°C) |
| `EXT=`       | `EXT=(-?\d+\.?\d*)C`     | Temperatura externa (°C) |
| `SP=`        | `SP=(\d+)C`              | Setpoint activo (°C) |
| `VENT=`      | `VENT=(ON\|OFF)`         | Estado del ventilador |
| `COMPUERTA=` | `COMPUERTA=(\w+)`        | Posición de compuertas |
| `AIN1/2 EN`  | `AIN1=(\d)` …            | GPIOs del puente H TB6612FNG |
| `(OVR)`      | `INT=[^ ]*\(OVR\)`       | Marca de *override* manual activo |

El dashboard también recibe y colorea las líneas de log de la FSM
(`[…] FSM[ESTADO] mensaje`), sin intentar parsearlas como telemetría.

### Estados de la FSM

| Estado    | Color   | Descripción en el panel |
|-----------|---------|--------------------------|
| `INIT`    | violeta | Inicializando · safe state |
| `READING` | cian    | Evaluando sensores NTC |
| `COOLING` | naranja | Enfriamiento activo |
| `IDLE`    | verde   | En reposo · dentro de rango |
| `ERROR`   | rojo    | Fallo de sensor · safe state |
| `LOCKOUT` | rojo    | Bloqueo · requiere mantenimiento |

### Posiciones de compuerta

| Valor      | Representación visual |
|------------|-----------------------|
| `CERRADA`  | Rejilla gris (baja) |
| `ABRIENDO` / `CERRANDO` | Rejilla ámbar parpadeante (movimiento ~3 s) |
| `ABIERTA`  | Rejilla verde (alta, con brillo) |

---

## 5. Componentes de la interfaz

### KPIs principales

- **🌡️ Temp. Interna / ❄️ Temp. Externa** — valor numérico monoespaciado con
  color dinámico frío→caliente (cian → ámbar → rojo) calculado **relativo al
  setpoint**, más una barra tipo termómetro. Indica cuándo la lectura proviene de
  un *override* manual (`⚡`).
- **🚪 Compuertas** — texto de estado + rejilla animada del actuador FIT0803.
- **🌀 Ventilador** — icono de **aspas que giran en CSS** cuando `VENT=ON`
  (MR1238E48B-FSR, 48 V vía MOSFET NMOS).

### Fila secundaria

- **⚙️ Estado del Sistema (FSM)** — estado actual con color y descripción.
- **🎯 Setpoint + GPIOs** — setpoint activo y estado de los pines `AIN1`, `AIN2`,
  `STBY` del puente H, más el *uptime* del dispositivo.

### Consola y control

- **📡 Flujo de Telemetría** — consola en vivo con coloreado por tipo:
  `TLM` (hielo), `FSM` (violeta), `WARN`/errores (ámbar), comandos enviados
  (verde). Retiene las últimas 250 líneas.
- **🎛️ Control Manual (Demo)** — envío de comandos al firmware.

---

## 6. Comandos de control (demo)

Permiten forzar condiciones térmicas sin calentar físicamente el NTC — útil para
la defensa en vivo. Corresponden al parser de comandos del firmware
(`main.cpp:604-639`).

| Comando        | Efecto |
|----------------|--------|
| `SET:<°C>`     | Fija el setpoint manualmente (ignora el DIP switch) |
| `SET:0`        | Desactiva el override → vuelve al DIP switch |
| `TEMP:<°C>`    | Fuerza la temperatura interna |
| `TEMP:AUTO`    | Vuelve a leer el NTC interno |
| `EXT:<°C>`     | Fuerza la temperatura externa |
| `EXT:AUTO`     | Vuelve a leer el NTC externo |

**Ejemplo de demo:** escribe `TEMP:65` → el sistema supera el umbral, transiciona
a `COOLING`, abre las compuertas y enciende el ventilador. Luego `TEMP:AUTO` para
regresar a la lectura real.

Puedes escribir el comando en el campo de texto (Enter para enviar) o usar los
*chips* de acceso rápido.

---

## 7. Detalles técnicos de implementación

- **Stack:** HTML + CSS + JavaScript *vanilla* (sin frameworks ni build).
- **Lectura serial:** `navigator.serial.requestPort()` → `port.open({baudRate:115200})`
  → bucle de lectura con `TextDecoder` en modo *stream* y *buffering* por líneas
  (`\n`), tolerante a `\r`.
- **Escritura:** `writer.write(TextEncoder … cmd + "\n")`.
- **Color de temperatura:** interpolación lineal (`lerp`) entre tres puntos
  (cian → ámbar → rojo) en función de la posición de la temperatura respecto al
  rango `[SP-15, SP+10]`.
- **Diseño:** *glassmorphism* (`backdrop-filter: blur`), fondo aurora animado,
  fuentes `Inter` (UI) y `JetBrains Mono` (valores numéricos), totalmente
  responsivo (grid adaptable a 4/2/1 columnas).

---

## 8. Solución de problemas

| Síntoma | Causa probable / solución |
|---------|---------------------------|
| El botón no abre el diálogo de puertos | Navegador sin Web Serial (usa Chrome/Edge de escritorio) |
| "Conexión cancelada o fallida" | Puerto ocupado por otro monitor serial → ciérralo |
| Conecta pero no llega telemetría | Baudrate incorrecto en el firmware, o el XIAO no está ejecutando `main.cpp` |
| Valores en blanco (`--`) | Aún no ha llegado la primera línea `TLM`; espera ~1 s |
| Fuentes distintas a las esperadas | Sin conexión a internet (Google Fonts) → usa fuentes del sistema como *fallback* |

---

## 9. Compatibilidad de navegadores

| Navegador | Web Serial | Estado |
|-----------|:----------:|--------|
| Chrome (escritorio)  | ✅ | Recomendado |
| Edge (escritorio)    | ✅ | Recomendado |
| Opera (escritorio)   | ✅ | Compatible |
| Firefox              | ❌ | No soportado |
| Safari               | ❌ | No soportado |
| Navegadores móviles  | ❌ | No soportado |

v1.1.1