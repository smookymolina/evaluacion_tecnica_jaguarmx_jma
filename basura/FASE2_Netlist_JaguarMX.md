# FASE 2 — NETLIST COMPLETO NET POR NET · KiCad v8
### Tarjeta de Control de Extracción · Jaguar de México
### Candidato: Ing. Jair Molina Arce | MCU: Seeed Studio XIAO RP2350

---

## CONVENCIONES DE ESTE DOCUMENTO

| Convención | Descripción |
|---|---|
| **Net en MAYÚSCULAS** | Identificador eléctrico único para KiCad (Net Inspector) |
| **RefDes.PinX** | Componente + número de pin físico del encapsulado |
| **RefDes.NombrePin** | Componente + nombre funcional del pin (en símbolos KiCad) |
| **(DNP)** | Do Not Populate — componente que NO se suelda en esa configuración |
| **(★ CRÍTICO)** | Conexión con implicación directa de seguridad o funcionamiento |
| **NET_xxx_DIV** | Nodo intermedio divisor de tensión (antes del filtro RC) |
| **NET_xxx_FILT** | Nodo intermedio post-filtro RC (directamente en el GPIO) |

### Nota sobre XIAO RP2350 — pines GP0 y GP7
- **GP0 (D0)**: Pad físico 1, borde izquierdo, pin superior. Disponible en castellación estándar.  
- **GP7 (D7)**: En la revisión v1.0 del XIAO RP2350, GP7 está expuesto en el **pad trasero B1** (back pad). Verificar contra la hoja de datos de Seeed Studio antes de rutear. Si el símbolo KiCad de la librería Seeed no lo incluye, crear pin personalizado o usar pad alternativo GP8 con ajuste en `dip_switch.py`.

### Nota sobre U4 (TC4420) y JP1 (bypass 0Ω)
> **Regla de poblado exclusivo:** U4 y JP1 son **mutuamente excluyentes**.  
> - Si U4 **SE PUEBLA**: JP1 = DNP. La señal GP4 ingresa por U4.IN y sale por U4.OUT hacia NET_VENT_GATE.  
> - Si U4 **NO SE PUEBLA**: JP1 = 0Ω (populated). La señal GP4 pasa directamente a NET_VENT_GATE vía JP1.  
> Los dos pads de JP1 deben estar en el footprint inmediatamente adyacente al encapsulado de U4 para minimizar inductancia parásita.

---

## CATEGORÍA 1: NETS DE ALIMENTACIÓN Y POTENCIA

---

### NET: +48V
**Descripción:** Rail de 48V DC externo. Alimenta exclusivamente el ventilador industrial. Trazas ≥ 2.0mm. Clase de red: Power.

| Net | Componente Origen (RefDes + Pin) | Componente Destino (RefDes + Pin) | Tipo de Señal / Notas Técnicas |
|---|---|---|---|
| +48V | J5.Pin1 (+, entrada 48V) | C10.Pin+ (100µF/63V bulk) | DC Potencia; terminal positivo cap bulk. C10 desacopla ripple de la fuente externa |
| +48V | J5.Pin1 (+, entrada 48V) | C11.Pin1 (100nF/63V HF) | DC Potencia; bypass HF en paralelo con C10. Colocar ≤5mm del Drain de Q1 |
| +48V | J5.Pin1 (+, entrada 48V) | J6.Pin1 (Fan+, salida extractor) | DC Potencia; terminal (+) del MR1238E48B-FSR. Traza ≥2mm, clase Power |
| +48V | J5.Pin1 (+, entrada 48V) | D3.Cátodo / K (US1M flyback) | DC Potencia; cátodo del diodo flyback apuntando al rail positivo. (★ CRÍTICO) |
| +48V | J5.Pin1 (+, entrada 48V) | TP3.Pad1 | Test Point; permite medir rail 48V con multímetro/osciloscopio en campo |

---

### NET: +5V
**Descripción:** Rail de 5V DC. Alimenta la entrada del LDO (U2), la tensión de motor del puente H (U3.VM) y la alimentación del gate driver opcional (U4.VCC). Trazas ≥ 1.0mm.

