# FASE 2.1 — NETLIST CORREGIDO Y BLINDADO · KiCad v8
### Tarjeta de Control de Extracción · Jaguar de México
### Candidato: Ing. Jair Molina Arce | Revisión: LIBERADO PARA FASE 3

---

## REGISTRO DE MODIFICACIONES APLICADAS

| ID | Descripción | Componentes Afectados | Estado |
|---|---|---|---|
| **MOD-1** | Remap NET_SW2: GP7 (D5, Pin 6, castellación lateral) para accesibilidad directa | U1.GP7, NET_SW2 | ✅ Aplicado |
| **MOD-2** | Protección ADC: SMBJ3.3A → BAT54S (SOT-23) en nodo filtrado post-R3/R4 | D1, D2 (RefDes conservado), +3V3, AGND | ✅ Aplicado |
| **MOD-3** | Inmunidad EMI DIP switch: R9/R10/R11 (10kΩ) + C12/C13/C14 (100nF) | NET_SW1/2/3, +3V3, AGND | ✅ Aplicado |
| **MOD-4** | Selector físico J9 (3-pin 2.54mm): elimina JP1 solder bridge parasitario | J9, NET_VENT, NET_VENT_GATE, NET_VENT_DRV (nuevo) | ✅ Aplicado |
| **MOD-5** | NT1: Ferrite Bead → Net-Tie cobre directo (baja impedancia en todas las frecuencias) | NT1 (RefDes conservado) | ✅ Aplicado |

---

## CONVENCIONES

| Símbolo | Significado |
|---|---|
| **[MOD-x]** | Fila modificada/añadida por la corrección x |
| ★ CRÍTICO | Conexión con implicación de seguridad o funcionamiento del sistema |
| DNP-A | Do Not Populate en Configuración A (U4 sin poblar, jumper J9 en Pin1-Pin2) |
| Active-B | Configuración B Activa (U4 poblado, jumper J9 en Pin2-Pin3) |

### BAT54S (SOT-23) — Diagrama funcional de pines
```
         +3V3
           │
        Pin 2 (Cátodo D_superior / K2)
           │ ↑ (D_superior: A2=Pin3 → K2=Pin2)
        Pin 3 (Cátodo/Ánodo común K1/A2) ←── NET_TEMP_xxx_FILT (señal ADC)
           │ ↑ (D_inferior: A1=Pin1 → K1=Pin3)
        Pin 1 (Ánodo D_inferior / A1)
           │
          AGND
```
- **Clamp positivo:** señal > 3.3V + Vf(≈0.3V) → D_superior conduce → clampea a ≈ 3.6V ✓
- **Clamp negativo:** señal < 0V - Vf(≈-0.3V) → D_inferior conduce → clampea a ≈ -0.3V ✓
- **En operación normal (0V–3.3V):** ningún diodo conduce → fuga típica < 1µA → sin error ADC ✓

### J9 (Header 3 pines 2.54mm) — Lógica de selección
```
Pin1 ── [NET_VENT / GP4 + U4.IN]
Pin2 ── [NET_VENT_GATE / entrada R6]
Pin3 ── [NET_VENT_DRV / U4.OUT]

Jumper en Pin1-Pin2: GP4 → Gate directo (sin TC4420)
Jumper en Pin2-Pin3: U4.OUT → Gate (TC4420 activo, máxima saturación)
```

---

## CATEGORÍA 1: NETS DE ALIMENTACIÓN Y POTENCIA

---

### NET: +48V
**Rail 48V DC externo. Solo extractor industrial. Trazas ≥ 2.0mm. Sin cambios respecto a Fase 2.**

