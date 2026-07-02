# Firmware — Sistema de Extracción de Aire Caliente
**Jaguar de México — Evaluación Técnica**
**Candidato:** Ing. Jair Molina Arce

---

## Descripción

Firmware en **MicroPython** para el control automático de un sistema de extracción de aire caliente en un gabinete de telecomunicaciones. El sistema compara la temperatura interna con la externa y activa/desactiva el ventilador y las compuertas mecánicas según corresponda.

---

## Hardware objetivo

| Componente | Modelo | Notas |
|---|---|---|
| MCU (simulación) | Raspberry Pi Pico (RP2040) | Plantilla Wokwi de Jaguar |
| MCU (producción) | Seeed XIAO RP2350 | Verificar mapeo GPIO antes de sesión en vivo |
| Puente H | TB6612FNG | Canal A para FIT0803 |
| Actuador compuertas | FIT0803 (lineal 5V) | 3s de recorrido estimado |
| Sensores temperatura | NTC TT05-10KC8-1S-T105-1500 | ×2, R0=10kΩ, **Beta=3435K** (corregido) |
| Ventilador | MR1238E48B-FSR | 48V — control via MOSFET NMOS |

---

## ⚠️ Notas críticas de hardware

### TB6612FNG — Pin STBY
El pin STBY **debe estar conectado a 3.3V** en el PCB. Si queda flotante o a GND, el puente H entra en standby y el actuador no responde sin importar el estado de AIN1/AIN2/MOTOR_EN. Este pin no se controla por GPIO — es un tie permanente a VCC.

### NTC — Beta corregido
El firmware usa `BETA = 3435 K` según el datasheet oficial de TEWA/TME para el TT05-10KC8-1S-T105-1500. El cronograma inicial indicaba 3950 K por error — la diferencia es de ~3-4°C a 50°C, significativa para control de temperatura. Ver `../datasheets/NTC_TT05.md`.

### FIT0803 — Tensión y tiempo de viaje
El FIT0803 es rated a 6V, pero el sistema lo alimenta a 5V (per spec Jaguar). A 5V la velocidad es ~5.8 mm/s → travel ~1.72 s. `ACTUATOR_TRAVEL_MS = 3000` incluye margen ×1.75. Calibrar con cronómetro en sesión en vivo.

### Datasheets
Ver carpeta `../datasheets/` para referencias técnicas con especificaciones y links de descarga de todos los componentes.

---

## Estructura de archivos

```
firmware/
├── main.py         # Punto de entrada — ejecutado automáticamente al encender
├── fsm.py          # Máquina de estados finita (FSM) principal
├── adc_ntc.py      # Lectura NTC + conversión Beta equation a °C
├── dip_switch.py   # Lectura DIP switch 3-bit + setpoint de temperatura
├── hbridge.py      # Control TB6612FNG (abrir/cerrar compuertas FIT0803)
├── fan.py          # Control ventilador MR1238E48B-FSR via MOSFET GPIO4
└── README.md       # Este archivo
```

---

## Mapa de GPIOs

| Señal | GPIO | Dirección | Descripción |
|---|---|---|---|
| TEMP_INT | GP26 / ADC0 | Entrada analógica | Temperatura interna gabinete |
| TEMP_EXT | GP27 / ADC1 | Entrada analógica | Temperatura externa |
| SW1 | GP6 | Entrada digital (pull-up) | Bit 0 del setpoint |
| SW2 | GP8 | Entrada digital (pull-up) | Bit 1 del setpoint |
| SW3 | GP0 | Entrada digital (pull-up) | Bit 2 del setpoint |
| AIN1 | GP2 | Salida digital | Dirección 1 del puente H |
| AIN2 | GP1 | Salida digital | Dirección 2 del puente H |
| MOTOR_EN | GP3 | Salida digital | Habilitación TB6612FNG |
| VENT | GP4 | Salida digital | Control ventilador (via MOSFET) |

---

## Lógica de control

| Condición | Compuertas | Ventilador |
|---|---|---|
| TEMP_INT > TEMP_EXT | Abrir (AIN1=0, AIN2=1, EN=1) | ON (GP4=1) |
| TEMP_INT ≤ TEMP_EXT | Cerrar (AIN1=1, AIN2=0, EN=1) | OFF (GP4=0) |
| Lectura inválida | Motor detenido (EN=0) | OFF (GP4=0) |

**Histéresis:** ±1°C alrededor del setpoint para evitar chattering.

---

## Setpoints DIP switch

| SW3 | SW2 | SW1 | Setpoint (°C) |
|---|---|---|---|
| 0 | 0 | 0 | 40 |
| 0 | 0 | 1 | 45 |
| 0 | 1 | 0 | 50 |
| 0 | 1 | 1 | 55 |
| 1 | 0 | 0 | 60 |
| 1 | 0 | 1 | 65 |
| 1 | 1 | 0 | 70 |
| 1 | 1 | 1 | 75 |

*Lógica pull-up: pin=0 (SW presionado) = bit=1*

---

## Diagrama de estados FSM