| Net | Componente Origen (RefDes + Pin) | Componente Destino (RefDes + Pin) | Tipo de Señal / Notas Técnicas |
|---|---|---|---|
| +5V | J7.Pin1 (+, entrada 5V) | U2.Pin4 (VIN, LDO input) | DC Potencia; entrada al regulador AP2112K-3.3 |
| +5V | J7.Pin1 (+, entrada 5V) | U2.Pin3 (EN, chip enable) | DC Potencia; EN tied to VIN → LDO siempre habilitado. Sin componente externo adicional |
| +5V | J7.Pin1 (+, entrada 5V) | C1.Pin1 (10µF/10V X7R) | DC Potencia; cap de desacoplo entrada LDO. X7R obligatorio (estabilidad AP2112K) |
| +5V | J7.Pin1 (+, entrada 5V) | C3.Pin1 (100nF/10V X5R) | DC Potencia; cap bypass HF entrada LDO. En paralelo con C1, ≤2mm de U2.VIN |
| +5V | J7.Pin1 (+, entrada 5V) | U3.Pin13 (VM, motor supply) | DC Potencia; alimentación canal actuador TB6612FNG. Traza ≥1.0mm |
| +5V | J7.Pin1 (+, entrada 5V) | U3.Pin14 (VM, duplicado) | DC Potencia; pin VM duplicado del TB6612FNG. Atar físicamente con Pin13 en PCB (paralelo) |
| +5V | J7.Pin1 (+, entrada 5V) | C7.Pin+ (47µF/10V bulk motor) | DC Potencia; cap bulk desacoplo VM. Absorbe picos de corriente del FIT0803 en arranque (~800mA pico) |
| +5V | J7.Pin1 (+, entrada 5V) | C8.Pin1 (100nF/10V X7R HF) | DC Potencia; bypass HF VM motor. Colocar ≤2mm de U3 pines VM |
| +5V | J7.Pin1 (+, entrada 5V) | U4.Pin5 (VCC, TC4420) | DC Potencia; alimentación gate driver. (DNP si U4 no se puebla) |
| +5V | J7.Pin1 (+, entrada 5V) | U4.Pin7 (VCC, duplicado) | DC Potencia; pin VCC duplicado TC4420 para capacidad de corriente. (DNP) |
| +5V | J7.Pin1 (+, entrada 5V) | U4.Pin8 (VCC, duplicado) | DC Potencia; pin VCC duplicado TC4420. (DNP) |
| +5V | J7.Pin1 (+, entrada 5V) | TP2.Pad1 | Test Point; validación rail 5V |

---

### NET: NET_3V3_LDO
**Descripción:** Nodo de salida del AP2112K **antes** del fusible PPTC F1. Los capacitores de salida del LDO (C2, C4) se conectan aquí para garantizar la estabilidad del lazo de control interno del regulador, independientemente del estado del fusible.

| Net | Componente Origen (RefDes + Pin) | Componente Destino (RefDes + Pin) | Tipo de Señal / Notas Técnicas |
|---|---|---|---|
| NET_3V3_LDO | U2.Pin2 (VOUT, salida LDO) | F1.Pin1 (PPTC 500mA, entrada) | DC 3.3V; nodo pre-fuse. Corriente máxima continua: 600mA (límite AP2112K) |
| NET_3V3_LDO | U2.Pin2 (VOUT, salida LDO) | C2.Pin1 (10µF/10V X7R, salida) | DC 3.3V; cap estabilidad salida LDO. (★ CRÍTICO) DEBE estar antes del fusible para no introducir impedancia en el lazo del LDO |
| NET_3V3_LDO | U2.Pin2 (VOUT, salida LDO) | C4.Pin1 (100nF/10V X5R HF) | DC 3.3V; bypass HF salida LDO. En paralelo con C2, ≤2mm de U2.VOUT |

---

### NET: +3V3
**Descripción:** Rail de 3.3V regulado y protegido. Nodo **después** del fusible PPTC F1. Alimenta el MCU, la lógica del puente H, los divisores NTC y el DIP switch. Todos los componentes lógicos y analógicos se alimentan desde aquí.

| Net | Componente Origen (RefDes + Pin) | Componente Destino (RefDes + Pin) | Tipo de Señal / Notas Técnicas |
|---|---|---|---|
| +3V3 | F1.Pin2 (PPTC, salida) | U1.3V3 / Pin12 (XIAO 3V3) | DC 3.3V; alimentación directa al RP2350 bypass del LDO interno del XIAO. U1.5V (VIN) debe quedar SIN CONEXIÓN (NC) para evitar conflicto entre reguladores |
| +3V3 | F1.Pin2 (PPTC, salida) | U3.Pin15 (VCC, lógica TB6612) | DC 3.3V; alimentación lógica del TB6612FNG. V_IH mín = 2.0V → 3.3V es válido |
| +3V3 | F1.Pin2 (PPTC, salida) | C9.Pin1 (100nF VCC lógica U3) | DC 3.3V; desacoplo local VCC lógica TB6612FNG. Colocar ≤2mm de U3.VCC (Pin15) |
| +3V3 | F1.Pin2 (PPTC, salida) | R1.Pin1 (10kΩ ±1%, divisor NTC1) | DC 3.3V; referencia superior divisor de voltaje sensor TEMP_INT |
| +3V3 | F1.Pin2 (PPTC, salida) | R2.Pin1 (10kΩ ±1%, divisor NTC2) | DC 3.3V; referencia superior divisor de voltaje sensor TEMP_EXT |
| +3V3 | F1.Pin2 (PPTC, salida) | R5.Pin1 (10kΩ pull-up STBY) | DC 3.3V; pull-up hardware al pin STBY del TB6612FNG. (★ CRÍTICO) |
| +3V3 | F1.Pin2 (PPTC, salida) | R_LED.Pin1 (1kΩ limitador LED) | DC 3.3V; alimentación indicador LED de power-on |
| +3V3 | F1.Pin2 (PPTC, salida) | TP1.Pad1 | Test Point; validación rail 3.3V post-fuse |

---

## CATEGORÍA 2: NETS DE TIERRA (PGND, AGND) Y UNIÓN ESTRELLA

---

### NET: PGND (Ground de Potencia)
**Descripción:** Plano de retorno para corrientes de alta magnitud. Incluye retornos del ventilador 48V, el MOSFET Q1, el puente H TB6612FNG (canal motor) y los capacitores bulk. En PCB: plano continuo en capa trasera, zona de cobre dedicada, vía stitching perimetral.

