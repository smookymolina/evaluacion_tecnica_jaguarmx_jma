# CLAUDE.md — Proyecto: Evaluación Técnica Jaguar de México
> Instrucciones de contexto para el agente de IA (Claude / Cowork)
> Candidato: **Ing. Jair Molina Arce**
> Herramienta: Claude (Anthropic) — uso documentado en ETISEJr_JairMolina.md

---

## Rol del agente en este proyecto

Eres un **Ingeniero Senior de Sistemas Embebidos** asistiendo a Jair Molina Arce en la Evaluación Técnica de Jaguar de México para la vacante de Ingeniero de Sistemas Embebidos Jr.

Tu función principal es:
- Generar código MicroPython correcto y robusto para el RP2040/RP2350
- Asistir en el diseño del esquemático y PCB en KiCad
- Ayudar a extender la simulación en Wokwi
- Responder dudas técnicas con base en datasheets reales
- Documentar el uso de IA de forma transparente

**Nunca** generes código incorrecto para "ahorrar tiempo". Si no estás seguro, dilo explícitamente.

---

## Contexto del sistema a diseñar

**Sistema:** Extracción de aire caliente para gabinete de telecomunicaciones

**Objetivo:** Comparar TEMP_INT vs TEMP_EXT y controlar automáticamente:
- Compuertas mecánicas (actuador lineal FIT0803 via TB6612FNG)
- Ventilador (MR1238E48B-FSR 48V via MOSFET NMOS)

**Plataformas:**
- Simulación Wokwi: Raspberry Pi Pico (RP2040) — plantilla base de Jaguar
- Sesión en vivo:   Seeed XIAO RP2350 — encapsulado difiere del Pico

---

## Mapa de GPIOs (CRÍTICO — no cambiar sin justificación)

| Señal     | GPIO  | Dirección        | Función                          |
|-----------|-------|------------------|----------------------------------|
| TEMP_INT  | GP26  | Entrada analógica| ADC0 — temperatura interna       |
| TEMP_EXT  | GP27  | Entrada analógica| ADC1 — temperatura externa       |
| SW1       | GP6   | Entrada (pull-up)| Bit 0 del setpoint DIP           |
| SW2       | GP7   | Entrada (pull-up)| Bit 1 del setpoint DIP (Remap MOD-1)|
| SW3       | GP0   | Entrada (pull-up)| Bit 2 del setpoint DIP           |
| AIN1      | GP2   | Salida digital   | Dirección 1 puente H             |
| AIN2      | GP1   | Salida digital   | Dirección 2 puente H             |
| MOTOR_EN  | GP3   | Salida digital   | Habilitación TB6612FNG           |
| VENT      | GP4   | Salida digital   | Control ventilador (via MOSFET)  |

---

## Componentes — parámetros técnicos clave

### NTC TT05-10KC8-1S-T105-1500
- R0 = 10,000 Ω @ T0 = 25°C (298.15 K)
- **Beta = 3435 K** ← CORREGIDO (el cronograma inicial usaba 3950 K por error; datasheet TEWA/TME indica 3435 K; diferencia ~4°C a 50°C)
- Rango: -40°C a **105°C** ← CORREGIDO (T105 en el part number = Tmax 105°C; el doc inicial decía 125°C)
- **Circuito:** divisor de voltaje con R_ref = 10kΩ (misma magnitud que R0 para maximizar sensibilidad)
- **Conversión:** ecuación Beta → T(K) = 1 / [(1/T0) + (1/Beta) × ln(R_ntc/R0)]
- **Filtrado:** promedio móvil de 8 muestras ADC (descartar max y min)
- **Datasheet:** ver `datasheets/NTC_TT05.md`

### TB6612FNG (Puente H)
- VM (motor): 5V para el FIT0803
- VCC (lógica): 3.3V del RP2350
- **CRÍTICO:** pin STBY debe mantenerse HIGH para operar
- Canal A usado para FIT0803:
  - Abrir compuertas:  AIN1=0, AIN2=1, MOTOR_EN=1
  - Cerrar compuertas: AIN1=1, AIN2=0, MOTOR_EN=1
  - Motor detenido:    AIN1=0, AIN2=0, MOTOR_EN=0 (safe state)

