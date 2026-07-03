# FASE 3 — GUÍA DE DISEÑO DEL ESQUEMÁTICO KiCad v8
## Proyecto: Extractor de Aire Caliente — Gabinete de Telecomunicaciones
## Candidato: Ing. Jair Molina Arce | Evaluación Técnica Jaguar de México
## Revisión: A | Fecha: 2026-06-30 | Basado en: Fase 2.1 (26 nets / ~133 nodos)

---

## ÍNDICE

1. [Configuración previa del proyecto KiCad v8](#0-configuracion)
2. [Bloques 0 & 1 — MCU XIAO RP2350 + LDO AP2112K-3.3](#bloques-0-1)
3. [Bloque 2 — Sensado NTC (×2 canales)](#bloque-2)
4. [Bloque 3 — DIP Switch 3-bit + protección EMI](#bloque-3)
5. [Bloques 4 & 5 — Puente H TB6612FNG + Etapa MOSFET 48V](#bloques-4-5)
6. [Bloque 6 — Net-Tie NT1 (star ground AGND↔PGND)](#bloque-6)
7. [Verificación ERC final y configuración de reglas](#erc-final)
8. [Distribución sugerida del canvas](#layout)

---

## 0. CONFIGURACIÓN PREVIA DEL PROYECTO KiCad v8 {#configuracion}

### 0.1 Crear proyecto nuevo

```
Archivo → Nuevo Proyecto → Crear nuevo proyecto
  Nombre:    jaguar_extractor
  Directorio: kicad/
```

### 0.2 Configuración del esquemático

```
Abrir jaguar_extractor.kicad_sch con el Editor de Esquemáticos

Archivo → Configuración de página:
  Tamaño:    A3 (420 × 297mm) — landscape
  Título:    Extractor Aire Caliente — Jaguar MX
  Revisión:  A
  Fecha:     2026-06-30
  Empresa:   Evaluación Técnica — Ing. Jair Molina Arce
```

### 0.3 Preferencias de grilla

```
Preferencias → Preferencias de esquemático:
  Grilla de movimiento: 50 mil (estándar KiCad)
  Grilla de alambre:    25 mil
```

### 0.4 Instalación de librerías externas requeridas

**Librería Seeed Studio (para XIAO RP2350):**
```
Gestor de Complementos y Contenido (PCM) → Librerías → Buscar: "Seeed"
Instalar: Seeed Studio KiCad Library
  → Proporciona: Seeed_XIAO:XIAO_RP2350
```

Si PCM no está disponible o la librería Seeed no está en el índice, el símbolo XIAO RP2350 deberá importarse manualmente desde:
```
https://github.com/Seeed-Studio/OPL_Kicad_Library
Archivo de símbolo: Seeed_Microcontroller.kicad_sym
```

**Verificar presencia de estas librerías en el gestor de librerías de símbolos:**
- `Device` — resistencias, condensadores, diodos, fuses, Net-Tie ✓ (estándar)
- `Regulator_Linear` — AP2112K ✓ (verificar nombre exacto)
- `Transistor_FET` — IRL520N ✓ (verificar presencia)
- `Diode` — BAT54S, US1M ✓ (verificar nombres)
- `Motor_Driver` o `Interface_Motor` — TB6612FNG (verificar; posible creación manual)
- `Amplifier_Buffer` o `Driver_FET` — TC4420 (posible creación manual)
- `Switch` — SW_DIP_x03 ✓

### 0.5 Creación de símbolos de potencia personalizados

Las redes AGND, PGND y +48V no existen en la librería `power` estándar de KiCad. Se crean así:

**Método A — Power Symbol personalizado (recomendado):**
```
Editor de Símbolos → Archivo → Nueva librería → Nombre: jaguar_power
  → Nuevo símbolo en jaguar_power:
     AGND: copiar template de power:GND → renombrar → pin tipo Power Input
     PGND: igual a AGND, cambiar nombre y forma (línea diagonal para diferenciar)
     +48V: copiar template de power:VCC → renombrar → pin tipo Power Output
     +5V:  igual a +48V
```

**Método B — Net Labels con PWR_FLAG (alternativa rápida):**
```
Colocar net label "AGND" en cada conexión a tierra analógica
Colocar net label "PGND" en cada conexión a tierra de potencia
Agregar UN símbolo power:PWR_FLAG en cada una de estas redes
  → Ubica el PWR_FLAG en la red de mayor número de conexiones
```

> **NOTA CRÍTICA:** AGND y PGND deben ser redes distintas en todo el esquemático.
> NO usar `power:GND` en ningún punto del diseño.
> El único punto de unión física entre AGND y PGND es el Net-Tie NT1 (Bloque 6).

### 0.6 Referencia de nets críticos (Fase 2.1)

| Net Label en KiCad  | Descripción                             | Nodos |
|---------------------|-----------------------------------------|-------|
| `+3V3`              | Distribución 3.3V (post fuse F1)       | 13    |
| `+5V`               | Alimentación 5V (motor + LDO input)    | 4     |
| `+48V`              | Alimentación ventilador 48V            | 3     |
| `AGND`              | Tierra analógica/lógica (MCU, NTC)     | 26    |
| `PGND`              | Tierra de potencia (motor, fan, FET)   | 8     |
| `NET_3V3_LDO`       | Salida LDO antes de fusible F1         | 4     |
| `NET_TEMP_INT_DIV`  | Nodo divisor NTC interior              | 2     |
| `NET_TEMP_INT_FILT` | Nodo filtrado NTC interior (→ADC)      | 5     |
| `NET_TEMP_EXT_DIV`  | Nodo divisor NTC exterior              | 2     |
| `NET_TEMP_EXT_FILT` | Nodo filtrado NTC exterior (→ADC)      | 4     |
| `NET_AIN1`          | Control dirección H-bridge (→GP2)      | 2     |
| `NET_AIN2`          | Control dirección H-bridge (→GP1)      | 2     |
| `NET_MOTOR_EN`      | Habilitación H-bridge (→GP3)           | 2     |
| `NET_VENT`          | Control ventilador (GP4→U4.IN→J9.1)   | 3     |
| `NET_VENT_GATE`     | Señal hacia gate MOSFET (J9.2→R6.1)   | 2     |
| `NET_VENT_DRV`      | Salida TC4420 (U4.OUT→J9.3) — nuevo   | 2     |
| `NET_AO1`           | Salida canal A puente H (→J3.1)        | 3     |
| `NET_AO2`           | Salida canal A puente H (→J3.2)        | 3     |
| `NET_SW1`           | DIP bit 0 (→GP6)                       | 4     |
| `NET_SW2`           | DIP bit 1 (→GP8) ← MOD-1              | 4     |
| `NET_SW3`           | DIP bit 2 (→GP0)                       | 4     |
| `NET_STBY`          | STBY TB6612 pull-up                    | 2     |

---

## BLOQUES 0 & 1 — MCU XIAO RP2350 + LDO AP2112K-3.3 {#bloques-0-1}

### A. Componentes y símbolos KiCad

| RefDes | Valor / Part Number          | Símbolo KiCad v8                                   | Footprint                            |
|--------|------------------------------|----------------------------------------------------|--------------------------------------|
| U1     | Seeed XIAO RP2350            | `Seeed_XIAO:XIAO_RP2350`                          | Seeed_XIAO:XIAO_RP2350_Footprint    |
| U2     | AP2112K-3.3TRG1              | `Regulator_Linear:AP2112K-3.3TRG1`                | SOT-25-5 (Seeed_Package o equiv)    |
| F1     | MF-MSMF050-2 (500mA PPTC)   | `Device:Polyfuse` o `Device:Fuse`                  | Fuse_1812_4532Metric                |
| C1     | 10µF/10V cerámico X5R (in)  | `Device:C`                                         | 0805                                |
| C2     | 10µF/10V cerámico X5R (out) | `Device:C`                                         | 0805                                |
| C3     | 100nF cerámico (in bypass)   | `Device:C`                                         | 0402                                |
| C4     | 100nF cerámico (out bypass)  | `Device:C`                                         | 0402                                |
| LED1   | LED verde 3mm o SMD 0805     | `Device:LED`                                       | LED_0805_2012Metric                 |
| R_LED  | 1kΩ 0.125W                   | `Device:R`                                         | R_0402                              |
| J7     | Conector 5V entrada (2 pines)| `Connector:Conn_01x02`                             | TerminalBlock_Phoenix_1x02          |
| J8     | Conector +48V entrada (2 pin)| `Connector:Conn_01x02`                             | TerminalBlock_Phoenix_1x02          |

> **BÚSQUEDA AP2112K:** En el buscador de símbolos KiCad, escribir "AP2112".
> Si el resultado muestra `AP2112K-3.3` sin sufijo, usar ese. Si no existe, buscar
> `Regulator_Linear:AP2112` y verificar que el encapsulado sea SOT-25 (5 pines).
> Si no está en la librería: crear símbolo con pines: VIN(1), GND(2), VOUT(3), EN(4), NC(5).

### B. Instrucciones de conexionado — LDO U2 + Fuse F1

**Paso 1: Colocar U2 (AP2112K-3.3)**
```
Símbolo → colocar en canvas
Identificar pines:
  U2.VIN  (pin 1) ← red +5V
  U2.GND  (pin 2) → red AGND
  U2.VOUT (pin 3) → NET_3V3_LDO  [NET LABEL, no power symbol]
  U2.EN   (pin 4) → conectar con alambre corto al mismo nodo que U2.VIN (+5V)
                    [EN = VIN = siempre habilitado]
  U2.NC   (pin 5) → colocar marcador X de "No Conectar" (tecla Q en KiCad)
```

**Paso 2: Condensadores de entrada C1 y C3**
```
C1 (10µF): Pin1 → +5V | Pin2 → AGND    [cerca de U2.VIN, ≤3mm]
C3 (100nF): Pin1 → +5V | Pin2 → AGND   [el más cercano a U2.VIN]
```

**Paso 3: Condensadores de salida C2 y C4 — CRÍTICO**
```
C2 (10µF): Pin1 → NET_3V3_LDO | Pin2 → AGND
C4 (100nF): Pin1 → NET_3V3_LDO | Pin2 → AGND

⚠ ADVERTENCIA FASE 2.1: C2 y C4 se conectan a NET_3V3_LDO (ANTES del fusible F1).
  NO conectar C2/C4 al net +3V3 (después del fusible).
  Razón: F1 introduce impedancia en el lazo de retroalimentación del LDO
  causando inestabilidad. C2/C4 deben estar en el nodo de salida del LDO
  para compensar la respuesta en frecuencia del regulador.
```

**Paso 4: Fusible F1 (MF-MSMF050-2)**
```
F1.Pin1 → NET_3V3_LDO     [entrada del fusible]
F1.Pin2 → +3V3             [salida del fusible — red de distribución 3.3V]

Nota: El símbolo Device:Polyfuse es no polarizado. Pin1 y Pin2 son intercambiables
eléctricamente, pero establecer la convención Pin1=entrada, Pin2=salida por claridad.
```

**Paso 5: Indicador LED de potencia**
```
+3V3 → R_LED (1kΩ) → LED1.Anodo → LED1.Cátodo → AGND

Cálculo: I = (3.3V - 2.0V) / 1000Ω ≈ 1.3mA — suficiente para visibilidad
Agregar etiqueta de texto en canvas: "LED ENCENDIDO = +3V3 OK"
```

### C. Instrucciones de conexionado — MCU U1 (XIAO RP2350)

**Paso 6: Pines de alimentación U1**
```
U1.3V3  → +3V3           [input 3.3V desde el bus de distribución post-F1]
U1.GND  → AGND
U1.5V   → marcador X "No Conectar"  ← CRÍTICO: no conectar VBUS del XIAO
                                        [se alimenta desde 3V3; 5V=NC]

Nota: El XIAO RP2350 tiene regulación interna, pero al alimentar desde U2 (LDO externo)
por el pin 3V3, se bypasea la regulación interna. El pin 5V/VBUS debe quedar NC.
```

**Paso 7: Pines de señal U1 — conexiones a nets nombrados**

```
U1.GP0  → NET_SW3   [DIP Switch bit 2]
U1.GP1  → NET_AIN2  [H-Bridge dirección 2]
U1.GP2  → NET_AIN1  [H-Bridge dirección 1]
U1.GP3  → NET_MOTOR_EN [H-Bridge enable]
U1.GP4  → NET_VENT  [Control ventilador]
U1.GP5  → marcador X "No Conectar"  [no usado en diseño]
U1.GP6  → NET_SW1   [DIP Switch bit 0]
U1.GP7  → NET_SW2   [DIP Switch bit 1 — MOD-1: remapeo a GP7]
U1.GP8  → marcador X "No Conectar"  [⚠ GP8 = back pad B1, INACCESIBLE en castellación]
U1.GP26 → NET_TEMP_INT_FILT [ADC0 — temperatura interna]
U1.GP27 → NET_TEMP_EXT_FILT [ADC1 — temperatura exterior]
```

> **MOD-1 EN EL ESQUEMÁTICO:** Agregar nota de ingeniería junto al pin GP7 del XIAO:
> `{NOTA MOD-1: SW2 asignado a GP7 (D5, Pin 6, castellación lateral). GP8=back pad B1 inaccesible en XIAO RP2350}`

**Paso 8: Pines SWD (opcional, depuración)**
```
U1.SWDIO → net label "SWDIO" (o NC si no se incluyó header de debug)
U1.SWDCLK → net label "SWDCLK" (o NC)
Los demás pines sin uso → marcadores X individuales
```

### D. Etiquetas y notas en el canvas — Bloque 0 & 1

Agregar los siguientes textos en el canvas cerca de los componentes:

```
[Junto a U2 y F1]:
"U2: AP2112K-3.3 — LDO 600mA SOT-25
 VIN=+5V, EN puente a VIN (siempre ON)
 Salida → NET_3V3_LDO → F1 (MF-MSMF050-2, 500mA)
 → +3V3 distribución"

[Junto a C2/C4]:
"⚠ C2/C4 conectan a NET_3V3_LDO (pre-fusible)
 NO a +3V3 — estabilidad LDO"

[Junto a U1.5V]:
"NC — XIAO alimentado por pin 3V3
 desde LDO externo U2"

[Junto a U1.GP7]:
"NC — GP7 = back pad B1
 NO accesible en XIAO RP2350
 MOD-1: SW2 → GP8"
```

### E. ERC — Advertencias esperadas y cómo resolverlas

| Advertencia ERC                              | Causa                          | Solución                                    |
|----------------------------------------------|--------------------------------|---------------------------------------------|
| "Pin sin conectar en U1.GP5"                 | GPIO no usado                  | Marcador NC ya colocado — OK                |
| "Pin sin conectar en U1.GP7"                 | Back pad inaccesible           | Marcador NC + nota MOD-1 — OK              |
| "Pin sin conectar en U1.5V"                  | VBUS no usado                  | Marcador NC ya colocado — OK                |
| "Pin de potencia sin driver en +3V3"         | Power rail sin fuente          | Agregar `power:PWR_FLAG` en el net +3V3    |
| "Pin de potencia sin driver en NET_3V3_LDO" | Subred intermedia              | Agregar `power:PWR_FLAG` en NET_3V3_LDO    |

---

## BLOQUE 2 — SENSADO NTC (×2 canales: TEMP_INT y TEMP_EXT) {#bloque-2}

> Este bloque se dibuja DOS VECES con componentes simétricos.
> Reemplazar sufijo `_INT` por `_EXT` y referencias R1→R2, R3→R4, C5→C6, D1→D2, J1→J2, TP6→TP7.

### A. Componentes y símbolos KiCad

| RefDes | Valor / Part Number              | Símbolo KiCad v8                       | Footprint                          |
|--------|----------------------------------|----------------------------------------|------------------------------------|
| R1     | 10kΩ 0.1% 25ppm (ref divisor)   | `Device:R`                             | R_0603                             |
| R2     | 10kΩ 0.1% 25ppm (ref divisor)   | `Device:R`                             | R_0603                             |
| NTC1   | TT05-10KC8-1S-T105-1500          | `Device:R_Thermistor_NTC`              | (sensor remoto — ver nota)         |
| NTC2   | TT05-10KC8-1S-T105-1500          | `Device:R_Thermistor_NTC`              | (sensor remoto — ver nota)         |
| J1     | JST-PH 2-pin — sensor TEMP_INT   | `Connector_JST:JST_PH_B2B-PH-K_1x02_P2.00mm_Vertical` | Connector_JST:JST_PH_2-2.00mm_Vertical |
| J2     | JST-PH 2-pin — sensor TEMP_EXT   | `Connector_JST:JST_PH_B2B-PH-K_1x02_P2.00mm_Vertical` | (igual a J1)                       |
| R3     | 1kΩ 1% filtro RC (INT)           | `Device:R`                             | R_0402                             |
| R4     | 1kΩ 1% filtro RC (EXT)           | `Device:R`                             | R_0402                             |
| C5     | 100nF 50V X7R filtro (INT)       | `Device:C`                             | C_0402                             |
| C6     | 100nF 50V X7R filtro (EXT)       | `Device:C`                             | C_0402                             |
| D1     | BAT54S — protección ADC (INT)    | `Diode:BAT54S` o `Device:D_Dual_Series_AKC` | SOT-23                        |
| D2     | BAT54S — protección ADC (EXT)    | (igual a D1)                           | SOT-23                             |
| TP6    | Test point — TEMP_INT_FILT       | `Connector:TestPoint` o `Device:TP`    | TestPoint_THTPad_D1.5mm            |
| TP7    | Test point — TEMP_EXT_FILT       | (igual a TP6)                          | (igual a TP6)                      |

> **NOTA SENSOR NTC:** El NTC TT05 es un sensor con cable remoto. En el esquemático,
> el símbolo `Device:R_Thermistor_NTC` representa el NTC como componente en la PCB.
> Sin embargo, J1/J2 son los conectores JST donde se conecta el cable del sensor externo.
> La NTC en el esquemático (NTC1/NTC2) puede representar un footprint de montaje alternativo
> en placa (si se desea NTC de montaje SMD) O puede dejarse como "dummy" conectado a J1.
> La topología definitiva es: R1 → [nodo divisor] → J1 (conector cable NTC) → AGND.

### B. Instrucciones de conexionado — Canal TEMP_INT (duplicar para TEMP_EXT)

**Paso 1: Divisor de voltaje NTC**
```
+3V3 → R1.Pin1
R1.Pin2 → NET_TEMP_INT_DIV   [net label]
NET_TEMP_INT_DIV → J1.Pin1   [pin "+" del conector]
J1.Pin2 → AGND               [pin "-" del conector, cable del NTC va a tierra]
```

> La NTC TT05 (con cable) se conecta entre J1.Pin1 y J1.Pin2.
> El NTC cierra el divisor hacia AGND: R1 (arriba) + NTC_cable (abajo).

**Paso 2: Filtro RC (R3 + C5)**
```
NET_TEMP_INT_DIV → R3.Pin1
R3.Pin2 → NET_TEMP_INT_FILT  [net label]
C5.Pin1 → NET_TEMP_INT_FILT
C5.Pin2 → AGND

fc = 1/(2π × 1kΩ × 100nF) = 1.59 kHz — filtra ruido de switching
```

**Paso 3: BAT54S D1 — protección de clamping en nodo filtrado**

```
⚠ PINOUT CONTRAINTUITIVO — VERIFICAR ORIENTACIÓN DEL SÍMBOLO

BAT54S en SOT-23 (vista superior):
  Pin 1 = Ánodo inferior  (A1)  → red AGND     (clamp a GND)
  Pin 2 = Cátodo superior (K2)  → red +3V3     (clamp a VCC)
  Pin 3 = Nodo central    (K1/A2) → NET_TEMP_INT_FILT  (señal a proteger)

Conexión en KiCad con símbolo Diode:BAT54S:
  D1.Pin1 (A1) → AGND
  D1.Pin2 (K2) → +3V3
  D1.Pin3 (K1/A2 — centro) → NET_TEMP_INT_FILT

Con símbolo Device:D_Dual_Series_AKC:
  El pin "A" del símbolo = D1.Pin1 → AGND
  El pin "K" del símbolo = D1.Pin2 → +3V3
  El pin "C" (centro) del símbolo = D1.Pin3 → NET_TEMP_INT_FILT
```

> **¿Por qué este pinout?** El BAT54S tiene dos diodos Schottky en serie.
> Corriente de polarización normal (señal en operación): < 1µA — despreciable.
> Si la señal excede +3V3 → diodo superior (A2→K2) conduce, clampea a +3.6V max.
> Si la señal baja de -0V → diodo inferior (A1→K1) conduce, clampea a -0.3V min.
> Resultado: ADC GP26/GP27 protegido entre -0.3V y +3.6V con mínima carga al divisor.

**Paso 4: Test point y conexión al ADC**
```
NET_TEMP_INT_FILT → TP6.Pin1   [test point para medición]
NET_TEMP_INT_FILT → U1.GP26    [net label a MCU — conectar con net label, no alambre físico]
```

> **CONVENCIÓN:** Usar net labels (no alambres largos) para conectar el nodo FILT al MCU.
> El net label `NET_TEMP_INT_FILT` aparece tanto en Bloque 2 como junto al pin GP26 del MCU.
> KiCad los une automáticamente por nombre de net.

### C. Etiquetas y notas en el canvas — Bloque 2

```
[Junto a R1]:
"R1: 10kΩ 0.1% 25ppm — R_ref divisor NTC
 = R0 del NTC → máxima sensibilidad ADC @ 25°C"

[Junto a D1]:
"D1: BAT54S SOT-23
 Pin3 (centro K1/A2) → señal
 Pin1 (A1) → AGND | Pin2 (K2) → +3V3
 Clamp: -0.3V / +3.6V @ <1µA en operación normal
 ⚠ MOD-2: sustituye TVS SMBJ3.3A (Fase 2.0)"

[Junto a R3/C5]:
"RC Anti-alias: R3=1kΩ | C5=100nF
 fc = 1.59kHz | τ = 100µs
 Filtro ANTES del BAT54S — corrección topología MOD-2"

[Junto a J1]:
"J1: JST-PH 2pin
 Pin1 = NTC+ (divisor)
 Pin2 = NTC- (AGND)
 NTC: TT05-10KC8-1S-T105-1500
 Beta=3435K, R0=10kΩ@25°C, Tmax=105°C"
```

### D. Verificación de la topología resistiva (canal INT)

```
Red completa canal INT:
+3V3 → R1(10kΩ) → NET_TEMP_INT_DIV → R3(1kΩ) → NET_TEMP_INT_FILT → U1.GP26
                         ↓                              ↓
                    J1.Pin1                        C5(100nF) → AGND
                    J1.Pin2 → AGND              D1.Pin3(centro)
                                                D1.Pin1 → AGND
                                                D1.Pin2 → +3V3
                                                TP6
```

---

## BLOQUE 3 — DIP SWITCH 3-BIT + PROTECCIÓN EMI {#bloque-3}

### A. Componentes y símbolos KiCad

| RefDes | Valor / Part Number                | Símbolo KiCad v8              | Footprint                           |
|--------|-------------------------------------|-------------------------------|-------------------------------------|
| SW4    | DIP Switch 3 posiciones            | `Switch:SW_DIP_x03`           | SW_DIP_SPSTx03_Slide_3.96x7.62mm   |
| R9     | 10kΩ 5% pull-up SW1               | `Device:R`                    | R_0402                              |
| R10    | 10kΩ 5% pull-up SW2               | `Device:R`                    | R_0402                              |
| R11    | 10kΩ 5% pull-up SW3               | `Device:R`                    | R_0402                              |
| C12    | 100nF 50V X7R bypass SW1          | `Device:C`                    | C_0402                              |
| C13    | 100nF 50V X7R bypass SW2          | `Device:C`                    | C_0402                              |
| C14    | 100nF 50V X7R bypass SW3          | `Device:C`                    | C_0402                              |

> **SÍMBOLO DIP SWITCH:** `Switch:SW_DIP_x03` proporciona 3 interruptores SPST.
> Si no existe, usar 3 símbolos `Device:SW_SPST` individuales (SW4a, SW4b, SW4c).
> El footprint físico sigue siendo un DIP de 3 posiciones.

### B. Instrucciones de conexionado — DIP Switch + EMI

```
Lógica: pull-up activo. Pin LOW = switch cerrado = bit '1'.
SW4 posición 1 = SW1 (bit 0, GP6)
SW4 posición 2 = SW2 (bit 1, GP7) ← MOD-1
SW4 posición 3 = SW3 (bit 2, GP0)
```

**Bit 0 — SW1 → GP6:**
```
+3V3 → R9.Pin1
R9.Pin2 → NET_SW1               [net label]
NET_SW1 → SW4.Bit1.Pin_común    [un lado del interruptor 1]
SW4.Bit1.Pin_NC → AGND          [otro lado del interruptor 1 a tierra]
C12.Pin1 → NET_SW1
C12.Pin2 → AGND
NET_SW1 → U1.GP6                [net label en MCU]
```

**Bit 1 — SW2 → GP7 (MOD-1):**
```
+3V3 → R10.Pin1
R10.Pin2 → NET_SW2              [net label]
NET_SW2 → SW4.Bit2.Pin_común
SW4.Bit2.Pin_NC → AGND
C13.Pin1 → NET_SW2
C13.Pin2 → AGND
NET_SW2 → U1.GP7                [⚠ GP7, NO GP8 — MOD-1]
```

**Bit 2 — SW3 → GP0:**
```
+3V3 → R11.Pin1
R11.Pin2 → NET_SW3              [net label]
NET_SW3 → SW4.Bit3.Pin_común
SW4.Bit3.Pin_NC → AGND
C14.Pin1 → NET_SW3
C14.Pin2 → AGND
NET_SW3 → U1.GP0                [net label en MCU]
```

### C. Tabla de setpoints — Agregar en el canvas como texto

```
+------------------------------------------+
| TABLA SETPOINTS DIP SWITCH               |
| SW3 SW2 SW1 | Setpoint | Código binario  |
|  0   0   0  |  40°C    |    000          |
|  0   0   1  |  45°C    |    001          |
|  0   1   0  |  50°C    |    010          |
|  0   1   1  |  55°C    |    011          |
|  1   0   0  |  60°C    |    100          |
|  1   0   1  |  65°C    |    101          |
|  1   1   0  |  70°C    |    110          |
|  1   1   1  |  75°C    |    111          |
| Lógica: LOW=1, HIGH=0 (pull-up activo)   |
+------------------------------------------+
```

### D. Notas de ingeniería en el canvas — Bloque 3

```
[Junto a R9/R10/R11 + C12/C13/C14]:
"Filtro EMI por canal DIP:
 R_ext=10kΩ ∥ R_int≈50kΩ → R_eff=8.3kΩ
 fc_eff = 1/(2π × 8.3kΩ × 100nF) ≈ 192Hz
 MOD-3: pull-up externo + cap bypass
 Entorno industrial 48V — protección contra EMI"

[Junto a SW4.Bit2 y U1.GP7]:
"⚠ MOD-1: SW2 → GP7 (D5, Pin 6 lateral del XIAO)
 GP8 = back pad B1, no castellado
 Actualizar dip_switch.py: SW2_PIN = 7"
```

---

## BLOQUES 4 & 5 — PUENTE H TB6612FNG + ETAPA MOSFET 48V {#bloques-4-5}

### A. Componentes y símbolos KiCad

| RefDes | Valor / Part Number                | Símbolo KiCad v8                        | Footprint                              |
|--------|-------------------------------------|-----------------------------------------|----------------------------------------|
| U3     | TB6612FNG (SSOP-24)                 | `Motor_Driver:TB6612FNG`                | SSOP-24_5.3x8.2mm_P0.65mm             |
| R5     | 10kΩ pull-up STBY                   | `Device:R`                              | R_0402                                 |
| C7     | 47µF/10V electrolítico (desac. VM)  | `Device:C_Polarized`                    | C_0805                                 |
| C8     | 100nF cerámico (desac. VM)          | `Device:C`                              | C_0402                                 |
| C9     | 100nF cerámico (desac. VCC)         | `Device:C`                              | C_0402                                 |
| J3     | Conector 2-pin — actuador FIT0803   | `Connector:Conn_01x02`                  | TerminalBlock_Phoenix_1x02             |
| U4     | TC4420CPA (SOIC-8) — gate driver    | `Amplifier_Buffer:TC4420` (o manual)    | SOIC-8_3.9x4.9mm_P1.27mm              |
| C15    | 100nF cerámico (desac. U4, DNP)     | `Device:C`                              | C_0402                                 |
| Q1     | IRL520N (TO-220)                    | `Transistor_FET:IRL520N`                | TO-220-3_Vertical                      |
| R6     | 330Ω gate series resistor           | `Device:R`                              | R_0402                                 |
| R7     | 10kΩ gate pull-down                 | `Device:R`                              | R_0402                                 |
| D3     | US1M (SMA/DO-214AC) flyback         | `Diode:US1M` o `Device:D`              | D_SMA                                  |
| C10    | 100µF/63V electrolítico +48V rail   | `Device:C_Polarized`                    | C_0810                                 |
| C11    | 100nF cerámico +48V bypass          | `Device:C`                              | C_0402                                 |
| J4     | Header 3-pin 2.54mm — selector J9  | `Connector_PinHeader_2.54mm:PinHeader_1x03_P2.54mm_Vertical` | PinHeader_1x03_P2.54mm_Vertical |
| J5     | Conector 2-pin — fan 48V           | `Connector:Conn_01x02`                  | TerminalBlock_Phoenix_1x02             |
| J6     | Conector 2-pin — alimentación 48V  | `Connector:Conn_01x02`                  | TerminalBlock_Phoenix_1x02             |

> **NOTA TB6612FNG:** Si `Motor_Driver:TB6612FNG` no está disponible, buscar en:
> `Interface_Motor:TB6612FNG` o `Motor:TB6612FNG`. Si no existe en ninguna,
> crear símbolo manual con los 24 pines del SSOP-24 según la tabla de pines siguiente.

**Tabla de pines TB6612FNG para símbolo manual:**
```
SSOP-24 (en orden de numeración):
 1: AO1a   2: AO1b   3: PGNDa  4: PGNDb  5: AO2a   6: AO2b
 7: BO2a   8: BO2b   9: PGNDc  10: PGNDd 11: BO1a  12: BO1b
13: VMa   14: VMb   15: VCC   16: STBY  17: AIN2  18: AIN1
19: PWMA  20: GNDa  21: GNDb  22: BIN2  23: BIN1  24: PWMB
(a/b = pines dobles de la misma función — cortocircuitar en símbolo)
```

### B. Instrucciones de conexionado — TB6612FNG (U3)

**Paso 1: Alimentación U3**
```
U3.VM  (pines 13,14) → +5V       [alimentación motor — VM máximo 15V]
U3.VCC (pin 15)      → +3V3      [alimentación lógica]
U3.GND (pines 20,21) → AGND      [tierra lógica]
U3.PGND(pines 3,4,9,10) → PGND  [tierra de potencia]

Desacoplamiento junto a U3:
  C7 (47µF): entre +5V y PGND    [más cercano a VM pines 13,14]
  C8 (100nF): entre +5V y PGND   [en paralelo con C7]
  C9 (100nF): entre +3V3 y AGND  [cerca de VCC pin 15]
```

**Paso 2: STBY — habilitación permanente (R5)**
```
+3V3 → R5.Pin1 (10kΩ)
R5.Pin2 → NET_STBY → U3.STBY (pin 16)

⚠ CRÍTICO: Si STBY = LOW → motor completamente deshabilitado (safe state).
  El pull-up R5 mantiene STBY=HIGH en operación normal.
  Nota en canvas: "STBY=HIGH vía R5 — required para habilitar TB6612FNG"
```

**Paso 3: Canal A — Control actuador FIT0803**
```
U3.AIN1 (pin 18) → NET_AIN1 → U1.GP2    [net label al MCU]
U3.AIN2 (pin 17) → NET_AIN2 → U1.GP1    [net label al MCU]
U3.PWMA (pin 19) → NET_MOTOR_EN → U1.GP3 [net label al MCU]

Tabla de operación Canal A (agregar en canvas):
┌─────────────────────────────────────────────────────┐
│ AIN1  AIN2  PWMA │ AO1  AO2  │ Acción              │
│  0     1     1   │  +    -   │ Abrir compuertas    │
│  1     0     1   │  -    +   │ Cerrar compuertas   │
│  0     0     0   │  0    0   │ STOP (safe state)   │
│  x     x     0   │  HIZ  HIZ │ Coast (alta Z)      │
└─────────────────────────────────────────────────────┘
```

**Paso 4: Salida Canal A → conector actuador J3**
```
U3.AO1 (pines 1,2) → NET_AO1 → J3.Pin1   [terminal A del motor]
U3.AO2 (pines 5,6) → NET_AO2 → J3.Pin2   [terminal B del motor]

Agregar junto a J3:
"J3: FIT0803 @ 5V nominal (rated 6V)
 Velocidad estimada: 5.8mm/s
 ACTUATOR_TRAVEL_MS = 3000ms (margen ×1.75)
 Calibrar con cronómetro en sesión en vivo"
```

**Paso 5: Canal B — Terminaciones (canal B no usado)**
```
U3.BIN1 (pin 22) → AGND
U3.BIN2 (pin 23) → AGND
U3.PWMB (pin 24) → AGND
U3.BO1  (pines 11,12) → marcadores NC individuales
U3.BO2  (pines 7,8)   → marcadores NC individuales

Nota en canvas: "Canal B no usado — BIN1/BIN2/PWMB → AGND (safe state)"
```

### C. Instrucciones de conexionado — Selector J9 (MOD-4)

**Descripción del selector:**
```
J9 es un header 3-pin 2.54mm con jumper removible.
Permite seleccionar entre dos modos de control del MOSFET Q1:

  MODO A (Bypass TC4420):  Jumper en pines 1-2
    GP4 → directo al gate de Q1 (vía R6)
    Funciona porque Vgs(th) IRL520N = 1.0-2.0V < 3.3V del GPIO

  MODO B (Con TC4420):     Jumper en pines 2-3
    GP4 → U4.IN → U4.OUT → gate de Q1 (vía R6)
    TC4420 convierte 3.3V → 5V en el gate
    Mejor margen de encendido, menor RDS(on)
```

**Paso 6: Conexionado J9 en el esquemático**

Usando el designador J4 en el esquemático (para distinguir de otros conectores J):
```
J4 = Header 3-pin (referenciado como "J9" en el diseño funcional)

J4.Pin1 → NET_VENT     [recibe señal GP4 y también entrada U4.IN]
J4.Pin2 → NET_VENT_GATE [sale hacia R6.Pin1 → gate Q1]
J4.Pin3 → NET_VENT_DRV  [recibe salida U4.OUT — nuevo net MOD-4]
```

**Cuadro de texto obligatorio junto a J4 en el canvas:**
```
╔══════════════════════════════════════════╗
║  SELECTOR J9 — MODO CONTROL MOSFET Q1  ║
╠══════════════════════════════════════════╣
║ Jumper 1-2: BYPASS TC4420               ║
║   GP4 → directo → R6 → Gate Q1         ║
║   Usar si 3.3V suficiente (Vgs ≥ 2V)   ║
╠══════════════════════════════════════════╣
║ Jumper 2-3: CON TC4420 (U4)             ║
║   GP4 → U4.IN → U4.OUT → R6 → Gate    ║
║   Mejor conmutación, menor RDS(on)      ║
╚══════════════════════════════════════════╝
```

### D. Instrucciones de conexionado — TC4420 U4

```
U4 = TC4420CPA SOIC-8
  Pines (SOIC-8 estándar TC4420):
    Pin 1: NC     → marcador NC
    Pin 2: NC     → marcador NC
    Pin 3: IN     → NET_VENT     [recibe GP4 y se conecta también a J4.Pin1]
    Pin 4: GND    → PGND         [tierra del driver — en zona PGND para retorno MOSFET]
    Pin 5: VCC    → +5V          [alimentación driver]
    Pin 6: OUT    → NET_VENT_DRV → J4.Pin3   [nuevo net MOD-4]
    Pin 7: NC     → marcador NC
    Pin 8: NC     → marcador NC

Desacoplamiento U4:
  100nF cerámico (C15) entre U4.VCC (pin 5) y U4.GND (pin 4) — Colocar C15 como DNP.
```

> **NOTA TC4420 DNP:** U4 es un componente "No Montar" (DNP) en la configuración por defecto.
> En KiCad v8, abrir propiedades de U4 → pestaña Atributos → marcar "Do not populate".
> Esto lo excluye del BOM de fabricación pero lo mantiene en el esquemático para la opción.

```
Nota en canvas junto a U4:
"U4: TC4420CPA — GATE DRIVER OPCIONAL (DNP por defecto)
 VIN = +5V, Vout_gate = 5V nivel
 Activar con jumper J9 pines 2-3
 Instalar si RDS(on) elevado o temperatura Q1 > 60°C"
```

### E. Instrucciones de conexionado — MOSFET Q1 (IRL520N)

```
Q1 = IRL520N TO-220 N-Channel
  Pines TO-220: G=Gate(1), D=Drain(2=central), S=Source(3)

Q1.Gate (pin 1)  → NET_VENT_GATE  [recibe de J4.Pin2]
Q1.Drain (pin 2) → NET_FAN_SW     [a D3.Cátodo y J5.Pin1]
Q1.Source (pin 3) → PGND

Circuito de gate:
  NET_VENT_GATE → R6.Pin1 (330Ω)
  R6.Pin2 → Q1.Gate
  Q1.Gate → R7.Pin1 (10kΩ pull-down)
  R7.Pin2 → PGND
```

**Notas en canvas junto a Q1:**
```
"Q1: IRL520N TO-220 N-Ch
 Vds=100V, Ids=10A, Vgs(th)=1.0-2.0V
 @Vgs=3.3V: RDS(on)≈1-1.8Ω
 P_loss @ 0.8A: P = 0.8² × 1.5Ω ≈ 0.96W — OK TO-220
 R6=330Ω: limita corriente de gate para proteger el GPIO
 R7=10kΩ: pull-down → Q1 OFF sin señal (fail-safe)"
```

### F. Instrucciones de conexionado — Diodo flyback D3 (US1M)

```
D3 = US1M SMA (DO-214AC)
  Cátodo (banda) → J5.Pin1 (ánodo ventilador, lado positivo 48V del motor)
  Ánodo          → J5.Pin2 (PGND — retorno ventilador)

  POLARIDAD: D3 conduce cuando el ventilador es apagado y L_motor genera
  tensión negativa en su terminal positivo. El flyback conduce de PGND hacia
  el rail de +48V a través del ventilador (inversamente al motor).

Nota en canvas junto a D3:
"D3: US1M SMA — Flyback ventilador
 Vrmm=1kV (margen ×20 sobre 48V)
 Irr=1A, trr=35ns (57× más rápido que 1N4007)
 MOD: sustituye 1N4007 original
 Polaridad: CÁTODO al +48V del motor"
```

### G. Instrucciones de conexionado — Conectores ventilador 48V

```
J6 = Entrada +48V alimentación
  J6.Pin1 → +48V        [positivo]
  J6.Pin2 → PGND        [negativo/retorno]

Desacoplamiento en rail +48V:
  C10 (100µF/63V): entre +48V y PGND    [electrolítico, cerca de J6]
  C11 (100nF): entre +48V y PGND        [cerámico, en paralelo con C10]

J5 = Salida a ventilador MR1238E48B-FSR
  J5.Pin1 → +48V        [positivo al ventilador]
  J5.Pin2 → Q1.Drain (NET_FAN_SW) ← el MOSFET Q1 conmuta el retorno
           [El retorno del ventilador pasa por Q1 hacia PGND]

Topología completa ventilador:
  +48V → J5.Pin1 → MR1238E48B-FSR(+) → MR1238E48B-FSR(-) → J5.Pin2
  → Q1.Drain → Q1.Source → PGND

D3 (US1M) en paralelo con ventilador:
  D3.Cátodo → J5.Pin1 (+48V/fan)
  D3.Ánodo  → J5.Pin2 (retorno = Q1.Drain)
```

**Cuadro control ventilador en canvas:**
```
"MR1238E48B-FSR: 48V DC, 1.9A max
 Control: Q1 (NMOS) conmuta retorno a PGND
 ON: GP4=HIGH → Q1.Vgs≥2V → Q1 ON → fan GND = PGND → fan gira
 OFF: GP4=LOW → Q1 OFF → fan GND = flotante (D3 absorbe flyback)"
```

---

## BLOQUE 6 — NET-TIE NT1 (STAR GROUND AGND↔PGND) {#bloque-6}

### A. Componentes y símbolos KiCad

| RefDes | Valor / Part Number     | Símbolo KiCad v8        | Footprint                              |
|--------|-------------------------|-------------------------|----------------------------------------|
| NT1    | Net-Tie (cobre directo) | `Device:Net-Tie-2`      | NetTie-2_Pads (o NetTie_2_Angled)     |

> El símbolo `Device:Net-Tie-2` en KiCad v8 tiene dos pads físicamente conectados
> en cobre pero asignados a dos nets distintos. Esto permite unir AGND y PGND en
> un solo punto físico sin que el DRC/ERC lo marque como error de red corta.

### B. Instrucciones de conexionado — NT1

**Paso 1: Localizar y colocar el símbolo**
```
Agregar símbolo → buscar "Net-Tie-2" en librería Device
Colocar en zona de separación entre bloque AGND y bloque PGND
```

**Paso 2: Asignar nets a los dos pines del Net-Tie**
```
NT1.Pin1 → AGND   [red de tierra analógica/lógica]
NT1.Pin2 → PGND   [red de tierra de potencia]

En KiCad v8, el Net-Tie-2 une físicamente Pin1 y Pin2 en el PCB
sin cortocircuitar las redes en el DRC (el footprint tiene la excepción).
```

**Paso 3: Posicionamiento estratégico en el esquemático**
```
Ubicar NT1 como punto de convergencia entre:
  - La última conexión de AGND del bloque de potencia
  - La primera conexión de PGND

En el canvas, trazar una línea visual (texto) indicando la separación:
  Zona izquierda del NT1 = AGND (lógica/analógica)
  Zona derecha del NT1 = PGND (potencia)
```

### C. Notas de ingeniería en el canvas — Bloque 6

```
[Junto a NT1]:
"NT1: Net-Tie — Punto único de unión AGND↔PGND
 Cobre directo (0Ω) — SIN ferrita
 MOD-5: Elimina impedancia en retorno de alta frecuencia
 de Q1 y TB6612FNG que generaba lazo EMI

 Regla de layout PCB (OBLIGATORIA):
   NT1 debe colocarse cerca de J7.Pin2 (retorno +5V)
   para minimizar el área del lazo de retorno PGND→AGND

 ← AGND (zona analógica/lógica)  PGND (zona potencia) →"

[Cuadro de separación de tierras en el canvas]:
"ARQUITECTURA DE TIERRA — SINGLE STAR POINT
 ┌─────────────────┬──────────────────────┐
 │    AGND          │     PGND             │
 │ MCU (U1)         │ TB6612FNG (U3)       │
 │ LDO (U2)         │ MOSFET Q1            │
 │ NTC R1/R2        │ Ventilador (J5/J6)   │
 │ Filtros R3/R4    │ Actuador (J3)        │
 │ BAT54S D1/D2     │ D3 flyback           │
 │ DIP SW4          │                      │
 │ LED1             │                      │
 └──────────┬───────┴──────────────────────┘
            NT1 (punto estrella único)"
```

---

## VERIFICACIÓN ERC FINAL Y CONFIGURACIÓN DE REGLAS {#erc-final}

### 7.1 Ejecutar ERC

```
Inspeccionar → Verificador de Reglas Eléctricas (ERC)
Ejecutar ERC → revisar lista de errores/advertencias
```

### 7.2 Errores esperados y resolución

| Error ERC                                              | Causa                                 | Acción                                                     |
|--------------------------------------------------------|---------------------------------------|------------------------------------------------------------|
| "Pin sin conectar: U1.GP5"                             | GPIO no usado                         | Marcador NC — ignorar o suprimir                           |
| "Pin sin conectar: U1.GP7"                             | Back pad inaccesible MOD-1            | Marcador NC + agregar comentario MOD-1                     |
| "Pin sin conectar: U1.5V"                              | VBUS no usado intencionalmente        | Marcador NC                                                |
| "Pin sin conectar: U1.SWDIO/SWDCLK"                   | Debug port sin header (opcional)      | Marcador NC si no se agrega header de depuración           |
| "Pin sin conectar: U3.BO1a,BO1b,BO2a,BO2b"           | Canal B del TB6612 no usado           | Marcadores NC — correcto                                   |
| "Pin sin conectar: U4.NC×4"                            | Pines NC del TC4420                   | Marcadores NC — correcto                                   |
| "Red de potencia sin fuente: +3V3"                     | KiCad no ve driver en esta red        | Agregar `power:PWR_FLAG` en el net +3V3                   |
| "Red de potencia sin fuente: NET_3V3_LDO"             | Subred interna sin power symbol       | Agregar `power:PWR_FLAG` en NET_3V3_LDO                   |
| "Red de potencia sin fuente: +5V"                      | Igual                                 | PWR_FLAG en +5V                                            |
| "Red de potencia sin fuente: +48V"                     | Igual                                 | PWR_FLAG en +48V                                           |
| "Red de potencia sin fuente: AGND"                     | Si se usó net label en vez de power   | PWR_FLAG en AGND                                           |
| "Red de potencia sin fuente: PGND"                     | Igual                                 | PWR_FLAG en PGND                                           |
| "Tipos de pin incompatibles en Net-Tie NT1"            | Normal en Net-Tie                     | Suprimir esta advertencia — es el comportamiento correcto  |

### 7.3 Configurar supresión de errores específicos

```
En la ventana ERC, click derecho en el error → "Ignorar este error"
O en: Configuración del Proyecto → ERC → Exclusiones → agregar las reglas:

  pin_unconnected: U1 GP5, GP7, 5V  [pines NC intencionales]
  pin_unconnected: U3 BO1*, BO2*    [canal B no usado]
  net_no_driver: NET_3V3_LDO        [subred sin power symbol — tiene PWR_FLAG]
```

### 7.4 Checklist de verificación manual (antes de pasar al PCB)

```
□ Todos los GPIOs mapeados correctamente según tabla en CLAUDE.md
□ GP8 → NC (no conectado) | GP7 → NET_SW2 ✓ (MOD-1)
□ U1.5V → NC (no conectar VBUS) ✓
□ U2.EN conectado a U2.VIN (no flotante) ✓
□ C2/C4 en NET_3V3_LDO (pre-fuse), NO en +3V3 ✓
□ D1.Pin3 (BAT54S centro) → NET_TEMP_INT_FILT | D1.Pin1 → AGND | D1.Pin2 → +3V3 ✓
□ D2.Pin3 (BAT54S centro) → NET_TEMP_EXT_FILT | D2.Pin1 → AGND | D2.Pin2 → +3V3 ✓
□ U3.STBY → R5 → +3V3 (STBY=HIGH permanente) ✓
□ U3.BIN1/BIN2/PWMB → AGND | BO1/BO2 → NC ✓
□ J4 (J9 funcional): Pin1=NET_VENT | Pin2=NET_VENT_GATE | Pin3=NET_VENT_DRV ✓
□ NET_VENT_DRV: solo 2 nodos (U4.OUT → J4.Pin3) — net nuevo MOD-4 ✓
□ D3.Cátodo → lado +48V ventilador | D3.Ánodo → Q1.Drain ✓
□ NT1.Pin1 → AGND | NT1.Pin2 → PGND (único punto de unión) ✓
□ PWR_FLAG colocados en: +3V3, NET_3V3_LDO, +5V, +48V, AGND, PGND ✓
□ Todos los marcadores NC colocados en pines sin usar ✓
□ ERC limpio o con solo advertencias suprimidas y documentadas ✓
□ Netlist exportada y validada: 26 nets / ~133 nodos ✓
```

---

## DISTRIBUCIÓN SUGERIDA DEL CANVAS {#layout}

```
Hoja A3 — Landscape

┌──────────────────────────────────────────────────────────────────────────────────┐
│                                                                        TITLE BOX │
│                                                                                  │
│  ┌──────────────────┐  ┌────────────────┐  ┌───────────────────────────────┐   │
│  │  BLK 0&1         │  │  BLK 1 (cont) │  │  BLK 2 — NTC SENSING (×2)   │   │
│  │  XIAO RP2350     │  │  LDO AP2112K  │  │  ┌─────────────┐             │   │
│  │  U1 (centro)     │  │  + Fuse F1    │  │  │  TEMP_INT   │ TEMP_EXT   │   │
│  │  GPIOs → labels  │  │  + LED power  │  │  │  R1,R3,C5   │ R2,R4,C6   │   │
│  │                  │  │  U2, C1-C4    │  │  │  D1,J1,TP6  │ D2,J2,TP7  │   │
│  └──────────────────┘  └────────────────┘  │  └─────────────┘             │   │
│                                              └───────────────────────────────┘   │
│                                                                                  │
│  ┌─────────────────────┐  ┌──────────────────────────────────────────────────┐  │
│  │  BLK 3 — DIP SW    │  │  BLK 4 & 5 — TB6612FNG + MOSFET 48V            │  │
│  │  SW4 (3-bit)       │  │                                                   │  │
│  │  R9/R10/R11        │  │  ┌──────────┐  ┌─────────────────────────────┐  │  │
│  │  C12/C13/C14       │  │  │ TB6612   │  │ J9 selector + U4 + Q1      │  │  │
│  │  Tabla setpoints   │  │  │ U3, J3   │  │ R6, R7, D3                 │  │  │
│  │  Nota MOD-1/MOD-3  │  │  │ R5, C7-9 │  │ J5, J6, C10, C11           │  │  │
│  └─────────────────────┘  │  └──────────┘  └─────────────────────────────┘  │  │
│                            └──────────────────────────────────────────────────┘  │
│                                                                                  │
│  ┌──────────────────────────────────────────────────────────────────────────┐   │
│  │  BLK 6 — NET-TIE NT1   ←AGND──────────────────────────PGND→           │   │
│  │  NT1 (Device:Net-Tie-2)  |  Diagrama star ground  |  Nota MOD-5        │   │
│  └──────────────────────────────────────────────────────────────────────────┘   │
│                                                                                  │
└──────────────────────────────────────────────────────────────────────────────────┘
```

---

## RESUMEN DE MODIFICACIONES (MOD-1 a MOD-5) EN EL ESQUEMÁTICO

| MOD  | Qué cambia en el esquemático                                           | Símbolo afectado       |
|------|------------------------------------------------------------------------|------------------------|
| MOD-1| U1.GP7 (no GP8) conectado a NET_SW2. GP8 = NC con marcador X          | U1 (XIAO RP2350)       |
| MOD-2| D1/D2 = BAT54S (no SMBJ3.3A) en nodo FILT (no en nodo DIV)           | D1, D2                 |
| MOD-3| R9/R10/R11 + C12/C13/C14 agregados. Pull-ups 10kΩ + bypass 100nF     | R9-R11, C12-C14        |
| MOD-4| J9 = header 3-pin (no solder bridge JP1). NET_VENT_DRV es net nuevo    | J4(J9), U4             |
| MOD-5| NT1 = Device:Net-Tie-2 (no ferrita). Unión directa AGND↔PGND         | NT1                    |

---

*Documento generado como parte de la Evaluación Técnica Jaguar de México — Ing. Jair Molina Arce*
*Uso de IA documentado en ETISEJr_JairMolina.md — Herramienta: Claude (Anthropic)*
*Fase 3 basada en Fase 2.1 LIBERADA (26 nets / ~133 nodos / ~107 conexiones mínimas)*