| Net | Componente Origen (RefDes + Pin) | Componente Destino (RefDes + Pin) | Tipo de Señal / Notas Técnicas |
|---|---|---|---|
| PGND | J5.Pin2 (–, retorno 48V) | C10.Pin– (100µF/63V bulk, negativo) | Retorno 48V; corriente continua del ventilador |
| PGND | J5.Pin2 (–, retorno 48V) | C11.Pin2 (100nF/63V HF, negativo) | Retorno 48V; cap HF a tierra de potencia |
| PGND | J5.Pin2 (–, retorno 48V) | Q1.Pin3 (Source, IRL520N) | Retorno conmutación MOSFET. (★ CRÍTICO) Source directamente a PGND, traza corta y ancha ≥2mm |
| PGND | J7.Pin2 (–, retorno 5V) | U3.Pin3 (PGND, motor ground) | Retorno 5V motor; corriente actuador FIT0803 |
| PGND | J7.Pin2 (–, retorno 5V) | U3.Pin4 (PGND, duplicado) | Retorno 5V motor; pin duplicado TB6612FNG. Atar con Pin3 en PCB (paralelo) |
| PGND | J7.Pin2 (–, retorno 5V) | U3.Pin9 (PGND, duplicado) | Retorno 5V motor; pin duplicado TB6612FNG |
| PGND | J7.Pin2 (–, retorno 5V) | U3.Pin10 (PGND, duplicado) | Retorno 5V motor; pin duplicado TB6612FNG |
| PGND | J7.Pin2 (–, retorno 5V) | C7.Pin– (47µF bulk motor, negativo) | Retorno 5V; GND cap bulk VM actuador |
| PGND | J7.Pin2 (–, retorno 5V) | C8.Pin2 (100nF HF motor, negativo) | Retorno 5V; GND cap HF VM motor |
| PGND | PGND (plano) | U4.Pin1 (GND, TC4420) | Retorno gate driver. (DNP si U4 no se puebla) |
| PGND | PGND (plano) | U4.Pin2 (GND, duplicado TC4420) | Retorno gate driver, pin duplicado. (DNP) |
| PGND | PGND (plano) | U4.Pin4 (GND, duplicado TC4420) | Retorno gate driver, pin duplicado. (DNP) |
| PGND | PGND (plano) | R7.Pin2 (10kΩ pull-down Gate) | Retorno pull-down; referencia de Gate Q1 a tierra de potencia |
| PGND | PGND (plano) | TP4.Pad1 | Test Point PGND |

---

### NET: AGND (Ground Analógico y Lógico)
**Descripción:** Plano de retorno para corrientes de baja magnitud: MCU, LDO, sensores NTC, DIP switch, LED. Separado físicamente del PGND en el PCB. Se une a PGND en un único punto vía NT1 (estrella).

| Net | Componente Origen (RefDes + Pin) | Componente Destino (RefDes + Pin) | Tipo de Señal / Notas Técnicas |
|---|---|---|---|
| AGND | U1.GND / Pin13 (XIAO RP2350) | AGND (plano analógico) | Retorno MCU; referencia del ADC interno del RP2350 |
| AGND | U2.Pin1 (GND, AP2112K) | AGND (plano analógico) | Retorno LDO; pin GND es común para entrada y salida del regulador |
| AGND | C1.Pin2 (10µF entrada LDO, negativo) | AGND (plano analógico) | Retorno cap desacoplo entrada LDO; en área analógica |
| AGND | C2.Pin2 (10µF salida LDO, negativo) | AGND (plano analógico) | Retorno cap estabilidad salida LDO |
| AGND | C3.Pin2 (100nF HF entrada, negativo) | AGND (plano analógico) | Retorno cap bypass HF entrada LDO |
| AGND | C4.Pin2 (100nF HF salida, negativo) | AGND (plano analógico) | Retorno cap bypass HF salida LDO |
| AGND | U3.Pin20 (GND lógico TB6612FNG) | AGND (plano analógico) | Retorno GND lógico del puente H; separado de PGND (pines motor) dentro del IC |
| AGND | U3.Pin21 (GND lógico, duplicado) | AGND (plano analógico) | Retorno GND lógico TB6612FNG, pin duplicado |
| AGND | C9.Pin2 (100nF VCC lógica U3, negativo) | AGND (plano analógico) | Retorno cap desacoplo VCC lógica TB6612FNG |
| AGND | C5.Pin2 (100nF filtro RC GP26, negativo) | AGND (plano analógico) | Retorno cap filtro RC; referencia ADC0 TEMP_INT. (★ CRÍTICO) Traza corta a AGND, no cruzar zonas digitales |
| AGND | C6.Pin2 (100nF filtro RC GP27, negativo) | AGND (plano analógico) | Retorno cap filtro RC; referencia ADC1 TEMP_EXT. Ídem a C5 |
| AGND | D1.Ánodo / A (SMBJ3.3A TEMP_INT) | AGND (plano analógico) | TVS referenciado a AGND. El ánodo va a AGND para clampar positivos en cátodo (señal) |
| AGND | D2.Ánodo / A (SMBJ3.3A TEMP_EXT) | AGND (plano analógico) | Ídem D1 para canal TEMP_EXT |
| AGND | J1.Pin2 (conector NTC1, terminal GND) | AGND (plano analógico) | Retorno NTC interna; polo frío del divisor de voltaje NTC1 |
| AGND | J2.Pin2 (conector NTC2, terminal GND) | AGND (plano analógico) | Retorno NTC externa; polo frío del divisor de voltaje NTC2 |
| AGND | SW1.Pin2 (DIP pos.1, común SW1-A) | AGND (plano analógico) | Común del DIP switch bit 0. Pull-up interna RP2350 activa por firmware |
| AGND | SW1.Pin4 (DIP pos.2, común SW2-A) | AGND (plano analógico) | Común del DIP switch bit 1 |
| AGND | SW1.Pin6 (DIP pos.3, común SW3-A) | AGND (plano analógico) | Común del DIP switch bit 2 |
| AGND | LED1.Cátodo / K (LED indicador power) | AGND (plano analógico) | Retorno LED indicador 3.3V |
| AGND | AGND (plano) | TP5.Pad1 | Test Point AGND |