```
================================================================================
  DIAGRAMA DE ESTADOS — Sistema de Extracción de Aire
  Jaguar de México | Candidato: Ing. Jair Molina Arce
================================================================================

  Leyenda:
    TH_HI = setpoint + 1°C     (umbral de activación — DIP + histéresis)
    TH_LO = setpoint − 1°C     (umbral de desactivación)
    N     = 3 errores ADC consecutivos
    INT   = TEMP_INT  (NTC sensor GP26 / ADC0)
    EXT   = TEMP_EXT  (NTC sensor GP27 / ADC1)

                         [Power On / Reset]
                                │
                                ▼
                     ┌──────────────────────┐
                     │         INIT         │
                     │──────────────────────│
                     │ • hbridge.stop()     │
                     │ • fan.off()          │
                     │ • WDT activado (8 s) │
                     │ • Lee setpoint DIP   │
                     └──────────┬───────────┘
                                │ [siempre]
                                ▼
               ┌────────────────────────────────┐
               │            READING             │◄─────────────────────┐
               │────────────────────────────────│                      │
               │ • Lee TEMP_INT y TEMP_EXT      │          [tras 30 s] │
               │ • Compara vs TH_HI y TEMP_EXT  │                      │
               │ • Lógica conservadora (IDLE by │                      │
               │   default; activa solo si >TH) │                      │
               └─────┬──────────────────┬───────┘                      │
                     │                  │                               │
    [INT > TH_HI     │                  │ [no se cumple                 │
     AND INT > EXT]  │                  │  condición COOLING]      ┌───┴────────────────┐
                     │                  │                           │       ERROR        │
                     ▼                  ▼                           │────────────────────│
          ┌─────────────────┐  ┌────────────────┐ ◄── [N err] ───  │ • fan.off()        │
          │     COOLING     │  │      IDLE      │                   │ • hbridge.stop()   │
          │─────────────────│  │────────────────│ ──── [N err] ───► │ • Safe state 30 s  │
          │ • open_dampers()│  │ • fan.off()    │                   │ • Compuertas: fail │
          │   (~3 s)        │  │ • close_dampers│                   │   in place         │
          │ • fan.on()      │  │   (~3 s)       │                   └────────────────────┘
          └────────┬────────┘  └───────┬────────┘
                   │                   │
    [INT ≤ TH_LO   │                   │ [INT > TH_HI AND INT > EXT]
     OR INT ≤ EXT] │                   │
                   └─────────┬─────────┘
                             │
                    (transición directa COOLING ↔ IDLE
                     sin pasar por READING)

================================================================================
  Tabla de salidas de hardware por estado
================================================================================

  Estado   │ AIN1 │ AIN2 │ EN  │ VENT │ Descripción
  ─────────┼──────┼──────┼─────┼──────┼──────────────────────────────────────
  INIT     │  0   │  0   │  0  │  0   │ Safe state inicial al arrancar
  READING  │  —   │  —   │  —  │  —   │ Sin cambio de salidas (solo evaluación)
  COOLING  │  0   │  1   │  1* │  1   │ Compuertas abiertas + ventilador ON
  IDLE     │  1   │  0   │  1* │  0   │ Compuertas cerradas + ventilador OFF
  ERROR    │  0   │  0   │  0  │  0   │ Motor detenido, ventilador OFF

  * EN=1 solo durante el recorrido del actuador (~3 s); al finalizar, stop() → EN=0.

================================================================================
  Conteo de errores consecutivos (N = 3)
================================================================================

  Cada lectura inválida de read_temperatures() en READING, COOLING o IDLE
  incrementa _errores_consec. Si llega a N=3 → transición a ERROR.
  Cualquier lectura exitosa resetea el contador a 0.

================================================================================
  WDT — Watchdog Timer (8 s timeout)
================================================================================

  Alimentado en 2 momentos:
    1. Al inicio de cada step()            → ciclo normal 1 Hz
    2. Cada 500 ms durante travel actuador → callback desde hbridge._safe_sleep_ms()

  Si el firmware se bloquea > 8 s sin alimentar el WDT, el RP2040/RP2350
  ejecuta un hardware reset automático.
```

---

## Instalación en MCU

```bash
# Usando mpremote
mpremote connect /dev/ttyUSB0 fs cp main.py fsm.py adc_ntc.py dip_switch.py hbridge.py fan.py :/

# Verificar archivos
mpremote connect /dev/ttyUSB0 fs ls

# Ejecutar y ver logs seriales
mpremote connect /dev/ttyUSB0 run main.py
```

---

## Debug en REPL

```python
# Deshabilitar watchdog para debug interactivo
from fsm import ThermalFSM
fsm = ThermalFSM(enable_watchdog=False)
fsm.step()   # Ejecutar un solo paso

# Leer sensores manualmente
from adc_ntc import read_temperatures
ok_i, t_i, ok_e, t_e = read_temperatures()
print(f"INT={t_i:.1f}°C  EXT={t_e:.1f}°C")

# Verificar DIP switch
from dip_switch import dip
print(dip.status_str())

# Controlar actuador manualmente
from hbridge import hbridge
hbridge.open_dampers()
hbridge.close_dampers()

# Controlar ventilador manualmente
from fan import fan
fan.on()
fan.off()
```

---

## Notas para la sesión en vivo (Fase 2)

- El `ACTUATOR_TRAVEL_MS` en `hbridge.py` debe ajustarse con el hardware físico real del FIT0803
- Verificar el mapeo de GPIOs en el Seeed XIAO RP2350 antes de conectar (el encapsulado difiere del Pico)
- El watchdog timer tiene timeout de 8s; el loop principal corre a 1Hz
- Todos los errores de sensor activan el estado seguro (todo OFF) antes de intentar recuperarse