### MR1238E48B-FSR (Ventilador)
- Alimentación: 48V DC — **NO conectar directamente al GPIO**
- Control: MOSFET NMOS (ej. IRL520N): Vgs(th)=1.0–2.0V (típico 1.3V), compatible 3.3V GPIO
- Protección: diodo flyback 1N4007 en paralelo con ventilador; capacitor 100µF/63V en rail 48V
- Pull-down 10kΩ en gate para estado seguro sin señal
- **Datasheet:** ver `datasheets/MR1238E48B-FSR.md` y `datasheets/IRL520N.md`

### FIT0803 (Actuador lineal)
- Tensión nominal: **6V** (rated); el sistema lo opera a **5V** per spec Jaguar
- A 5V la velocidad es ~5.8 mm/s (vs 7 mm/s @ 6V) → travel ~1.72s → `ACTUATOR_TRAVEL_MS = 3000` da margen ×1.75
- Controlado por TB6612FNG canal A
- **Calibrar tiempo de recorrido con cronómetro en la sesión en vivo**
- **Datasheet:** ver `datasheets/FIT0803.md`

---

## Arquitectura de firmware (no cambiar estructura sin motivo)

```
main.py         ← entry point, banner, manejo de errores críticos
  └── fsm.py    ← FSM principal (INIT→READING→COOLING/IDLE/ERROR)
        ├── adc_ntc.py      ← lectura NTC + conversión Beta
        ├── dip_switch.py   ← DIP switch 3-bit + setpoints + histéresis
        ├── hbridge.py      ← control TB6612FNG (open/close/stop)
        └── fan.py          ← control MOSFET ventilador (on/off)
```

**Estados FSM:**
- `INIT`    → configuración y auto-diagnóstico
- `READING` → adquisición temperatura y evaluación (1 Hz)
- `COOLING` → TEMP_INT > TEMP_EXT: compuertas abiertas + fan ON
- `IDLE`    → TEMP_INT ≤ TEMP_EXT: compuertas cerradas + fan OFF
- `ERROR`   → lectura inválida → safe state → recovery tras 30s

**Histéresis:** ±1°C alrededor del setpoint para evitar chattering del actuador

**Watchdog:** RP2350 WDT timeout = 8000ms (se alimenta al inicio de cada step)
- Durante el travel del actuador FIT0803 (~3s bloqueante), `hbridge._safe_sleep_ms()` lo alimenta cada 500ms via callback `set_wdt_feed()` registrado desde `fsm.py`

---

## Setpoints DIP switch

| Código (SW3 SW2 SW1) | Setpoint |
|----------------------|----------|
| 000 | 40°C |
| 001 | 45°C |
| 010 | 50°C |
| 011 | 55°C |
| 100 | 60°C |
| 101 | 65°C |
| 110 | 70°C |
| 111 | 75°C |

*Lógica pull-up: pin LOW (presionado) = bit 1*

---

## Guías de diseño PCB (para KiCad)

- **Stackup:** 2 capas, FR4, 1.6mm, Cu 1oz
- **Plano GND:** capa trasera continua, via stitching en zona analógica
- **Separación física:** zona potencia (TB6612FNG + MOSFET) ≠ zona analógica (NTC + ADC)
- **Trazas potencia motor:** ancho ≥ 1.5mm
- **Trazas analógicas:** ≤ 0.3mm, no cruzar bajo componentes digitales
- **Desacoplamiento:** 100nF cerámico + 47µF electrolítico en VM del TB6612FNG
- **Protecciones:** TVS SMBJ3.3A en entradas analógicas GP26/GP27

---

## Entregables requeridos (Fase 1 — take-home)

Archivo ZIP: `ETISEJr_JairMolina.zip`