---

### NET: Unión Única AGND ↔ PGND (Estrella) vía NT1
**Descripción:** El Ferrite Bead NT1 (BLM21PG600SN1L, 600Ω@100MHz) conecta los dos planos de tierra en **un único punto físico**. Esta conexión debe realizarse cerca del conector J7 (retorno 5V de motor), que es el punto de mayor corriente compartida. En KiCad, NT1 se coloca como componente 0805 en la unión de las dos zonas de cobre.

| Net | Componente Origen (RefDes + Pin) | Componente Destino (RefDes + Pin) | Tipo de Señal / Notas Técnicas |
|---|---|---|---|
| AGND → NT1 | NT1.Pin1 (lado analógico) | AGND (plano analógico/lógico) | Polo AGND del ferrite bead; baja impedancia DC, alta impedancia HF (600Ω@100MHz) |
| PGND → NT1 | NT1.Pin2 (lado potencia) | PGND (plano de potencia) | Polo PGND del ferrite bead; unión estrella. (★ CRÍTICO) Este debe ser el ÚNICO punto de contacto físico entre ambos planos |

---

## CATEGORÍA 3: NETS DE SEÑAL Y CONTROL DEL MCU (XIAO RP2350)

---

### 3.1 · Ruta Completa TEMP_INT — GP26 / ADC0

**Topología de la ruta:** `+3V3 → R1 → [NET_TEMP_INT_DIV] ← NTC1(vía J1) ← AGND`  
`[NET_TEMP_INT_DIV] → D1(TVS clamping) → R3(filtro) → [NET_TEMP_INT_FILT] → C5(shunt AGND) → U1.GP26`

**Valores clave:**  
- Divisor en equilibrio a 25°C: V_div = 3.3 × 10k/(10k+10k) = **1.65V**  
- Filtro RC: τ = R3 × C5 = 1kΩ × 100nF = **100µs** → fc ≈ **1.59kHz**  
- TVS SMBJ3.3A: Vrwm=3.3V, Vbr=3.67–4.03V@1mA; clampea positivos por encima de ~4V

#### NET: NET_TEMP_INT_DIV
**Descripción:** Nodo intermedio del divisor resistivo NTC1. Aquí convergen: la resistencia de referencia R1 (desde +3V3), el terminal activo del NTC1 (vía J1), el cátodo del TVS D1, y la entrada de la resistencia de filtro R3.

| Net | Componente Origen (RefDes + Pin) | Componente Destino (RefDes + Pin) | Tipo de Señal / Notas Técnicas |
|---|---|---|---|
| NET_TEMP_INT_DIV | R1.Pin2 (salida divisor hacia nodo) | D1.Cátodo / K (SMBJ3.3A) | Analógico DC; nodo del divisor conectado al cátodo del TVS. D1 clampea transitorios externos del cable NTC |
| NET_TEMP_INT_DIV | R1.Pin2 (salida divisor hacia nodo) | J1.Pin1 (conector NTC1, terminal caliente) | Analógico DC; terminal superior del NTC1 en el circuito divisor (R_ref en top, NTC a GND) |
| NET_TEMP_INT_DIV | R1.Pin2 (salida divisor hacia nodo) | R3.Pin1 (1kΩ filtro, entrada) | Analógico; entrada al filtro RC pasa-bajos antes del GPIO |

#### NET: NET_TEMP_INT_FILT
**Descripción:** Nodo post-filtro RC del canal TEMP_INT. La tensión en este nodo es la que el ADC0 del RP2350 digitaliza. C5 forma el polo del filtro junto con R3.

| Net | Componente Origen (RefDes + Pin) | Componente Destino (RefDes + Pin) | Tipo de Señal / Notas Técnicas |
|---|---|---|---|
| NET_TEMP_INT_FILT | R3.Pin2 (1kΩ filtro, salida) | C5.Pin1 (100nF, shunt a AGND) | Analógico; nodo del polo de filtro. fc = 1/(2π·R3·C5) ≈ 1.59kHz |
| NET_TEMP_INT_FILT | R3.Pin2 (1kΩ filtro, salida) | U1.GP26 / Pin8 (ADC0 XIAO) | Analógico ADC 12-bit; señal TEMP_INT filtrada. V rango: ~0.3V (130°C) a ~2.8V (10°C) |
| NET_TEMP_INT_FILT | R3.Pin2 (1kΩ filtro, salida) | TP6.Pad1 | Test Point analógico; medir con osciloscopio para verificar ausencia de ripple / ruido HF |