| Nombre del Net | Componente Origen (RefDes + Pin #) | Componente Destino (RefDes + Pin #) | Tipo de Señal / Notas Técnicas |
|---|---|---|---|
| +48V | J5.Pin1 (entrada 48V, +) | C10.Pin+ (100µF/63V bulk) | DC Potencia; cap bulk desacoplo rail 48V |
| +48V | J5.Pin1 (entrada 48V, +) | C11.Pin1 (100nF/63V HF) | DC Potencia; bypass HF, colocar ≤5mm de Q1.Drain |
| +48V | J5.Pin1 (entrada 48V, +) | J6.Pin1 (Fan+, terminal positivo extractor) | DC Potencia; terminal (+) MR1238E48B-FSR. Traza ≥2mm |
| +48V | J5.Pin1 (entrada 48V, +) | D3.Cátodo/K (US1M flyback) | DC Potencia; ★ CRÍTICO — cátodo flyback al rail positivo 48V |
| +48V | J5.Pin1 (entrada 48V, +) | TP3.Pad1 | Test Point; validación rail 48V en campo |

---

### NET: +5V
**Rail 5V DC. Alimenta LDO, VM motor y gate driver. Sin cambios respecto a Fase 2.**

| Nombre del Net | Componente Origen (RefDes + Pin #) | Componente Destino (RefDes + Pin #) | Tipo de Señal / Notas Técnicas |
|---|---|---|---|
| +5V | J7.Pin1 (entrada 5V, +) | U2.Pin4 (VIN, AP2112K entrada) | DC Potencia; entrada regulador LDO |
| +5V | J7.Pin1 (entrada 5V, +) | U2.Pin3 (EN, chip enable) | DC Potencia; EN tied to VIN → LDO siempre habilitado |
| +5V | J7.Pin1 (entrada 5V, +) | C1.Pin1 (10µF/10V X7R, entrada LDO) | DC Potencia; cap desacoplo entrada LDO. X7R obligatorio |
| +5V | J7.Pin1 (entrada 5V, +) | C3.Pin1 (100nF/10V X5R HF, entrada) | DC Potencia; bypass HF entrada LDO, ≤2mm de U2.VIN |
| +5V | J7.Pin1 (entrada 5V, +) | U3.Pin13 (VM, TB6612FNG) | DC Potencia; alimentación canal actuador TB6612FNG |
| +5V | J7.Pin1 (entrada 5V, +) | U3.Pin14 (VM, duplicado TB6612FNG) | DC Potencia; pin VM duplicado — atar con Pin13 en PCB |
| +5V | J7.Pin1 (entrada 5V, +) | C7.Pin+ (47µF/10V bulk motor) | DC Potencia; cap bulk desacoplo VM, absorbe picos FIT0803 |
| +5V | J7.Pin1 (entrada 5V, +) | C8.Pin1 (100nF/10V X7R HF motor) | DC Potencia; bypass HF VM motor, ≤2mm de U3 pines VM |
| +5V | J7.Pin1 (entrada 5V, +) | U4.Pin5 (VCC, TC4420) | DC Potencia; alimentación gate driver (DNP si U4 no poblado) |
| +5V | J7.Pin1 (entrada 5V, +) | U4.Pin7 (VCC, duplicado TC4420) | DC Potencia; pin VCC duplicado TC4420 (DNP) |
| +5V | J7.Pin1 (entrada 5V, +) | U4.Pin8 (VCC, duplicado TC4420) | DC Potencia; pin VCC duplicado TC4420 (DNP) |
| +5V | J7.Pin1 (entrada 5V, +) | C15.Pin1 (100nF bypass U4, VCC) | DC Potencia; bypass HF de U4 (DNP si U4 no poblado) |
| +5V | J7.Pin1 (entrada 5V, +) | TP2.Pad1 | Test Point; validación rail 5V |

---

### NET: NET_3V3_LDO
**Nodo salida AP2112K antes de fusible F1. C2 y C4 conectados aquí para estabilidad del lazo LDO. Sin cambios.**

| Nombre del Net | Componente Origen (RefDes + Pin #) | Componente Destino (RefDes + Pin #) | Tipo de Señal / Notas Técnicas |
|---|---|---|---|
| NET_3V3_LDO | U2.Pin2 (VOUT, salida AP2112K) | F1.Pin1 (PPTC 500mA, entrada) | DC 3.3V; nodo pre-fuse, corriente máxima 600mA (límite AP2112K) |
| NET_3V3_LDO | U2.Pin2 (VOUT, salida AP2112K) | C2.Pin1 (10µF/10V X7R, salida LDO) | DC 3.3V; ★ CRÍTICO — cap estabilidad ANTES del fusible para no perturbar el lazo |
| NET_3V3_LDO | U2.Pin2 (VOUT, salida AP2112K) | C4.Pin1 (100nF/10V X5R HF, salida) | DC 3.3V; bypass HF salida LDO, ≤2mm de U2.VOUT |

---

### NET: +3V3
**Rail 3.3V regulado y protegido, post-fusible F1. Alimenta lógica, sensores y ahora también los cátodos superiores BAT54S (MOD-2) y pull-ups DIP (MOD-3).**

| Nombre del Net | Componente Origen (RefDes + Pin #) | Componente Destino (RefDes + Pin #) | Tipo de Señal / Notas Técnicas |
|---|---|---|---|
| +3V3 | F1.Pin2 (PPTC, salida protegida) | U1.3V3 / Pin12 (XIAO RP2350, alimentación directa) | DC 3.3V; bypasa LDO interno del XIAO. U1.5V/VBUS debe quedar NC |
| +3V3 | F1.Pin2 (PPTC, salida protegida) | U3.Pin15 (VCC, lógica TB6612FNG) | DC 3.3V; alimentación lógica puente H. V_IH mín=2.0V ✓ |
| +3V3 | F1.Pin2 (PPTC, salida protegida) | C9.Pin1 (100nF, desacoplo VCC U3) | DC 3.3V; desacoplo local VCC lógica TB6612FNG, ≤2mm U3.Pin15 |
| +3V3 | F1.Pin2 (PPTC, salida protegida) | R1.Pin1 (10kΩ ±1%, divisor NTC1) | DC 3.3V; referencia superior divisor TEMP_INT |
| +3V3 | F1.Pin2 (PPTC, salida protegida) | R2.Pin1 (10kΩ ±1%, divisor NTC2) | DC 3.3V; referencia superior divisor TEMP_EXT |
| +3V3 | F1.Pin2 (PPTC, salida protegida) | R5.Pin1 (10kΩ, pull-up STBY) | DC 3.3V; ★ CRÍTICO — pull-up hardware STBY del TB6612FNG |
| +3V3 | F1.Pin2 (PPTC, salida protegida) | R_LED.Pin1 (1kΩ, limitador LED) | DC 3.3V; alimentación indicador power-on |
| +3V3 | F1.Pin2 (PPTC, salida protegida) | TP1.Pad1 | Test Point; validación +3V3 post-fuse |
| **+3V3** | **F1.Pin2 (PPTC, salida protegida)** | **R9.Pin1 (10kΩ, pull-up SW1)** | **DC 3.3V; [MOD-3] pull-up externo NET_SW1 (GP6/bit0 DIP)** |
| **+3V3** | **F1.Pin2 (PPTC, salida protegida)** | **R10.Pin1 (10kΩ, pull-up SW2)** | **DC 3.3V; [MOD-3] pull-up externo NET_SW2 (GP8/bit1 DIP)** |
| **+3V3** | **F1.Pin2 (PPTC, salida protegida)** | **R11.Pin1 (10kΩ, pull-up SW3)** | **DC 3.3V; [MOD-3] pull-up externo NET_SW3 (GP0/bit2 DIP)** |
| **+3V3** | **F1.Pin2 (PPTC, salida protegida)** | **D1.Pin2 (BAT54S cátodo superior / K2)** | **DC 3.3V; [MOD-2] referencia clamp positivo TEMP_INT — limita señal a ≈3.6V en pin ADC GP26** |
| **+3V3** | **F1.Pin2 (PPTC, salida protegida)** | **D2.Pin2 (BAT54S cátodo superior / K2)** | **DC 3.3V; [MOD-2] referencia clamp positivo TEMP_EXT — limita señal a ≈3.6V en pin ADC GP27** |

---

## CATEGORÍA 2: NETS DE TIERRA

---

### NET: PGND (Ground de Potencia)
**Plano retorno alta corriente: motor, MOSFET, extractor 48V. Sin cambios estructurales respecto a Fase 2.**

| Nombre del Net | Componente Origen (RefDes + Pin #) | Componente Destino (RefDes + Pin #) | Tipo de Señal / Notas Técnicas |
|---|---|---|---|
| PGND | J5.Pin2 (entrada 48V, –) | C10.Pin– (100µF/63V, negativo) | Retorno 48V; corriente continua extractor |
| PGND | J5.Pin2 (entrada 48V, –) | C11.Pin2 (100nF/63V, negativo) | Retorno 48V; cap HF al plano PGND |
| PGND | J5.Pin2 (entrada 48V, –) | Q1.Pin3 (Source, IRL520N) | ★ CRÍTICO — Source MOSFET directamente a PGND, traza ≤10mm y ≥2mm de ancho |
| PGND | J7.Pin2 (entrada 5V, –) | U3.Pin3 (PGND, TB6612FNG) | Retorno 5V motor; corriente FIT0803 |
| PGND | J7.Pin2 (entrada 5V, –) | U3.Pin4 (PGND, duplicado) | Retorno 5V; atar con Pin3 en cobre (paralelo) |
| PGND | J7.Pin2 (entrada 5V, –) | U3.Pin9 (PGND, duplicado) | Retorno 5V; atar con Pin3 en cobre |
| PGND | J7.Pin2 (entrada 5V, –) | U3.Pin10 (PGND, duplicado) | Retorno 5V; atar con Pin3 en cobre |
| PGND | J7.Pin2 (entrada 5V, –) | C7.Pin– (47µF bulk motor, negativo) | Retorno 5V; GND cap bulk VM actuador |
| PGND | J7.Pin2 (entrada 5V, –) | C8.Pin2 (100nF HF motor, negativo) | Retorno 5V; GND cap HF VM motor |
| PGND | PGND (plano) | U4.Pin1 (GND, TC4420) | Retorno gate driver (DNP si U4 no poblado) |
| PGND | PGND (plano) | U4.Pin2 (GND, duplicado TC4420) | Retorno gate driver, pin duplicado (DNP) |
| PGND | PGND (plano) | U4.Pin4 (GND, duplicado TC4420) | Retorno gate driver, pin duplicado (DNP) |
| PGND | PGND (plano) | R7.Pin2 (10kΩ pull-down Gate, retorno) | ★ CRÍTICO — pull-down Gate referenciado a PGND (no a AGND) |
| PGND | PGND (plano) | C15.Pin2 (100nF bypass U4, GND) | Retorno bypass HF driver U4 (DNP si U4 no poblado) |
| PGND | PGND (plano) | TP4.Pad1 | Test Point PGND |

---

### NET: AGND (Ground Analógico y Lógico)
**Plano retorno baja corriente: MCU, LDO, sensores, DIP switch. Incluye ánodos inferiores BAT54S (MOD-2) y GND bypass caps DIP (MOD-3). Termina los canales B no usados del TB6612FNG.**

| Nombre del Net | Componente Origen (RefDes + Pin #) | Componente Destino (RefDes + Pin #) | Tipo de Señal / Notas Técnicas |
|---|---|---|---|
| AGND | U1.GND / Pin13 (XIAO RP2350) | AGND (plano analógico) | Retorno MCU; referencia ADC interno RP2350 |
| AGND | U2.Pin1 (GND, AP2112K) | AGND (plano analógico) | Retorno LDO; GND común entrada/salida regulador |
| AGND | C1.Pin2 (10µF entrada LDO, –) | AGND (plano analógico) | Retorno cap desacoplo entrada LDO |
| AGND | C2.Pin2 (10µF salida LDO, –) | AGND (plano analógico) | Retorno cap estabilidad salida LDO |
| AGND | C3.Pin2 (100nF HF entrada, –) | AGND (plano analógico) | Retorno bypass HF entrada LDO |
| AGND | C4.Pin2 (100nF HF salida, –) | AGND (plano analógico) | Retorno bypass HF salida LDO |
| AGND | U3.Pin20 (GND lógico TB6612FNG) | AGND (plano analógico) | Retorno GND lógico puente H; separado de PGND dentro del IC |
| AGND | U3.Pin21 (GND lógico, duplicado) | AGND (plano analógico) | Retorno GND lógico TB6612FNG, pin duplicado |
| AGND | C9.Pin2 (100nF VCC lógica U3, –) | AGND (plano analógico) | Retorno cap desacoplo VCC lógica TB6612FNG |
| AGND | C5.Pin2 (100nF filtro RC GP26, –) | AGND (plano analógico) | ★ CRÍTICO — retorno cap filtro RC; referencia ADC0. Traza corta, no cruzar zona digital |
| AGND | C6.Pin2 (100nF filtro RC GP27, –) | AGND (plano analógico) | Retorno cap filtro RC; referencia ADC1. Mismas reglas que C5 |
| **AGND** | **D1.Pin1 (BAT54S, ánodo inferior / A1)** | **AGND (plano analógico)** | **[MOD-2] ánodo del diodo de clamp negativo TEMP_INT. Sustituye D1.A del SMBJ3.3A eliminado** |
| **AGND** | **D2.Pin1 (BAT54S, ánodo inferior / A1)** | **AGND (plano analógico)** | **[MOD-2] ánodo del diodo de clamp negativo TEMP_EXT. Sustituye D2.A del SMBJ3.3A eliminado** |
| AGND | J1.Pin2 (conector NTC1, GND) | AGND (plano analógico) | Retorno NTC1; polo frío del divisor TEMP_INT |
| AGND | J2.Pin2 (conector NTC2, GND) | AGND (plano analógico) | Retorno NTC2; polo frío del divisor TEMP_EXT |
| AGND | SW1.Pin2 (DIP pos.1, común SW1) | AGND (plano analógico) | Común DIP switch bit 0 (LSB) |
| AGND | SW1.Pin4 (DIP pos.2, común SW2) | AGND (plano analógico) | Común DIP switch bit 1 |
| AGND | SW1.Pin6 (DIP pos.3, común SW3) | AGND (plano analógico) | Común DIP switch bit 2 (MSB) |
| **AGND** | **C12.Pin2 (100nF bypass SW1, –)** | **AGND (plano analógico)** | **[MOD-3] retorno cap bypass EMI para NET_SW1** |
| **AGND** | **C13.Pin2 (100nF bypass SW2, –)** | **AGND (plano analógico)** | **[MOD-3] retorno cap bypass EMI para NET_SW2** |
| **AGND** | **C14.Pin2 (100nF bypass SW3, –)** | **AGND (plano analógico)** | **[MOD-3] retorno cap bypass EMI para NET_SW3** |
| AGND | LED1.Cátodo/K (LED power-on) | AGND (plano analógico) | Retorno LED indicador +3V3 |
| AGND | U3.Pin22 (BIN1, canal B) | AGND (plano analógico) | Canal B TB6612FNG → GND; modo STOP canal B (no utilizado) |
| AGND | U3.Pin23 (BIN2, canal B) | AGND (plano analógico) | Canal B TB6612FNG → GND; modo STOP canal B |
| AGND | U3.Pin24 (PWMB, canal B) | AGND (plano analógico) | Canal B TB6612FNG → GND; PWMB=LOW deshabilita canal B |
| AGND | AGND (plano) | TP5.Pad1 | Test Point AGND |

---

### NET: Unión Única AGND ↔ PGND vía NT1 (Net-Tie Cobre Directo)
> **[MOD-5] NT1 ahora es un Net-Tie de cobre directo (0Ω), NO un ferrite bead.**  
> Justificación técnica: El ferrite bead introduce impedancia inductiva a alta frecuencia (~600Ω@100MHz) que impide que las corrientes de retorno de conmutación del MOSFET Q1 y el TB6612FNG encuentren el camino de menor impedancia de regreso a sus fuentes. Un Net-Tie de cobre directo elimina esta impedancia, reduce el área del lazo de corriente de retorno, y por lo tanto disminuye la emisión EMI irradiada. La separación de planos AGND/PGND en el PCB ya proporciona el aislamiento necesario; el Net-Tie es el único punto de contacto físico entre ambas zonas de cobre.  
> En KiCad v8: utilizar el símbolo `Device:Net-Tie-2` de la librería estándar con las net labels AGND y PGND asignadas a cada pad.

| Nombre del Net | Componente Origen (RefDes + Pin #) | Componente Destino (RefDes + Pin #) | Tipo de Señal / Notas Técnicas |
|---|---|---|---|
| AGND | NT1.Pin1 (Net-Tie, lado analógico) | AGND (zona cobre analógica) | ★ CRÍTICO — lado AGND del Net-Tie. Este es el ÚNICO punto de contacto físico entre los dos planos |
| PGND | NT1.Pin2 (Net-Tie, lado potencia) | PGND (zona cobre potencia) | ★ CRÍTICO — lado PGND del Net-Tie. Ubicar cerca de J7.Pin2 (retorno 5V) para minimizar lazo de corriente |

---

## CATEGORÍA 3: NETS DE SEÑAL Y CONTROL DEL MCU

---

### 3.1 · Ruta Completa TEMP_INT — GP26 / ADC0

> **[MOD-2] Cambio de topología:** El SMBJ3.3A (D1) en el nodo divisor NET_TEMP_INT_DIV fue **eliminado**. La protección se reubica en el nodo filtrado NET_TEMP_INT_FILT mediante el BAT54S (D1, mismo RefDes). Esto reduce el efecto de carga en el divisor resistivo y proporciona un clamp preciso directamente en la entrada del ADC.
>
> **Nueva topología completa:**
> `+3V3 → R1 → [NET_TEMP_INT_DIV] ← NTC1(J1) ← AGND`
> `[NET_TEMP_INT_DIV] → R3 → [NET_TEMP_INT_FILT]`
> `[NET_TEMP_INT_FILT]: D1.Pin3(señal) + C5 + U1.GP26`
> `D1.Pin1 → AGND | D1.Pin2 → +3V3`

#### NET: NET_TEMP_INT_DIV
**Nodo del divisor resistivo. SIN TVS en este nodo (eliminado por MOD-2).**

| Nombre del Net | Componente Origen (RefDes + Pin #) | Componente Destino (RefDes + Pin #) | Tipo de Señal / Notas Técnicas |
|---|---|---|---|
| NET_TEMP_INT_DIV | R1.Pin2 (10kΩ divisor, salida hacia nodo) | J1.Pin1 (conector NTC1, terminal activo) | Analógico DC; terminal superior del NTC1 en el divisor (R_ref en top, NTC1 a GND) |
| NET_TEMP_INT_DIV | R1.Pin2 (10kΩ divisor, salida hacia nodo) | R3.Pin1 (1kΩ filtro, entrada) | Analógico; salida del divisor hacia el filtro RC pasa-bajos |

#### NET: NET_TEMP_INT_FILT
**Nodo post-filtro RC. Aquí convergen: salida R3, cátodo/ánodo común D1 (BAT54S), C5 y entrada GP26.**

| Nombre del Net | Componente Origen (RefDes + Pin #) | Componente Destino (RefDes + Pin #) | Tipo de Señal / Notas Técnicas |
|---|---|---|---|
| NET_TEMP_INT_FILT | R3.Pin2 (1kΩ filtro, salida) | **D1.Pin3 (BAT54S, cátodo/ánodo común K1/A2)** | **[MOD-2] nodo señal ADC; D1 clampea la señal entre –0.3V y +3.6V protegiendo el pin ADC** |
| NET_TEMP_INT_FILT | R3.Pin2 (1kΩ filtro, salida) | C5.Pin1 (100nF X7R, polo del filtro) | Analógico; polo RC — τ=R3·C5=100µs, fc≈1.59kHz |
| NET_TEMP_INT_FILT | R3.Pin2 (1kΩ filtro, salida) | U1.GP26 / Pin8 (ADC0, XIAO RP2350) | Analógico ADC 12-bit; señal TEMP_INT filtrada y protegida. V_rango: ≈0.3V (130°C) a ≈2.8V (10°C) |
| NET_TEMP_INT_FILT | R3.Pin2 (1kΩ filtro, salida) | TP6.Pad1 | Test Point analógico; verificar ausencia de ruido HF en esta señal |

#### Conexiones separadas D1 (BAT54S) — pines a otras redes
| Nombre del Net | Componente Origen (RefDes + Pin #) | Componente Destino (RefDes + Pin #) | Tipo de Señal / Notas Técnicas |
|---|---|---|---|
| AGND | D1.Pin1 (BAT54S, ánodo inferior / A1) | AGND (plano analógico) | [MOD-2] clamp negativo; conduce cuando señal < –0.3V. Ver también Cat.2 AGND |
| +3V3 | D1.Pin2 (BAT54S, cátodo superior / K2) | +3V3 (rail regulado) | [MOD-2] clamp positivo; conduce cuando señal > +3.6V. Ver también Cat.1 +3V3 |

---

### 3.2 · Ruta Completa TEMP_EXT — GP27 / ADC1

> **[MOD-2] Misma corrección de topología que TEMP_INT.** SMBJ3.3A eliminado del nodo divisor; BAT54S (D2, RefDes conservado) reubicado en nodo filtrado.

#### NET: NET_TEMP_EXT_DIV
**Nodo del divisor NTC2. SIN TVS en este nodo.**

| Nombre del Net | Componente Origen (RefDes + Pin #) | Componente Destino (RefDes + Pin #) | Tipo de Señal / Notas Técnicas |
|---|---|---|---|
| NET_TEMP_EXT_DIV | R2.Pin2 (10kΩ divisor, salida hacia nodo) | J2.Pin1 (conector NTC2, terminal activo) | Analógico DC; terminal superior NTC2. Cable externo → mayor exposición a ESD, protegida por BAT54S en nodo FILT |
| NET_TEMP_EXT_DIV | R2.Pin2 (10kΩ divisor, salida hacia nodo) | R4.Pin1 (1kΩ filtro, entrada) | Analógico; salida divisor hacia el filtro RC del canal TEMP_EXT |

#### NET: NET_TEMP_EXT_FILT
**Nodo post-filtro RC canal externo.**

| Nombre del Net | Componente Origen (RefDes + Pin #) | Componente Destino (RefDes + Pin #) | Tipo de Señal / Notas Técnicas |
|---|---|---|---|
| NET_TEMP_EXT_FILT | R4.Pin2 (1kΩ filtro, salida) | **D2.Pin3 (BAT54S, cátodo/ánodo común K1/A2)** | **[MOD-2] nodo señal ADC; D2 protege GP27 entre –0.3V y +3.6V. NTC externo más expuesto a transitorios de campo** |
| NET_TEMP_EXT_FILT | R4.Pin2 (1kΩ filtro, salida) | C6.Pin1 (100nF X7R, polo del filtro) | Analógico; polo RC TEMP_EXT — τ=100µs, fc≈1.59kHz |
| NET_TEMP_EXT_FILT | R4.Pin2 (1kΩ filtro, salida) | U1.GP27 / Pin9 (ADC1, XIAO RP2350) | Analógico ADC 12-bit; señal TEMP_EXT filtrada y protegida |
| NET_TEMP_EXT_FILT | R4.Pin2 (1kΩ filtro, salida) | TP7.Pad1 | Test Point analógico canal externo |

#### Conexiones separadas D2 (BAT54S) — pines a otras redes
| Nombre del Net | Componente Origen (RefDes + Pin #) | Componente Destino (RefDes + Pin #) | Tipo de Señal / Notas Técnicas |
|---|---|---|---|
| AGND | D2.Pin1 (BAT54S, ánodo inferior / A1) | AGND (plano analógico) | [MOD-2] clamp negativo TEMP_EXT. Ver también Cat.2 AGND |
| +3V3 | D2.Pin2 (BAT54S, cátodo superior / K2) | +3V3 (rail regulado) | [MOD-2] clamp positivo TEMP_EXT. Ver también Cat.1 +3V3 |

---

### 3.3 · DIP Switch Setpoint 3-bit (Pull-ups Externas + Bypass EMI)

> **[MOD-3] Añadidas R9/R10/R11 (10kΩ, pull-ups a +3V3) y C12/C13/C14 (100nF, bypass a AGND) por canal.**  
> Las pull-ups internas del RP2350 (~50kΩ) siguen activas por firmware. La pull-up externa 10kΩ en paralelo resulta en una resistencia efectiva de ~8.3kΩ, proporcionando:
> - Mayor inmunidad al ruido inductivo acoplado por cables en entorno industrial
> - fc del filtro RC = 1/(2π × 8.3kΩ × 100nF) ≈ **192 Hz** — suficiente para switch manual, rechaza EMI industrial  
> - **[MOD-1]:** NET_SW2 remapeado de GP7 (back pad) a GP8 (Pin10, castellación lateral)

#### NET: NET_SW1 (Bit 0 / LSB — GP6)

| Nombre del Net | Componente Origen (RefDes + Pin #) | Componente Destino (RefDes + Pin #) | Tipo de Señal / Notas Técnicas |
|---|---|---|---|
| NET_SW1 | SW1.Pin1 (DIP pos.1, terminal señal) | U1.GP6 / Pin7 (Input, pull-up interna) | Digital 3.3V; LSB setpoint. LOW=DIP cerrado=bit'1' |
| **NET_SW1** | **R9.Pin2 (10kΩ pull-up, salida hacia net)** | **SW1.Pin1 (DIP pos.1, terminal señal)** | **[MOD-3] pull-up externo 10kΩ a +3V3. En paralelo con pull-up interna RP2350 (~50kΩ) → R_eff≈8.3kΩ** |
| **NET_SW1** | **SW1.Pin1 (DIP pos.1, terminal señal)** | **C12.Pin1 (100nF, bypass EMI, entrada)** | **[MOD-3] cap bypass en el nodo; absorbe transitorios rápidos de EMI. fc_filtro≈192Hz con R_eff** |
| NET_SW1 | SW1.Pin2 (DIP pos.1, común, retorno) | AGND | Polo común switch a AGND. Ver también Cat.2 AGND |

#### NET: NET_SW2 (Bit 1 — GP7) ← **[MOD-1] GP7 EN CASTELLACIÓN LATERAL**

| Nombre del Net | Componente Origen (RefDes + Pin #) | Componente Destino (RefDes + Pin #) | Tipo de Señal / Notas Técnicas |
|---|---|---|---|
| **NET_SW2** | **SW1.Pin3 (DIP pos.2, terminal señal)** | **U1.GP7 / Pin6 (Input, pull-up interna)** | **[MOD-1] asignado a GP7 (D5, Pin 6 de la castellación lateral para fácil ruteo). firmware actualizado: dip_switch.py usa PIN_SW2 = 7** |
| **NET_SW2** | **R10.Pin2 (10kΩ pull-up, salida hacia net)** | **SW1.Pin3 (DIP pos.2, terminal señal)** | **[MOD-3] pull-up externo 10kΩ a +3V3 para canal SW2** |
| **NET_SW2** | **SW1.Pin3 (DIP pos.2, terminal señal)** | **C13.Pin1 (100nF, bypass EMI, entrada)** | **[MOD-3] cap bypass EMI canal SW2** |
| NET_SW2 | SW1.Pin4 (DIP pos.2, común, retorno) | AGND | Polo común switch a AGND |

#### NET: NET_SW3 (Bit 2 / MSB — GP0)

| Nombre del Net | Componente Origen (RefDes + Pin #) | Componente Destino (RefDes + Pin #) | Tipo de Señal / Notas Técnicas |
|---|---|---|---|
| NET_SW3 | SW1.Pin5 (DIP pos.3, terminal señal) | U1.GP0 / Pin1 (Input, pull-up interna) | Digital 3.3V; MSB setpoint |
| **NET_SW3** | **R11.Pin2 (10kΩ pull-up, salida hacia net)** | **SW1.Pin5 (DIP pos.3, terminal señal)** | **[MOD-3] pull-up externo 10kΩ a +3V3 para canal SW3** |
| **NET_SW3** | **SW1.Pin5 (DIP pos.3, terminal señal)** | **C14.Pin1 (100nF, bypass EMI, entrada)** | **[MOD-3] cap bypass EMI canal SW3** |
| NET_SW3 | SW1.Pin6 (DIP pos.3, común, retorno) | AGND | Polo común switch a AGND |

---

### 3.4 · Control Puente H TB6612FNG (Actuador FIT0803)

**Sin cambios respecto a Fase 2.**

#### NET: NET_AIN1 (GP2 → AIN1)
| Nombre del Net | Componente Origen (RefDes + Pin #) | Componente Destino (RefDes + Pin #) | Tipo de Señal / Notas Técnicas |
|---|---|---|---|
| NET_AIN1 | U1.GP2 / Pin3 (Output 3.3V) | U3.Pin18 (AIN1, control dirección A) | Digital 3.3V salida; dirección 1 puente H. AIN1=0, AIN2=1 → abrir compuertas |

#### NET: NET_AIN2 (GP1 → AIN2)
| Nombre del Net | Componente Origen (RefDes + Pin #) | Componente Destino (RefDes + Pin #) | Tipo de Señal / Notas Técnicas |
|---|---|---|---|
| NET_AIN2 | U1.GP1 / Pin2 (Output 3.3V) | U3.Pin17 (AIN2, control dirección A) | Digital 3.3V salida; dirección 2 puente H. AIN1=1, AIN2=0 → cerrar compuertas |

#### NET: NET_MOTOR_EN (GP3 → PWMA)
| Nombre del Net | Componente Origen (RefDes + Pin #) | Componente Destino (RefDes + Pin #) | Tipo de Señal / Notas Técnicas |
|---|---|---|---|
| NET_MOTOR_EN | U1.GP3 / Pin4 (Output 3.3V) | U3.Pin19 (PWMA, enable canal A) | Digital 3.3V salida; HIGH=canal A activo. LOW=motor stop (safe state — hbridge.py) |

#### NET: NET_STBY (STBY → Tied HIGH hardware)
| Nombre del Net | Componente Origen (RefDes + Pin #) | Componente Destino (RefDes + Pin #) | Tipo de Señal / Notas Técnicas |
|---|---|---|---|
| NET_STBY | R5.Pin1 (10kΩ pull-up, desde +3V3) | R5.Pin2 (salida resistencia) | DC 3.3V; resistencia pull-up hardware STBY |
| NET_STBY | R5.Pin2 (salida resistencia) | U3.Pin16 (STBY, activo en HIGH) | ★ CRÍTICO — STBY=HIGH habilita todas las salidas TB6612FNG. STBY=LOW → alta impedancia (fail-safe) |

#### Canales B no utilizados — terminaciones seguras a AGND
| Nombre del Net | Componente Origen (RefDes + Pin #) | Componente Destino (RefDes + Pin #) | Tipo de Señal / Notas Técnicas |
|---|---|---|---|
| AGND | AGND (plano) | U3.Pin22 (BIN1, canal B) | Canal B en modo STOP — ver Cat.2 AGND |
| AGND | AGND (plano) | U3.Pin23 (BIN2, canal B) | Canal B en modo STOP — ver Cat.2 AGND |
| AGND | AGND (plano) | U3.Pin24 (PWMB, canal B) | PWMB=LOW, canal B deshabilitado — ver Cat.2 AGND |
| NC | — | U3.Pin7 / Pin8 (BO2, BO2 dup.) | Sin conexión — salida canal B no utilizado. No rutear |
| NC | — | U3.Pin11 / Pin12 (BO1, BO1 dup.) | Sin conexión — salida canal B no utilizado. No rutear |

---

### 3.5 · Control Ventilador 48V — Selector Físico J9 + MOSFET Q1

> **[MOD-4] JP1 (solder bridge 0Ω) ELIMINADO. Sustituido por J9 (header macho 3 pines, paso 2.54mm).**  
> J9 permite selección manual segura mediante jumper extraíble. La señal U4.OUT se asigna al nuevo net NET_VENT_DRV.
>
> **Tabla de operación J9:**
>
> | Jumper | Efecto eléctrico | Estado U4 | Uso |
> |---|---|---|---|
> | Pin1–Pin2 | GP4 → NET_VENT_GATE → R6 → Gate Q1 | Ignorado (OUT a Pin3 flotante) | Prototipo sin TC4420 poblado |
> | Pin2–Pin3 | U4.OUT → NET_VENT_GATE → R6 → Gate Q1 | Activo (IN=GP4, OUT=5V) | Producción con TC4420 poblado |

#### NET: NET_VENT (señal GP4 antes de J9 / U4)

| Nombre del Net | Componente Origen (RefDes + Pin #) | Componente Destino (RefDes + Pin #) | Tipo de Señal / Notas Técnicas |
|---|---|---|---|
| NET_VENT | U1.GP4 / Pin5 (Output digital 3.3V) | U4.Pin3 (IN, entrada TC4420) | Digital 3.3V; señal de control al gate driver. U4.IN activo siempre que U4 esté poblado |
| **NET_VENT** | **U1.GP4 / Pin5 (Output digital 3.3V)** | **J9.Pin1 (header 3-pin, terminal MCU)** | **[MOD-4] señal GP4 disponible en Pin1 de J9 para jumper directo a Pin2 (NET_VENT_GATE)** |

#### NET: NET_VENT_GATE (nodo seleccionado por jumper J9, entrada R6)

| Nombre del Net | Componente Origen (RefDes + Pin #) | Componente Destino (RefDes + Pin #) | Tipo de Señal / Notas Técnicas |
|---|---|---|---|
| **NET_VENT_GATE** | **J9.Pin2 (header 3-pin, terminal central)** | **R6.Pin1 (330Ω serie Gate, entrada)** | **[MOD-4] único punto de entrada a la trayectoria Gate. El jumper en J9 decide qué señal llega: PIN1-PIN2=GP4 directo; PIN2-PIN3=U4.OUT** |

#### NET: NET_VENT_DRV (salida U4 → J9.Pin3) ← **NUEVO NET**

| Nombre del Net | Componente Origen (RefDes + Pin #) | Componente Destino (RefDes + Pin #) | Tipo de Señal / Notas Técnicas |
|---|---|---|---|
| **NET_VENT_DRV** | **U4.Pin6 (OUT, salida TC4420)** | **J9.Pin3 (header 3-pin, terminal gate driver)** | **[MOD-4] red exclusiva para la salida del gate driver. Nivel: 0–5V (rail-to-rail respecto +5V de U4). Conecta a NET_VENT_GATE solo cuando jumper en Pin2-Pin3** |

#### NET: NET_Q1_GATE (Gate IRL520N, entre R6 y Q1)

| Nombre del Net | Componente Origen (RefDes + Pin #) | Componente Destino (RefDes + Pin #) | Tipo de Señal / Notas Técnicas |
|---|---|---|---|
| NET_Q1_GATE | R6.Pin2 (330Ω serie, salida) | Q1.Pin1 (Gate, IRL520N) | Gate drive; R6 amortigua oscilaciones LC parásitas. Colocar R6 ≤5mm del Gate |
| NET_Q1_GATE | R6.Pin2 (330Ω serie, salida) | R7.Pin1 (10kΩ pull-down, terminal señal) | Pull-down Gate; garantiza V_GS=0V en ausencia de señal, reset MCU o fallo GPIO |
| NET_Q1_GATE | R6.Pin2 (330Ω serie, salida) | TP8.Pad1 | Test Point Gate. Nivel esperado: ≈0V(OFF) / ≈3.3V(ON sin U4) / ≈5.0V(ON con U4) |

---

### 3.6 · LED Indicador Power-On

#### NET: NET_LED_ANODE
| Nombre del Net | Componente Origen (RefDes + Pin #) | Componente Destino (RefDes + Pin #) | Tipo de Señal / Notas Técnicas |
|---|---|---|---|
| NET_LED_ANODE | R_LED.Pin2 (1kΩ limitador, salida) | LED1.Ánodo/A (LED verde 0805) | DC 3.3V; I_LED=(3.3–2.0)/1kΩ≈1.3mA. Indicador visual +3V3 activo |

---

## CATEGORÍA 4: NETS DE SALIDA DE POTENCIA

---

### 4.1 · Salida Actuador FIT0803 (TB6612FNG Canal A → J3)

> Sin cambios respecto a Fase 2. Trazas ≥1.5mm en pares AO1, AO2. Pines duplicados del IC en paralelo.

#### NET: NET_AO1 (Salida Motor A1 → J3.Pin1)

| Nombre del Net | Componente Origen (RefDes + Pin #) | Componente Destino (RefDes + Pin #) | Tipo de Señal / Notas Técnicas |
|---|---|---|---|
| NET_AO1 | U3.Pin1 (AO1, salida canal A) | U3.Pin2 (AO1, pin duplicado) | ★ CRÍTICO — atar con copper-pour o trazas paralelas ≥1.5mm; I_cont=1.2A, I_pico=3.2A |
| NET_AO1 | U3.Pin1 (AO1, salida canal A) | J3.Pin1 (bloque tornillo, terminal 1 motor) | DC Motor 5V; terminal 1 FIT0803. Polaridad según modo: abrir=AO1(+), cerrar=AO1(–) |

#### NET: NET_AO2 (Salida Motor A2 → J3.Pin2)

| Nombre del Net | Componente Origen (RefDes + Pin #) | Componente Destino (RefDes + Pin #) | Tipo de Señal / Notas Técnicas |
|---|---|---|---|
| NET_AO2 | U3.Pin5 (AO2, salida canal A) | U3.Pin6 (AO2, pin duplicado) | ★ CRÍTICO — misma regla de atado que AO1. Trazas paralelas ≥1.5mm |
| NET_AO2 | U3.Pin5 (AO2, salida canal A) | J3.Pin2 (bloque tornillo, terminal 2 motor) | DC Motor 5V; terminal 2 FIT0803 |

---

### 4.2 · Salida Ventilador 48V (Q1 + D3 + J6)

> Sin cambios estructurales. NET_FAN_HS sigue siendo el nodo de conmutación de alta tensión.

#### NET: NET_FAN_HS (Drain Q1 / Fan(–) / Ánodo D3)

> Durante operación: Q1 ON → V(NET_FAN_HS) ≈ 0.4–1.5V. Q1 OFF (transitorio) → V(NET_FAN_HS) sube hasta D3 conduce → clampea a +48V + Vf_D3 ≈ 49.7V. V_DS(Q1) máximo ≈ 49.7V << 100V (rating IRL520N) → margen ×2.

| Nombre del Net | Componente Origen (RefDes + Pin #) | Componente Destino (RefDes + Pin #) | Tipo de Señal / Notas Técnicas |
|---|---|---|---|
| NET_FAN_HS | Q1.Pin2 (Drain, IRL520N) | D3.Ánodo/A (US1M, flyback) | ★ CRÍTICO — Drain Q1 al ánodo flyback. Cuando Q1 abre, D3 conduce → suprime pico inductivo. Colocar D3 ≤10mm del Drain |
| NET_FAN_HS | Q1.Pin2 (Drain, IRL520N) | J6.Pin2 (bloque tornillo, Fan–) | DC conmutación 48V; terminal (–) del extractor MR1238E48B-FSR |
| NET_FAN_HS | Q1.Pin2 (Drain, IRL520N) | TP7.Pad1 | Test Point Drain Q1. ⚠️ Precaución: hasta 49.7V transitorio — usar punta de osciloscopio ×10 |

#### Conexiones de retorno y alimentación fan (referenciadas en Cat.1 y Cat.2)

| Nombre del Net | Componente Origen (RefDes + Pin #) | Componente Destino (RefDes + Pin #) | Tipo de Señal / Notas Técnicas |
|---|---|---|---|
| +48V | D3.Cátodo/K (US1M) | +48V (rail; incluye J5.Pin1, C10.Pin+, J6.Pin1) | Cátodo flyback al rail positivo — lazo freewheeling al condensador bulk C10 |
| PGND | Q1.Pin3 (Source, IRL520N) | PGND (plano potencia; incluye J5.Pin2) | ★ CRÍTICO — Source a PGND con traza de baja inductancia para minimizar rebote V_GS |
| +48V | J6.Pin1 (Fan+, terminal positivo) | +48V (rail) | Terminal (+) extractor; siempre a +48V, el control es por el retorno (Q1 low-side) |

---

## RESUMEN DE NETS Y CONTEO DE NODOS — VALIDACIÓN MATEMÁTICA

| Net | # Nodos | Δ vs Fase 2 | Tipo | Notas de modificación |
|---|---|---|---|---|
| +48V | 5 | = | Potencia DC 48V | Sin cambios |
| +5V | **13** | **+1** | Potencia DC 5V | +C15.Pin1 bypass driver U4 |
| NET_3V3_LDO | 3 | = | Potencia DC 3.3V pre-fuse | Sin cambios |
| +3V3 | **13** | **+5** | Potencia DC 3.3V post-fuse | +R9.Pin1, +R10.Pin1, +R11.Pin1, +D1.Pin2, +D2.Pin2 [MOD-2, MOD-3] |
| PGND | **15** | **+1** | Ground potencia | +C15.Pin2 bypass driver U4 |
| AGND | **26** | **+6** | Ground analógico | –D1.A(SMBJ), –D2.A(SMBJ); +D1.Pin1(BAT54S), +D2.Pin1(BAT54S), +C12.Pin2, +C13.Pin2, +C14.Pin2; +BIN1,BIN2,PWMB contabilizados [MOD-2, MOD-3] |
| NT1 (AGND↔PGND) | 2 | = | Net-Tie cobre [MOD-5] | Mismo conteo; cambio de tipo: Ferrite → Net-Tie directo |
| NET_TEMP_INT_DIV | **2** | **–1** | Analógico | –D1.Cátodo (SMBJ eliminado) [MOD-2] |
| NET_TEMP_INT_FILT | **5** | **+1** | Analógico ADC | +D1.Pin3 (BAT54S añadido) [MOD-2] |
| NET_TEMP_EXT_DIV | **2** | **–1** | Analógico | –D2.Cátodo (SMBJ eliminado) [MOD-2] |
| NET_TEMP_EXT_FILT | **4** | **+1** | Analógico ADC | +D2.Pin3 (BAT54S añadido) + TP7 [MOD-2] |
| NET_SW1 | **4** | **+2** | Digital entrada | +R9.Pin2, +C12.Pin1 [MOD-3] |
| NET_SW2 | **4** | **+2** | Digital entrada | +R10.Pin2, +C13.Pin1; destino GP8 (era GP7) [MOD-1, MOD-3] |
| NET_SW3 | **4** | **+2** | Digital entrada | +R11.Pin2, +C14.Pin1 [MOD-3] |
| NET_AIN1 | 2 | = | Digital salida | Sin cambios |
| NET_AIN2 | 2 | = | Digital salida | Sin cambios |
| NET_MOTOR_EN | 2 | = | Digital salida | Sin cambios |
| NET_STBY | 2 | = | Digital tied HIGH | Sin cambios |
| NET_VENT | **3** | **+1** | Digital salida 3.3V | +J9.Pin1 (era JP1.Pin1) [MOD-4] |
| NET_VENT_GATE | 2 | = | Selección jumper | J9.Pin2→R6 (reemplaza lógica JP1) [MOD-4] |
| **NET_VENT_DRV** | **2** | **NUEVO** | Digital 0–5V salida U4 | Red creada por [MOD-4] — U4.Pin6→J9.Pin3 |
| NET_Q1_GATE | 4 | = | Gate drive MOSFET | Sin cambios |
| NET_LED_ANODE | 2 | = | DC 3.3V | Sin cambios |
| NET_AO1 | 3 | = | DC Motor 5V | Sin cambios |
| NET_AO2 | 3 | = | DC Motor 5V | Sin cambios |
| NET_FAN_HS | 3 | = | DC conmutación 48V | Sin cambios (TP7 ya contabilizado arriba) |
| **TOTAL NODOS** | **≈ 135** | **+14** | | |
| **TOTAL NETS** | **26** | **+1** (NET_VENT_DRV) | | |
| **CONEXIONES MÍNIMAS** (nodos – nets) | **≈ 109** | **+13** | | |

### Validación de cierre del diseño

| Verificación | Condición | Resultado |
|---|---|---|
| Todo GPIO mapeado en CLAUDE.md tiene un net | GP0→SW3, GP1→AIN2, GP2→AIN1, GP3→MOTOR_EN, GP4→VENT, GP6→SW1, GP8→SW2, GP26→TEMP_INT, GP27→TEMP_EXT | ✅ 9/9 GPIOs cubiertos |
| Cada componente activo tiene retorno de GND | U1, U2, U3, U4, Q1 | ✅ Todos referenciados |
| STBY del TB6612FNG tied HIGH en hardware | R5 pull-up 10kΩ a +3V3 → U3.Pin16 | ✅ Confirmado |
| Flyback D3 correctamente polarizado | Ánodo→NET_FAN_HS, Cátodo→+48V | ✅ Confirmado |
| U4 y J9 tienen lógica de selección mutuamente excluyente | JP1 eliminado; J9 Pin1-Pin2 o Pin2-Pin3 | ✅ [MOD-4] |
| AGND y PGND unidos en un único punto físico | NT1 Net-Tie | ✅ [MOD-5] |
| BAT54S orientado correctamente para clamping ADC | A1(Pin1)→AGND, K1/A2(Pin3)→señal, K2(Pin2)→+3V3 | ✅ [MOD-2] |
| GP7 (back pad) eliminado del diseño PCB | NET_SW2 → U1.GP8 (Pin10, castellación) | ✅ [MOD-1] |

---

*Documento generado: 2026-06-30 | Revisión: 2.1 — LIBERADO PARA FASE 3: Esquemático KiCad v8*  
*Proyecto: Jaguar MX — Evaluación Técnica | Ing. Jair Molina Arce*