```
ETISEJr_JairMolina.zip
├── firmware/
│   ├── main.py
│   ├── fsm.py
│   ├── adc_ntc.py
│   ├── dip_switch.py
│   ├── hbridge.py
│   ├── fan.py
│   └── README.md
├── kicad/
│   ├── jaguar_extractor.kicad_sch
│   └── jaguar_extractor.kicad_pcb
└── ETISEJr_JairMolina.md
    ├── # Simulación Wokwi  (URL + descripción)
    ├── # Cuestionario       (6 preguntas)
    └── # Uso de AI          (log detallado)
```

> **Nota:** La carpeta `datasheets/` (referencias técnicas + links de PDFs) es un recurso de trabajo interno del proyecto y no forma parte del ZIP de entrega. Contiene un `.md` por componente con specs verificadas contra datasheets reales.

Plantilla Wokwi base: https://wokwi.com/projects/468449090390286337
Entrega: software@jaguar.mx — "Evaluación Técnica — Jair Molina Arce"

---

## Instrucciones para el agente

### HACER siempre:
- Usar los números de GPIO exactos del mapa anterior
- Documentar cualquier decisión de diseño que se aparte del documento original
- Validar que el código MicroPython sea compatible con `machine` del RP2040/RP2350
- Proponer histéresis y manejo de estado seguro (fail-safe) en cualquier cambio de control
- Usar `time.ticks_ms()` y `time.ticks_diff()` para medir tiempo en MicroPython (no `time.time()` para intervalos cortos)
- Comentar el código en español para coherencia con el proyecto

### NO HACER:
- No cambiar los números de GPIO sin verificar el mapa del documento oficial
- No eliminar el watchdog timer sin justificación técnica
- No usar `time.sleep()` en el loop principal (usar compensación de tiempo)
- No asumir que los pines del Seeed XIAO RP2350 son iguales a los del Pico (verificar datasheet)
- No sugerir bibliotecas externas que no estén disponibles en MicroPython estándar
- No hacer cálculos NTC con la ecuación Steinhart-Hart completa (no tenemos los 3 coeficientes; usar Beta)

### Cuando el agente genere código nuevo:
1. Indicar en qué archivo va (`# archivo: nombre.py`)
2. Indicar si reemplaza completamente el archivo o es una adición
3. Ejecutar un check mental de: ¿los GPIOs son correctos? ¿hay manejo de errores?

---

## Decisiones técnicas ya tomadas (no revertir)

| Decisión | Justificación |
|---|---|
| MicroPython (no C/C++) | Iteración rápida en 4 días; ciclo de control a 1Hz no requiere C |
| Beta equation (no Steinhart-Hart) | Solo tenemos 2 puntos del datasheet; Beta es suficiente para ±0.5°C |
| **Beta = 3435 K (no 3950 K)** | **CORRECCIÓN:** datasheet TEWA/TME indica 3435 K; usar 3950 K daba error de ~4°C a 50°C |
| **Tmax = 105°C (no 125°C)** | **CORRECCIÓN:** "T105" en el part number indica Tmax = 105°C según datasheet |
| R_ref = 10kΩ = R0 | Maximiza sensibilidad ADC centrada en 25°C |
| MOSFET NMOS IRL520N | Accionable por 3.3V GPIO (Vgs(th)=1.0–2.0V), soporta 10A, Vds=100V |
| Histéresis ±1°C | Evita chattering del actuador FIT0803 |
| GND unificado en PCB | Recomendación Analog Devices para mixed-signal de baja frecuencia |
| Loop principal 1 Hz | Suficiente para dinámica térmica de gabinete; reduce desgaste actuador |
| WDT feed via callback en hbridge | `_safe_sleep_ms()` alimenta WDT cada 500ms durante travel actuador (best practice industrial) |
| FIT0803 @ 5V (rated 6V) | Jaguar especifica 5V; velocidad ~5.8 mm/s → travel ~1.72s; ACTUATOR_TRAVEL_MS=3000 da margen ×1.75 |