---

### 3.2 · Ruta Completa TEMP_EXT — GP27 / ADC1

**Topología idéntica a TEMP_INT.** Mismos valores de componentes, canal independiente.

#### NET: NET_TEMP_EXT_DIV
**Descripción:** Nodo divisor del canal temperatura externa. R2 + NTC2 + D2 + R4.

| Net | Componente Origen (RefDes + Pin) | Componente Destino (RefDes + Pin) | Tipo de Señal / Notas Técnicas |
|---|---|---|---|
| NET_TEMP_EXT_DIV | R2.Pin2 (salida divisor hacia nodo) | D2.Cátodo / K (SMBJ3.3A) | Analógico DC; TVS D2 clampea transitorios del cable NTC2 externo (mayor exposición a ESD) |
| NET_TEMP_EXT_DIV | R2.Pin2 (salida divisor hacia nodo) | J2.Pin1 (conector NTC2, terminal caliente) | Analógico DC; terminal superior del NTC2 en el divisor. J2 está en el exterior del gabinete |
| NET_TEMP_EXT_DIV | R2.Pin2 (salida divisor hacia nodo) | R4.Pin1 (1kΩ filtro, entrada) | Analógico; entrada al filtro RC pasa-bajos GP27 |

#### NET: NET_TEMP_EXT_FILT
**Descripción:** Nodo post-filtro RC del canal TEMP_EXT. Entra directamente al ADC1 del RP2350.

| Net | Componente Origen (RefDes + Pin) | Componente Destino (RefDes + Pin) | Tipo de Señal / Notas Técnicas |
|---|---|---|---|
| NET_TEMP_EXT_FILT | R4.Pin2 (1kΩ filtro, salida) | C6.Pin1 (100nF, shunt a AGND) | Analógico; polo del filtro RC TEMP_EXT. τ = 100µs, fc = 1.59kHz |
| NET_TEMP_EXT_FILT | R4.Pin2 (1kΩ filtro, salida) | U1.GP27 / Pin9 (ADC1 XIAO) | Analógico ADC 12-bit; señal TEMP_EXT filtrada. Rango de tensión idéntico a TEMP_INT |

---

### 3.3 · DIP Switch Setpoint 3-bit (Pull-up Interna RP2350)

**Nota firmware:** El firmware activa `Pin.PULL_UP` (~50kΩ interno RP2350) en GP0, GP6 y GP7 antes de leer. No se requieren resistencias pull-up externas. Lógica inversa: DIP cerrado → pin LOW → bit '1'. DIP abierto → pin HIGH → bit '0'.

#### NET: NET_SW1 (Bit 0 / LSB — GP6)

| Net | Componente Origen (RefDes + Pin) | Componente Destino (RefDes + Pin) | Tipo de Señal / Notas Técnicas |
|---|---|---|---|
| NET_SW1 | SW1.Pin1 (DIP posición 1, terminal señal) | U1.GP6 / Pin7 (Input con pull-up) | Digital 3.3V entrada; nivel LOW cuando SW1 cerrado (DIP ON = bit 0 activo = LSB setpoint) |
| NET_SW1 | SW1.Pin2 (DIP posición 1, común/retorno) | AGND | Retorno; el polo común del switch va a AGND para completar el circuito de pull-down cuando se activa |

#### NET: NET_SW2 (Bit 1 — GP7)

| Net | Componente Origen (RefDes + Pin) | Componente Destino (RefDes + Pin) | Tipo de Señal / Notas Técnicas |
|---|---|---|---|
| NET_SW2 | SW1.Pin3 (DIP posición 2, terminal señal) | U1.GP7 (Input con pull-up interna) | Digital 3.3V entrada; Bit 1 del código setpoint. ⚠️ Verificar pad físico GP7 en XIAO RP2350 v1.0 |
| NET_SW2 | SW1.Pin4 (DIP posición 2, común/retorno) | AGND | Retorno DIP switch bit 1 |

#### NET: NET_SW3 (Bit 2 / MSB — GP0)

| Net | Componente Origen (RefDes + Pin) | Componente Destino (RefDes + Pin) | Tipo de Señal / Notas Técnicas |
|---|---|---|---|
| NET_SW3 | SW1.Pin5 (DIP posición 3, terminal señal) | U1.GP0 / Pin1 (Input con pull-up) | Digital 3.3V entrada; MSB del código setpoint de 3 bits |
| NET_SW3 | SW1.Pin6 (DIP posición 3, común/retorno) | AGND | Retorno DIP switch bit 2 |

---

### 3.4 · Control Puente H TB6612FNG (Actuador FIT0803)

#### NET: NET_AIN1 (GP2 → AIN1 TB6612FNG · Dirección 1)

| Net | Componente Origen (RefDes + Pin) | Componente Destino (RefDes + Pin) | Tipo de Señal / Notas Técnicas |
|---|---|---|---|
| NET_AIN1 | U1.GP2 / Pin3 (Output 3.3V) | U3.Pin18 (AIN1, control dirección A) | Digital 3.3V salida; define dirección 1 del puente H. Según hbridge.py: AIN1=0,AIN2=1 → abrir compuertas |

#### NET: NET_AIN2 (GP1 → AIN2 TB6612FNG · Dirección 2)

| Net | Componente Origen (RefDes + Pin) | Componente Destino (RefDes + Pin) | Tipo de Señal / Notas Técnicas |
|---|---|---|---|
| NET_AIN2 | U1.GP1 / Pin2 (Output 3.3V) | U3.Pin17 (AIN2, control dirección A) | Digital 3.3V salida; define dirección 2 del puente H. AIN1=1,AIN2=0 → cerrar compuertas |

#### NET: NET_MOTOR_EN (GP3 → PWMA TB6612FNG · Habilitación Canal A)

| Net | Componente Origen (RefDes + Pin) | Componente Destino (RefDes + Pin) | Tipo de Señal / Notas Técnicas |
|---|---|---|---|
| NET_MOTOR_EN | U1.GP3 / Pin4 (Output 3.3V) | U3.Pin19 (PWMA, enable/PWM canal A) | Digital 3.3V salida; HIGH = canal A activo. LOW = motor en stop (safe state según hbridge.py) |

#### NET: NET_STBY (STBY TB6612FNG · Tied HIGH Hardware)

| Net | Componente Origen (RefDes + Pin) | Componente Destino (RefDes + Pin) | Tipo de Señal / Notas Técnicas |
|---|---|---|---|
| NET_STBY | R5.Pin1 (10kΩ pull-up, entrada desde +3V3) | R5.Pin2 (salida pull-up hacia STBY) | DC 3.3V; resistencia pull-up hardware |
| NET_STBY | R5.Pin2 (salida pull-up) | U3.Pin16 (STBY, activo en HIGH) | Digital 3.3V; (★ CRÍTICO) STBY=HIGH habilita todos los canales del TB6612FNG. Si STBY=LOW, AO1/AO2/BO1/BO2 quedan en alta impedancia (fail-safe) |

#### Canal B TB6612FNG — No utilizado, terminaciones seguras

| Net | Componente Origen (RefDes + Pin) | Componente Destino (RefDes + Pin) | Tipo de Señal / Notas Técnicas |
|---|---|---|---|
| AGND | AGND (plano) | U3.Pin22 (BIN1, control B) | Digital; BIN1 a GND → modo STOP canal B |
| AGND | AGND (plano) | U3.Pin23 (BIN2, control B) | Digital; BIN2 a GND → modo STOP canal B |
| AGND | AGND (plano) | U3.Pin24 (PWMB, enable B) | Digital; PWMB=LOW → canal B deshabilitado. Safe state |
| NC | U3.Pin7 (BO2, salida B) | — (sin conexión) | NC; salida canal B no utilizado. No rutear ni conectar |
| NC | U3.Pin8 (BO2, duplicado) | — (sin conexión) | NC |
| NC | U3.Pin11 (BO1, salida B) | — (sin conexión) | NC |
| NC | U3.Pin12 (BO1, duplicado) | — (sin conexión) | NC |

---

### 3.5 · Control Ventilador 48V (GP4 → Gate IRL520N)

**Topología de ruta (con U4 poblado):**  
`U1.GP4 → U4.IN → U4.OUT → NET_VENT_GATE → R6 → NET_Q1_GATE → Q1.Gate`  
                                                              `↑`  
                                                    `R7 (pull-down) → PGND`  

**Topología de ruta (U4 NO poblado, JP1 poblado):**  
`U1.GP4 → JP1.Pin1 → JP1.Pin2 → NET_VENT_GATE → R6 → NET_Q1_GATE → Q1.Gate`

#### NET: NET_VENT (señal GP4 antes de U4 o JP1)

| Net | Componente Origen (RefDes + Pin) | Componente Destino (RefDes + Pin) | Tipo de Señal / Notas Técnicas |
|---|---|---|---|
| NET_VENT | U1.GP4 / Pin5 (Output digital) | U4.Pin3 (IN, entrada TC4420) | Digital 3.3V; señal de control ventilador hacia gate driver. (DNP si U4 no poblado) |
| NET_VENT | U1.GP4 / Pin5 (Output digital) | JP1.Pin1 (0Ω bypass, entrada) | Digital 3.3V; bypass directo GP4 → NET_VENT_GATE cuando U4 no está poblado. (DNP si U4 SÍ poblado) |

#### NET: NET_VENT_GATE (señal post-U4 o post-JP1, antes de R6)

| Net | Componente Origen (RefDes + Pin) | Componente Destino (RefDes + Pin) | Tipo de Señal / Notas Técnicas |
|---|---|---|---|
| NET_VENT_GATE | U4.Pin6 (OUT, salida TC4420) | R6.Pin1 (100Ω gate series, entrada) | Digital 0–5V; salida gate driver; V_HIGH = +5V → saturación plena IRL520N. (DNP si U4 no poblado) |
| NET_VENT_GATE | JP1.Pin2 (0Ω bypass, salida) | R6.Pin1 (100Ω gate series, entrada) | Digital 0–3.3V; bypass cuando U4 ausente. V_GS = 3.3V: operación marginal pero funcional (ver auditoría Fase 1) |

#### NET: NET_Q1_GATE (nodo Gate del IRL520N, entre R6 y el pin G)

| Net | Componente Origen (RefDes + Pin) | Componente Destino (RefDes + Pin) | Tipo de Señal / Notas Técnicas |
|---|---|---|---|
| NET_Q1_GATE | R6.Pin2 (100Ω serie, salida) | Q1.Pin1 (Gate, IRL520N) | Gate drive; R6 amortigua oscilaciones LC parásitas Gate–Source durante conmutación. Colocar R6 ≤5mm del Gate |
| NET_Q1_GATE | R6.Pin2 (100Ω serie, salida) | R7.Pin1 (10kΩ pull-down, entrada) | Pull-down Gate; en paralelo con la señal en el nodo Gate. R7 garantiza V_GS=0V cuando GP4=LOW, reset del MCU o ausencia de señal |
| NET_Q1_GATE | R6.Pin2 (100Ω serie, salida) | TP8.Pad1 | Test Point Gate; medir forma de onda de conmutación. Nivel esperado: ~0V (OFF) / ~3.3V sin U4 o ~5.0V con U4 (ON) |
| PGND | R7.Pin2 (10kΩ pull-down, retorno) | PGND (plano de potencia) | Retorno pull-down Gate a PGND; (★ CRÍTICO) pull-down referenciado a PGND, no a AGND |

---

### 3.6 · LED Indicador Power-On

#### NET: NET_LED_ANODE (entre R_LED y LED1)

| Net | Componente Origen (RefDes + Pin) | Componente Destino (RefDes + Pin) | Tipo de Señal / Notas Técnicas |
|---|---|---|---|
| NET_LED_ANODE | R_LED.Pin2 (1kΩ limitador, salida) | LED1.Ánodo / A (LED verde 0805) | DC 3.3V; nodo ánodo LED. V_A = 3.3V – I×R_LED. I_LED = (3.3–2.0)/1kΩ ≈ 1.3mA. Indicador visual de alimentación 3.3V activa |

---

## CATEGORÍA 4: NETS DE SALIDA DE POTENCIA

---

### 4.1 · Salida Actuador FIT0803 (TB6612FNG Canal A → J3)

**Notas de diseño PCB:**  
- Pines AO1 (Pin1 y Pin2) del TB6612FNG deben atarse con trazas paralelas de ≥1.5mm (corriente continua 1.2A, pico 3.2A)  
- Pines AO2 (Pin5 y Pin6) ídem  
- El conector J3 debe ubicarse lo más cerca posible de U3 para minimizar inductancia parásita en el lazo del puente H  
- Agregar capacitor de 100nF entre AO1 y AO2 en el conector J3 (supresión de EMI motor)

#### NET: NET_AO1 (Salida Motor A1 → J3.Pin1)

| Net | Componente Origen (RefDes + Pin) | Componente Destino (RefDes + Pin) | Tipo de Señal / Notas Técnicas |
|---|---|---|---|
| NET_AO1 | U3.Pin1 (AO1, salida A puente H) | U3.Pin2 (AO1, duplicado — atar en PCB) | DC Motor 5V; pines duplicados del IC. Atar con copper-pour o trazas en paralelo. No usar una sola traza delgada |
| NET_AO1 | U3.Pin1 (AO1, salida A puente H) | J3.Pin1 (bloque tornillo, terminal 1) | DC Motor 5V; terminal 1 del actuador FIT0803. Polaridad según modo: abrir=AO1(+), cerrar=AO1(–) |

#### NET: NET_AO2 (Salida Motor A2 → J3.Pin2)

| Net | Componente Origen (RefDes + Pin) | Componente Destino (RefDes + Pin) | Tipo de Señal / Notas Técnicas |
|---|---|---|---|
| NET_AO2 | U3.Pin5 (AO2, salida A puente H) | U3.Pin6 (AO2, duplicado — atar en PCB) | DC Motor 5V; pines duplicados del IC. Misma regla que AO1: trazas paralelas ≥1.5mm |
| NET_AO2 | U3.Pin5 (AO2, salida A puente H) | J3.Pin2 (bloque tornillo, terminal 2) | DC Motor 5V; terminal 2 del actuador FIT0803 |

---

### 4.2 · Salida Ventilador 48V (Q1 + D3 + J6)

**Descripción del nodo NET_FAN_HS:**  
Este es el nodo de conmutación de alta tensión. Durante operación:  
- **Q1 ON:** V(NET_FAN_HS) = V_PGND + V_DS(on) ≈ 0.4–1.5V (según corriente y R_DS)  
- **Q1 OFF:** V(NET_FAN_HS) transitoriamente puede alcanzar: +48V + Vf_D3 ≈ +49.7V antes de que D3 conduzca  
- **D3 (US1M):** clampea el nodo a +48V + 1.7V = 49.7V, protegiendo V_DS de Q1 (rated 100V → margen ×2 conservador)

**Trazas de potencia:** NET_FAN_HS ≥2mm. Colocar D3 lo más cerca posible del Drain de Q1 y del conector J6 para minimizar la inductancia del lazo de flyback.

#### NET: NET_FAN_HS (Nodo Drain Q1 / Fan(–) / Ánodo D3)

| Net | Componente Origen (RefDes + Pin) | Componente Destino (RefDes + Pin) | Tipo de Señal / Notas Técnicas |
|---|---|---|---|
| NET_FAN_HS | Q1.Pin2 (Drain, IRL520N) | D3.Ánodo / A (US1M flyback) | DC conmutación 48V; (★ CRÍTICO) Drain Q1 conectado al ánodo del flyback. Cuando Q1 abre, D3 conduce en sentido directo frenando el pico inductivo |
| NET_FAN_HS | Q1.Pin2 (Drain, IRL520N) | J6.Pin2 (bloque tornillo, Fan–) | DC conmutación 48V; terminal (–) del extractor MR1238E48B-FSR. Retorno de corriente del motor vía MOSFET |
| NET_FAN_HS | Q1.Pin2 (Drain, IRL520N) | TP7.Pad1 | Test Point Drain Q1; medir forma de onda de conmutación (¡precaución 48V, usar punta atenuadora!) |

#### Conexión Cátodo D3 → +48V (documentada también en Cat.1)

| Net | Componente Origen (RefDes + Pin) | Componente Destino (RefDes + Pin) | Tipo de Señal / Notas Técnicas |
|---|---|---|---|
| +48V | D3.Cátodo / K (US1M) | +48V (rail, incluye J5.Pin1, C10.Pin+, J6.Pin1) | DC 48V; el cátodo del flyback cierra el lazo de freewheeling al rail positivo. La energía inductiva se recircula al condensador C10 |

#### Conexión Source Q1 → PGND (documentada también en Cat.2)

| Net | Componente Origen (RefDes + Pin) | Componente Destino (RefDes + Pin) | Tipo de Señal / Notas Técnicas |
|---|---|---|---|
| PGND | Q1.Pin3 (Source, IRL520N) | PGND (plano de potencia, unido a J5.Pin2) | DC retorno potencia; (★ CRÍTICO) Source directamente al plano PGND. Traza de retorno debe ser corta y de baja inductancia para minimizar rebote V_GS durante conmutación |

#### Conexión Fan(+) → +48V (documentada también en Cat.1)

| Net | Componente Origen (RefDes + Pin) | Componente Destino (RefDes + Pin) | Tipo de Señal / Notas Técnicas |
|---|---|---|---|
| +48V | J6.Pin1 (bloque tornillo, Fan+) | +48V (rail) | DC 48V; terminal positivo del extractor. El ventilador opera con J6.Pin1=+48V y J6.Pin2=NET_FAN_HS controlado por Q1 |

---

## RESUMEN DE NETS Y CONTEO DE NODOS

| Net | # Nodos | Tipo | Notas |
|---|---|---|---|
| +48V | 5 | Potencia DC | Máxima precaución en campo, ≥2mm traces |
| +5V | 12 | Potencia DC | Alimenta motor + LDO |
| NET_3V3_LDO | 3 | Potencia DC (pre-fuse) | Solo C2, C4, F1 |
| +3V3 | 8 | Potencia DC (post-fuse) | Distribución lógica/analógica |
| PGND | 14 | Ground potencia | Plano trasero, retornos alta corriente |
| AGND | 20 | Ground analógico | Plano sensible, baja corriente |
| NT1 (AGND↔PGND) | 2 | Unión estrella | UN solo punto de contacto físico |
| NET_TEMP_INT_DIV | 3 | Analógico | Nodo divisor NTC1 |
| NET_TEMP_INT_FILT | 3 | Analógico | Nodo post-filtro GP26 |
| NET_TEMP_EXT_DIV | 3 | Analógico | Nodo divisor NTC2 |
| NET_TEMP_EXT_FILT | 2 | Analógico | Nodo post-filtro GP27 |
| NET_SW1 | 2 | Digital entrada | GP6, pull-up interna |
| NET_SW2 | 2 | Digital entrada | GP7, pull-up interna |
| NET_SW3 | 2 | Digital entrada | GP0, pull-up interna |
| NET_AIN1 | 2 | Digital salida 3.3V | GP2 → TB6612FNG |
| NET_AIN2 | 2 | Digital salida 3.3V | GP1 → TB6612FNG |
| NET_MOTOR_EN | 2 | Digital salida 3.3V | GP3 → TB6612FNG |
| NET_STBY | 2 | Digital tied HIGH | R5 → TB6612FNG |
| NET_VENT | 2 | Digital salida 3.3V | GP4 → U4 o JP1 |
| NET_VENT_GATE | 2 | Digital 3.3V o 5V | U4/JP1 → R6 |
| NET_Q1_GATE | 3 | Gate drive | R6 + R7 + Q1.Gate + TP8 |
| NET_LED_ANODE | 2 | DC 3.3V | R_LED → LED1 |
| NET_AO1 | 3 | DC Motor 5V | TB6612FNG → J3 |
| NET_AO2 | 3 | DC Motor 5V | TB6612FNG → J3 |
| NET_FAN_HS | 3 | DC conmutación 48V | Q1.Drain / D3.A / J6.Pin2 |
| **TOTAL** | **~106 nodos** | | **~81 conexiones únicas** |

---

*Documento generado: 2026-06-30 | Proyecto: Jaguar MX — Evaluación Técnica | Fase 2 de 4*  
*Pendiente de aprobación para avanzar a Fase 3: Esquemático KiCad v8*
