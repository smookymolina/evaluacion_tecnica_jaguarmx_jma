# FASE 4 — REGLAS DE DISEÑO, ESTRATEGIA DE LAYOUT Y RUTEADO FÍSICO
## Proyecto: Extractor de Aire Caliente — Gabinete de Telecomunicaciones
## Candidato: Ing. Jair Molina Arce | Evaluación Técnica Jaguar de México
## Revisión: A | Fecha: 2026-06-30 | Norma base: IPC-2152 / IPC-2221B

---

## EJE 1 — CONFIGURACIÓN DE NETCLASSES Y REGLAS DE DISEÑO (DRC)

### 1.1 Fundamento matemático — IPC-2152 External Conductors

**Cobre 1 oz (35 µm = 1.378 mils de espesor), capa externa, ΔT_max = 10 °C**

La ecuación IPC-2152 para conductores externos es:

```
I = 0.048 × ΔT^0.44 × A^0.725       [A en mils², ΔT en °C, I en Amperios]

Despejando A para un I dado:
A = ( I / (0.048 × ΔT^0.44) )^(1/0.725)

Para ΔT = 10 °C:
  factor_k = 0.048 × 10^0.44 = 0.048 × 2.7542 = 0.13220

Ancho de pista [mils] = A / 1.378
Ancho de pista [mm]   = Ancho [mils] × 0.0254
```

---

### 1.2 Clase 1 — Power_48V

**Nets asignadas:** `+48V`, `NET_FAN_HS` (conector J5.Pin1 → fan positivo)

**Corriente de diseño:**
- MR1238E48B-FSR: consumo nominal 0.8 A (medido), startup ~1.5× = 1.2 A
- Factor de seguridad industrial: ×1.67 → **I_diseño = 2.0 A** (garantiza ΔT < 10 °C con margen ante variación de fabricación)
- Para validación con 3 A (sobredimensionado absoluto): se calcula también

```
Cálculo para I = 2.0 A:
  A = (2.0 / 0.13220)^(1/0.725)
    = (15.129)^1.3793
    = e^(1.3793 × ln 15.129)
    = e^(1.3793 × 2.716)
    = e^3.745
    = 42.3 mils²

  Ancho_min = 42.3 / 1.378 = 30.7 mils = 0.780 mm

Verificación inversa con W = 1.5 mm (38 mils) (per CLAUDE.md ≥ 1.5 mm):
  A = 59.1 × 1.378 = 81.4 mils²
  I_max = 0.13220 × 81.4^0.725
        = 0.13220 × e^(0.725 × 4.399)
        = 0.13220 × e^3.189
        = 0.13220 × 24.25
        = 3.21 A  →  margen ×1.6 sobre I_diseño  ✓
```

**Parámetros de diseño Clase Power_48V:**

| Parámetro              | Valor calculado | Valor adoptado | Justificación                         |
|------------------------|-----------------|----------------|---------------------------------------|
| Ancho de pista mínimo  | 0.78 mm         | **1.5 mm**     | Norma interna CLAUDE.md + margen ×1.6 |
| Clearance (IPC-2221B B2 ≤50V)  | 0.60 mm min   | **0.6 mm**   | IPC-2221B Tabla 6-1, externo sin barniz |
| Diámetro de vía (drill)| —               | **0.8 mm**     | IPC-2152: ≥1.9 A por vía 0.8mm 1oz    |
| Anular de vía (pad)    | —               | **1.4 mm**     | Anular mínimo 0.3 mm + drill 0.8 mm   |

**Capacidad verificada de vía 0.8 mm drill, pared 25 µm:**
```
Área_vía = π × 0.8mm × 0.025mm = 0.0628 mm² = 97.4 mils²
I_vía = 0.13220 × 97.4^0.725
      = 0.13220 × e^(0.725 × 4.579)
      = 0.13220 × e^3.320
      = 0.13220 × 27.66 = 3.66 A por vía  ✓
```

---

### 1.3 Clase 2 — Power_5V

**Nets asignadas:** `+5V`, `NET_AO1`, `NET_AO2`, `PGND`

**Corriente de diseño por subcircuito:**

| Subcircuito                  | I_nominal | I_pico (startup) | I_diseño adoptado |
|------------------------------|-----------|------------------|-------------------|
| `+5V` rail total             | 1.8 A     | 3.2 A (TB6612 pk)| **3.0 A**         |
| `NET_AO1` / `NET_AO2` (motor)| 1.2 A     | 3.2 A (stall)    | **2.0 A**         |
| `PGND` (retorno de potencia) | suma ↑    | igual que arriba | **3.0 A**         |

```
Cálculo para NET_AO1/AO2 a I = 2.0 A:
  A = 42.3 mils² → ancho = 0.78 mm → adoptar 1.0 mm

Verificación inversa con W = 1.0 mm (39.4 mils):
  A = 39.4 × 1.378 = 54.3 mils²
  I_max = 0.13220 × 54.3^0.725
        = 0.13220 × e^(0.725 × 3.994)
        = 0.13220 × e^2.895
        = 0.13220 × 18.07
        = 2.39 A  →  margen ×1.19 sobre 2.0 A  ✓ (suficiente — pico protegido por TB6612 current limit)

Cálculo para +5V rail a I = 3.0 A:
  A = (3.0 / 0.13220)^1.3793 = (22.69)^1.3793
    = e^(1.3793 × 3.122) = e^4.305 = 73.9 mils²
  Ancho_min = 73.9 / 1.378 = 53.6 mils = 1.36 mm → adoptar 1.5 mm
```

**Parámetros de diseño Clase Power_5V:**

| Parámetro                    | NET_AO1/AO2   | Rail +5V / PGND | Justificación                          |
|------------------------------|---------------|-----------------|----------------------------------------|
| Ancho de pista mínimo        | **1.0 mm**    | **1.5 mm**      | IPC-2152 + margen startup FIT0803      |
| Clearance (IPC-2221B B2 ≤30V)| **0.3 mm**    | **0.3 mm**      | IPC-2221B: ≥0.1 mm para ≤30V          |
| Vía drill / pad              | 0.6 mm / 1.0 mm | 0.8 mm / 1.4 mm | Proporcional a corriente              |

**Capacidad verificada de vía 0.6 mm drill (pared 25 µm) en NET_AO1/AO2:**
```
Área_vía = π × 0.6mm × 0.025mm = 0.0471 mm² = 73.0 mils²
I_vía = 0.13220 × 73.0^0.725 = 0.13220 × 22.5 = 2.97 A por vía  ✓
```

---

### 1.4 Clase 3 — Signal_Logic

**Nets asignadas:** `+3V3`, `AGND`, `NET_SW1/2/3`, `NET_TEMP_INT_FILT`, `NET_TEMP_EXT_FILT`, `NET_AIN1`, `NET_AIN2`, `NET_MOTOR_EN`, `NET_VENT`, `NET_VENT_GATE`, `NET_VENT_DRV`, `NET_STBY`

**Corriente de diseño:**
- `+3V3` total: MCU 100 mA + LDO lógica 20 mA + pull-ups + TC4420 pico 100 mA ≈ **300 mA**
- Nets de señal (SW, TEMP_FILT, control): < 5 mA — límite manufacturabilidad domina

```
Cálculo para +3V3 a I = 0.30 A:
  A = (0.30 / 0.13220)^1.3793 = (2.269)^1.3793
    = e^(1.3793 × 0.819) = e^1.130 = 3.10 mils²
  Ancho_min = 3.10 / 1.378 = 2.25 mils = 0.057 mm

  → Límite real: tolerancia de fabricación. Ancho mínimo estándar JLCPCB/PCBWay = 0.127 mm
  → Adoptar 0.4 mm para +3V3 (margen ×7 sobre mínimo IPC, ×3 sobre límite fab)

Verificación con W = 0.4 mm (15.75 mils):
  A = 15.75 × 1.378 = 21.70 mils²
  I_max = 0.13220 × 21.70^0.725 = 0.13220 × 9.31 = 1.23 A
  Margen sobre 300 mA: ×4.1  ✓ (headroom para expansión futura del diseño)
```

**Parámetros de diseño Clase Signal_Logic:**

| Parámetro                    | Rail +3V3     | Señales (SW, NTC, ctrl) | Justificación                |
|------------------------------|---------------|-------------------------|------------------------------|
| Ancho de pista mínimo        | **0.4 mm**    | **0.2 mm**              | Fab limit 0.127mm + margen   |
| Clearance (IPC-2221B ≤15V)   | **0.15 mm**   | **0.15 mm**             | IPC-2221B: ≥0.1mm para ≤15V |
| Vía drill / pad              | 0.4 mm / 0.8 mm | 0.3 mm / 0.7 mm      | Estándar señal, min fab      |

---

### 1.5 Archivo de reglas DRC — `jaguar_extractor.kicad_dru`

Crear en el directorio del proyecto: `kicad/jaguar_extractor.kicad_dru`

```kicad_dru
(version 1)

# ══════════════════════════════════════════════════
#  JAGUAR EXTRACTOR — KiCad v8 Custom Design Rules
#  IPC-2152 / IPC-2221B | Cu 1oz | ΔT_max = 10°C
#  Rev A — 2026-06-30
# ══════════════════════════════════════════════════

# ── CLASE 1: Power_48V ────────────────────────────
(rule "Power48V_MinWidth"
  (constraint track-width (min 1.5mm))
  (condition "A.NetName == '+48V' || A.NetName == 'NET_FAN_HS'")
)

(rule "Power48V_Clearance"
  (constraint clearance (min 0.6mm))
  (condition "A.NetName == '+48V' || B.NetName == '+48V'")
)

(rule "Power48V_Via"
  (constraint via-diameter (min 1.4mm))
  (constraint hole-size    (min 0.8mm))
  (condition "A.NetName == '+48V' || A.NetName == 'NET_FAN_HS'")
)

# ── CLASE 2: Power_5V ─────────────────────────────
(rule "Power5V_Rail_MinWidth"
  (constraint track-width (min 1.5mm))
  (condition "A.NetName == '+5V' || A.NetName == 'PGND'")
)

(rule "Power5V_Motor_MinWidth"
  (constraint track-width (min 1.0mm))
  (condition "A.NetName == 'NET_AO1' || A.NetName == 'NET_AO2'")
)

(rule "Power5V_Clearance"
  (constraint clearance (min 0.3mm))
  (condition "A.NetName == '+5V' || B.NetName == '+5V'")
)

# ── CLASE 3: Signal_Logic ─────────────────────────
(rule "Signal_3V3_MinWidth"
  (constraint track-width (min 0.4mm))
  (condition "A.NetName == '+3V3'")
)

(rule "Signal_Logic_MinWidth"
  (constraint track-width (min 0.2mm))
  (condition "A.NetClass == 'Signal_Logic'")
)

(rule "Signal_Logic_Clearance"
  (constraint clearance (min 0.15mm))
  (condition "A.NetClass == 'Signal_Logic' && B.NetClass == 'Signal_Logic'")
)

# ── AISLAMIENTO CRÍTICO: 48V vs. resto ────────────
(rule "HV_to_Logic_Isolation"
  (constraint clearance (min 0.6mm))
  (condition "(A.NetName == '+48V' || A.NetName == 'NET_FAN_HS') &&
             (B.NetClass == 'Signal_Logic' || B.NetName == '+3V3')")
)

# ── RUTAS ANALÓGICAS: sin vías si es posible ──────
# Regla informativa: limita cambios de capa en rutas ADC sensibles
# (no es error DRC, es guía de ruteado — ver Eje 3)
(rule "Analog_MaxVias_INT"
  (constraint via-count (max 1))
  (condition "A.NetName == 'NET_TEMP_INT_FILT'")
)

(rule "Analog_MaxVias_EXT"
  (constraint via-count (max 1))
  (condition "A.NetName == 'NET_TEMP_EXT_FILT'")
)

# ── SEPARACIÓN ANALÓGICA vs. CONMUTACIÓN ──────────
(rule "Analog_vs_PWM_Spacing"
  (constraint clearance (min 0.5mm))
  (condition "(A.NetName == 'NET_TEMP_INT_FILT' || A.NetName == 'NET_TEMP_EXT_FILT') &&
             (B.NetName == 'NET_VENT' || B.NetName == 'NET_VENT_GATE' ||
              B.NetName == 'NET_VENT_DRV' || B.NetName == 'NET_MOTOR_EN')")
)

# ── TIERRA: separación de zonas ───────────────────
(rule "AGND_vs_PGND_Clearance"
  (constraint clearance (min 0.5mm))
  (condition "A.NetName == 'AGND' && B.NetName == 'PGND'")
)
```

### 1.6 Asignación de Netclasses en KiCad v8

```
Ruta: Archivo → Configuración del Esquema → Clases de Red

Clase: Power_48V
  Nets: +48V, NET_FAN_HS
  Track Width: 1.5 mm | Clearance: 0.6 mm | Via Drill: 0.8 mm | Via Pad: 1.4 mm

Clase: Power_5V
  Nets: +5V, NET_AO1, NET_AO2, PGND
  Track Width: 1.0 mm | Clearance: 0.3 mm | Via Drill: 0.6 mm | Via Pad: 1.0 mm

Clase: Signal_Logic
  Nets: +3V3, NET_3V3_LDO, AGND, NET_SW1, NET_SW2, NET_SW3,
        NET_TEMP_INT_DIV, NET_TEMP_INT_FILT, NET_TEMP_EXT_DIV, NET_TEMP_EXT_FILT,
        NET_AIN1, NET_AIN2, NET_MOTOR_EN, NET_VENT, NET_VENT_GATE,
        NET_VENT_DRV, NET_STBY
  Track Width: 0.2 mm | Clearance: 0.15 mm | Via Drill: 0.3 mm | Via Pad: 0.7 mm

Nota: La clase "Default" de KiCad se deja como fallback.
      Todos los nets anteriores deben asignarse explícitamente.
```

---

## EJE 2 — FLOORPLANNING Y ZONIFICACIÓN DE LA PLACA

### 2.1 Dimensiones y contorno del PCB

```
Dimensiones adoptadas: 80 mm × 55 mm (FR4, 1.6 mm, 1 oz Cu, 2 capas)
Herramienta KiCad: Board Setup → Physical Stackup

Origen (0,0): esquina inferior izquierda
Eje X: longitud 80 mm (horizontal)
Eje Y: longitud 55 mm (vertical)

Commandos en PCB Editor:
  Dibujar → Edge.Cuts → Rectángulo de 80×55 mm
  Radio de esquina: 2 mm (R2 – facilita panelización)
  Montura DIN: dejar espacio inferior 5 mm para tiras de cobre de anclaje
```

### 2.2 División bipartita: Hemisferio Lógico / Hemisferio de Potencia

```
Línea de frontera funcional: X = 40 mm (línea vertical central)
Esta frontera NO se dibuja físicamente en el PCB.
Se respeta como regla de placement durante el floorplanning.

 X=0                 X=40                X=80
  │                    │                    │
  ├────────────────────┼────────────────────┤
  │                    │                    │
  │  HEMISFERIO        │  HEMISFERIO        │
  │  LÓGICO/ANALÓGICO  │  DE POTENCIA       │
  │                    │                    │
  │  U1 (XIAO)         │  U3 (TB6612FNG)   │
  │  U2 (LDO)          │  Q1 (IRL520N)     │
  │  F1 (PPTC)         │  U4 (TC4420 DNP)  │
  │  LED1              │  D3 (US1M)        │
  │  SW4 (DIP)         │  J3 (FIT0803)     │
  │  J1/J2 (NTC)       │  J5 (Fan 48V)     │
  │  R1-R4, C5-C6      │  J6 (48V entrada) │
  │  D1, D2 (BAT54S)   │  J4/J9 (selector) │
  │  R9-R11, C12-C14   │  R6, R7, C10, C11 │
  │  C1-C4, C7-C9      │                   │
  │  TP6, TP7          │                   │
  │                    │                    │
  │                  NT1                   │
  │               (X≈40mm, Y≈15mm)        │
  └────────────────────┴────────────────────┘
```

### 2.3 Posición exacta de cada componente clave

**HEMISFERIO LÓGICO (X: 0–40 mm)**

```
Componente   Centro (X, Y)   Orientación   Notas de placement
──────────   ──────────────  ────────────  ─────────────────────────────────────────
U1 (XIAO)   (20, 30)        0°            USB-C hacia borde superior (Y=55). Espacio
                                           libre 2mm en todos los lados del módulo.
U2 (AP2112) (10, 45)        0°            Arriba-izquierda. Salida (VOUT) apunta
                                           hacia F1. Entrada (VIN) apunta a J7.
F1 (PPTC)   (18, 45)        90°           En línea entre U2.VOUT y bus +3V3.
LED1        (5, 48)         0°            Esquina superior izquierda — visible.
R_LED       (5, 44)         0°            En serie con LED1.
J7 (5V in)  (5, 50)         0°            Conector en borde superior izquierdo.
SW4 (DIP)   (10, 15)        0°            Borde inferior — acceso operador.
J1 (NTC in) (3, 35)         0°            Borde izquierdo — cable sensor interior.
J2 (NTC ex) (3, 25)         0°            Borde izquierdo — cable sensor exterior.
R1, R3, C5  (20, 37)        —             Cluster NTC_INT — junto a U1.GP26/A0.
D1 (BAT54S) (22, 37)        —             Inmediatamente antes de U1.GP26 (ver Eje 3).
R2, R4, C6  (20, 23)        —             Cluster NTC_EXT — junto a U1.GP27/A1.
D2 (BAT54S) (22, 23)        —             Inmediatamente antes de U1.GP27.
R9-R11      (12, 15)        —             Cluster pull-ups DIP — junto a SW4.
C12-C14     (12, 12)        —             Cluster bypass DIP — junto a pull-ups.
TP6, TP7    (24, 37)/(24,23) —            Test points accesibles (fuera de zonas de Via).
C1, C3      (8, 42)         —             Entrada LDO — < 3mm de U2.VIN.
C2, C4      (14, 42)        —             Salida LDO pre-fuse — < 3mm de U2.VOUT.
C9          (30, 42)        —             Desacoplamiento U3.VCC — cerca de U3.
```

**HEMISFERIO DE POTENCIA (X: 40–80 mm)**

```
Componente   Centro (X, Y)   Orientación   Notas de placement
──────────   ──────────────  ────────────  ─────────────────────────────────────────
U3 (TB6612) (55, 35)        0°            Centro del hemisferio. Pines PGND hacia J3.
Q1 (TO-220) (72, 20)        0°            Borde derecho. Tab hacia X=80 (exterior PCB).
                                           Pies: Gate(izq), Drain(centro), Source(der).
U4 (TC4420) (50, 22)        0°            DNP. Posición entre U3.AIN y Q1.Gate.
J4/J9       (55, 18)        0°            Selector junto a U4 — acceso operador.
D3 (US1M)   (68, 20)        0°            CRÍTICO: entre Q1.Drain y J5.Pin2 (ver Eje 3).
R6 (100Ω)   (66, 20)        0°            Entre J4.Pin2/U4.OUT y Q1.Gate — < 3mm gate.
R7 (10kΩ)   (70, 17)        90°           Pull-down: Q1.Gate a PGND — junto al gate.
J3 (actuad) (45, 10)        0°            Borde inferior izquierdo del hemisferio.
J5 (fan 48V)(75, 10)        0°            Borde inferior derecho.
J6 (48V in) (75, 45)        0°            Borde superior derecho — entrada 48V.
J8 (48V ret)(75, 38)        0°            Borde superior derecho — retorno PGND.
C7 (47µF)   (52, 28)        —             Desacoplamiento VM: < 3mm de U3.VM (pines 13,14).
C8 (100nF)  (53, 28)        —             En paralelo con C7.
C10 (100µF) (73, 38)        —             Bulk decoupling +48V — junto a J6.
C11 (100nF) (74, 40)        —             En paralelo con C10.
NT1 (NT)    (40, 15)        0°            FRONTERA exacta — ver sección 2.4.
```

### 2.4 Posicionamiento estratégico del Net-Tie NT1

```
NT1 se ubica en X=40 mm, Y=15 mm (borde inferior de la línea frontera).

Justificación EMC:
  El retorno de corriente de +5V llega a J7.Pin2 (borde superior izquierdo).
  El retorno de corriente de la carga del motor (PGND) viene de U3/Q1 hacia
  el borde inferior del hemisferio de potencia.
  Ubicar NT1 en Y=15mm (zona baja) minimiza el área del LAZO DE RETORNO
  compartido entre AGND y PGND:
    PGND_loop_area ≈ U3.PGND → [derecha] → J3/J5 → PGND → NT1 → AGND → J7 → +5V → U2 → +3V3 → U3.VCC
  Al bajar NT1 hacia los conectores de potencia, el área de este lazo es mínima.

Orientación del símbolo NT1 en el PCB:
  NT1.Pin1 (AGND) ← apunta hacia la izquierda (hemisferio lógico)
  NT1.Pin2 (PGND) ← apunta hacia la derecha (hemisferio potencia)
  La pista que une NT1 a cada plano de tierra debe ser la MÁS CORTA POSIBLE.
  Ancho de pista NT1: usar 1.5mm (misma clase que Power_5V — lleva corriente de retorno total).
```

### 2.5 Orientación de conectores de borde

```
Regla de placement: todos los conectores externos al borde del PCB.
  Borde superior  (Y=55mm): J7 (5V), J1 (NTC_INT), J2 (NTC_EXT), J8 (+48V entrada alternativa)
  Borde inferior  (Y=0mm):  J3 (actuador FIT0803), J5 (fan 48V), SW4 (DIP acceso operador)
  Borde derecho   (X=80mm): J6 (48V principal), Q1 tab (disipación)
  Borde izquierdo (X=0mm):  (libre — reservado para encapsulamiento)
```

---

## EJE 3 — MITIGACIÓN DE RUIDO EMI Y RUTEADO CRÍTICO

### 3.1 Célula de conmutación 48V — Minimización del lazo de freewheeling

**El lazo de freewheeling** es el área formada por los conductores que conducen
la corriente de recirculación del ventilador cuando Q1 se apaga.

```
LAZO DE FREEWHEELING (diagrama funcional):

  +48V ──┬── J5.Pin1 ──── Fan(+)
         │                   │
        C10               MR1238E48B
        C11              (inductancia)
         │                   │
  D3.K ──┘           Fan(-) = J5.Pin2
  D3.A ──────────────────────┤
                             │
                        Q1.Drain (NET_FAN_HS_SW)
                             │
                         Q1 (apagado)
                             │
                        Q1.Source → PGND

Cuando Q1=OFF:
  Fan(-) → D3 → +48V → [a través del condensador C10/C11] → +48V
  La corriente recircula por: D3.A → D3.K → C10/C11 → J5.Pin1 → Fan → J5.Pin2 → D3.A
```

**Reglas de ruteado para minimizar el área de este lazo:**

**Regla 3.1.1 — Proximidad D3 a J5**
```
D3 (US1M) se coloca a ≤ 5mm de J5.
El lazo J5.Pin1 → D3.K → D3.A → J5.Pin2 debe estar contenido en < 100 mm².
En el layout: D3 a la derecha de J5, entre J5 y Q1.Drain.

Ruta en PCB (F.Cu):
  J5.Pin1 (+48V, cátodo D3) → pista 1.5mm → D3.K
  D3.A → pista 1.5mm → Q1.Drain
  Q1.Drain → pista 1.5mm → J5.Pin2 (solo 1-2mm de traza)
```

**Regla 3.1.2 — Condensadores bulk inmediatos al rail 48V**
```
C10 (100µF) y C11 (100nF) se ubican entre J6.Pin1 (+48V entrada) y J5.Pin1 (fan+).
Máxima separación tolerable J6 → C10: ≤ 5 mm.
La pista J6.Pin1 → C10.Pin1 → J5.Pin1 es un segmento de 1.5mm en línea recta.
Nunca doblar esta pista con ángulos de 90° — usar curvas de 45° o arcos.
```

**Regla 3.1.3 — Pista de Gate de Q1 (R6)**
```
R6 (100Ω serie) debe colocarse lo más CERCA POSIBLE del gate de Q1, no del driver.
Razón: la traza larga Gate → R6 → Driver actúa como antena sintonizada a la
frecuencia de oscilación parásita del gate. Con R6 en el gate, se disipa la energía
de la oscilación en la propia resistencia, no en el aire.

Máxima longitud de pista Q1.Gate → R6: 3 mm.
Ancho de pista NET_VENT_GATE: 0.2mm (señal de control, no potencia).
Routing NET_VENT_GATE: en F.Cu solamente, sin cambio de capa.
Ninguna otra pista en paralelo con NET_VENT_GATE en longitud > 10 mm.
```

**Regla 3.1.4 — R7 pull-down del gate**
```
R7 (10kΩ) entre Q1.Gate y PGND: distancia máxima al gate = 5 mm.
La pista R7 → PGND via: usar vía directa a PGND_plane (no rodeo).
Propósito: R7 garantiza Q1=OFF en ausencia de señal (fail-safe industrial).
```

**Regla 3.1.5 — Secuencia de ruteado de la célula de conmutación**
```
Orden obligatorio para rutear la célula 48V:
  1. Rutear J6.Pin1 → C10.Pin1 → C11.Pin1 → J5.Pin1 (bus +48V, 1.5mm)
  2. Rutear J5.Pin2 → D3.A → Q1.Drain (bus commutation, 1.5mm)
  3. Rutear D3.K → J5.Pin1 (flyback return, 1.5mm, longitud < 5mm)
  4. Rutear Q1.Source → PGND_plane (vía directa, 1.5mm o vía ×2)
  5. Rutear J5.Pin1 → PGND_plane (retorno, vía a plano B.Cu)
  6. ÚLTIMOS: rutas de control (Gate, R6, R7, J4, U4)
```

---

### 3.2 Ruteado analógico sensible — J1/J2 → GP26/GP27

**Regla de oro analógica:** Los nodos `NET_TEMP_INT_FILT` y `NET_TEMP_EXT_FILT`
representan señales de < 3.3 V con impedancia de fuente efectiva de ~1 kΩ.
Una capacitancia parásita de solo 5 pF acopla suficiente ruido de switching
de 48 V para saturar el ADC de 12 bits. Cada regla aquí es no negociable.

**Regla 3.2.1 — División del camino en dos segmentos**
```
Segmento 1: J1.Pin1 → NET_TEMP_INT_DIV → R3.Pin1     (divisor NTC, pre-filtro)
  Puede ser más largo (hasta 30 mm). Señal de baja impedancia (divisor).
  Ancho: 0.2mm, cualquier capa.

Segmento 2: R3.Pin2 → NET_TEMP_INT_FILT → D1.Pin3 → C5 → U1.GP26   (post-filtro)
  DEBE ser ≤ 10 mm total. Alta impedancia después del filtro RC.
  Ancho: 0.2mm, F.Cu solamente (sin vías).
  Sin cambios de capa en este segmento.
```

**Regla 3.2.2 — Proximidad D1/D2 y C5/C6 al MCU**
```
Los condensadores C5/C6 y diodos D1/D2 se colocan en el LADO DEL MCU,
NO en el lado del conector J1/J2.

Razón: R3 (1kΩ) atenúa el ruido proveniente del conector antes de llegar
a la capacitancia de C5. C5 filtra. D1 clampea. El MCU ve la señal limpia.
Si C5 estuviera cerca de J1, el ruido estaría en la pista de alta impedancia
entre C5 y el MCU.

Ubicación D1, C5 respecto a U1.GP26: ≤ 3 mm del pad GP26.
Ubicación D2, C6 respecto a U1.GP27: ≤ 3 mm del pad GP27.
```

**Regla 3.2.3 — Separación respecto a trazas de conmutación**
```
NET_TEMP_INT_FILT y NET_TEMP_EXT_FILT deben mantener:
  ≥ 0.5 mm de cualquier traza de NET_VENT, NET_VENT_GATE, NET_AIN1, NET_AIN2
  ≥ 1.0 mm del perímetro del componente U3 (TB6612FNG)
  ≥ 2.0 mm del Q1 (MOSFET Q1 irradia campo magnético por gate charge)

Patrón de ruteado prohibido (CROSSTALK):
  ✗ PROHIBIDO: NET_TEMP_INT_FILT paralela a NET_MOTOR_EN por > 5 mm
  ✗ PROHIBIDO: NET_TEMP_EXT_FILT atravesando el hemisferio de potencia
  ✗ PROHIBIDO: Vías en NET_TEMP_*_FILT dentro de 10mm del Q1
```

**Regla 3.2.4 — Plano AGND como blindaje debajo de rutas analógicas**
```
Las pistas NET_TEMP_INT_FILT y NET_TEMP_EXT_FILT se rutean en F.Cu.
En B.Cu, en la zona exactamente debajo de estas pistas, AGND_zone debe
estar presente y continuo (sin interrupciones de pistas de potencia en B.Cu).

El plano AGND en B.Cu actúa como plano de retorno de baja impedancia
para los campos eléctricos de las señales analógicas.

Verificar en 3D View que no existan huecos en B.Cu/AGND bajo los segmentos
NET_TEMP_INT_FILT y NET_TEMP_EXT_FILT.
```

**Regla 3.2.5 — Dos canales NTC separados físicamente**
```
Los dos canales (INT y EXT) deben rotar en capas opuestas O separados ≥ 1.0 mm.
Nunca en paralelo en la misma capa, < 0.5 mm de separación, por más de 20 mm.
Cross-talk mínimo entre los dos canales = < 0.1% (error < 0.04°C en la medición).
```

**Regla 3.2.6 — Test points TP6 y TP7**
```
TP6 (NET_TEMP_INT_FILT) y TP7 (NET_TEMP_EXT_FILT):
  Colocar ANTES del BAT54S (D1.Pin3), no después.
  Razón: una punta de osciloscopio en el test point introduce ~10pF.
  Si el TP está después de D1 pero antes de C5, la carga del TP se suma a C5
  y desplaza la frecuencia de corte del filtro.
  Al colocar el TP antes de D1, la impedancia que "ve" el ADC no cambia
  durante la medición.
```

---

### 3.3 Ruteado del bus de control de compuertas (TB6612FNG)

```
NET_AIN1, NET_AIN2, NET_MOTOR_EN:
  Ancho: 0.2mm (señal lógica < 5mA)
  Capa: F.Cu preferiblemente
  Longitud máxima recomendada: < 30 mm cada una
  Separación mínima entre sí: 0.15 mm (DRC Signal_Logic)
  Separación de +5V/NET_AO1/NET_AO2: 0.3 mm (cruce de netclass)

  Pueden agruparse en un bus paralelo de 3 trazas (fanout de U1 hacia U3),
  manteniendo 0.15 mm de separación entre ellas.
  No rutearlas en paralelo con NET_TEMP_*_FILT por más de 20 mm.
```

---

## EJE 4 — ESTRATEGIA DE PLANOS DE TIERRA (STRICT STAR GROUND)

### 4.1 Configuración de zonas de cobre AGND y PGND en KiCad v8

**Ruta:** PCB Editor → Dibujar → Añadir Zona de Relleno

**Zona AGND — F.Cu (capa superior, hemisferio lógico)**
```
Red: AGND
Capa: F.Cu
Polígono: desde X=0 hasta X=39.5 mm, Y=0 a Y=55 mm  [con 0.5mm gap en X=40]
Prioridad de relleno: 1 (más alta)
Modo de relleno: Solid fill
Ancho mínimo de relleno: 0.25 mm
Conexión a pads SMD: Thermal Relief (spokes 0.5mm, gap 0.3mm)
  EXCEPTO: pads de decoupling (C1, C2, C3, C4, C5, C6, C9, C12-C14) → SOLID
Clearance a pistas externas: 0.25 mm
```

**Zona AGND — B.Cu (capa inferior, hemisferio lógico)**
```
Mismos parámetros geométricos que F.Cu/AGND.
Prioridad de relleno: 1
Este plano actúa como BLINDAJE de retorno para las señales analógicas en F.Cu.
CRÍTICO: No debe tener interrupciones bajo las rutas NET_TEMP_*_FILT en F.Cu.
```

**Zona PGND — F.Cu (capa superior, hemisferio de potencia)**
```
Red: PGND
Capa: F.Cu
Polígono: desde X=40.5 mm hasta X=80 mm, Y=0 a Y=55 mm
Prioridad de relleno: 1
Modo de relleno: Solid fill
Ancho mínimo de relleno: 0.3 mm
Conexión a pads:
  → U3.PGND pines: SOLID (máxima capacidad de corriente)
  → Q1.Source: SOLID (corriente total del MOSFET)
  → D3.Ánodo: SOLID (corriente de flyback)
  → Demás: Thermal Relief (0.5mm spokes, 0.3mm gap)
Clearance a AGND_zone: 0.5 mm (per .kicad_dru rule AGND_vs_PGND_Clearance)
```

**Zona PGND — B.Cu (capa inferior, hemisferio de potencia)**
```
Mismos parámetros geométricos que F.Cu/PGND.
Prioridad de relleno: 1
Bajo Q1: ZONA ESPECIAL de vías térmicas (ver sección 4.3).
```

### 4.2 Via Stitching entre capas F.Cu y B.Cu

**AGND Stitching (hemisferio lógico):**
```
Colocar vías de stitching en una grilla de 5 mm × 5 mm
en toda la zona AGND donde no haya componentes ni pistas.
Especificación de cada vía de stitching:
  Drill: 0.3 mm (mínimo fab)
  Pad: 0.7 mm
  Net: AGND
  Clase: Signal_Logic (vía pequeña, suficiente para equalización de potencial)
  Evitar: región bajo U1 (el XIAO tiene componentes en su footprint extendido)
          región bajo rutas analógicas activas (puede introducir ruido)
```

**PGND Stitching (hemisferio de potencia):**
```
Colocar vías de stitching en grilla de 3 mm × 3 mm (más densa — más corriente).
Especificación de cada vía de stitching PGND:
  Drill: 0.6 mm
  Pad: 1.0 mm
  Net: PGND
  Clase: Power_5V
  Densidad alta bajo U3 (TB6612FNG): área 10mm × 8mm bajo el componente.
  La zona de stitching bajo U3 mejora la capacidad de corriente del plano.
```

### 4.3 Vías térmicas bajo Q1 (IRL520N TO-220)

**Problema:** Q1 disipa P_loss ≈ 0.96 W (a I_fan = 0.8 A, RDS_on ≈ 1.5 Ω).
Sin disipador, θ_JA del TO-220 ≈ 60 °C/W → ΔT_J = 58 °C → T_J = 98 °C @ T_amb = 40 °C.
Aunque T_J_max IRL520N = 175 °C (margen existe), reducir T_J mejora MTTF.

**Solución: Via Array Térmico en PGND bajo posición Q1**

```
Geometría del TO-220:
  Cuerpo: ~15 mm × 10 mm
  Tab de montaje (Drain): ~10 mm × 8 mm de cobre expuesto

Copper pour de disipación en F.Cu (net PGND):
  Polígono: 12 mm × 8 mm centrado bajo el tab de Q1
  Conectado a PGND (Drain = tab del IRL520N)

Array de vías térmicas en este polígono:
  Drill: 0.4 mm | Pad: 0.8 mm | Net: PGND
  Grilla: 1.2 mm × 1.2 mm → ≈ 10×7 = 70 vías (ajustar según DRC)
  Estas vías transfieren calor del F.Cu al B.Cu/PGND (plano inferior actúa como heatsink)

Copper pour espejo en B.Cu (net PGND):
  Mismo polígono 12×8mm en B.Cu — el calor se disipa al aire por convección.

Estimación de mejora térmica:
  θ_via_array ≈ 20 °C/W (70 vías de 0.4mm en cobre 1oz)
  θ_JA efectivo ≈ 1/(1/60 + 1/20 + 1/35) [plano B.Cu solo] ≈ 30-35 °C/W
  ΔT_J_nuevo ≈ 0.96 W × 33 °C/W ≈ 32 °C → T_J ≈ 72 °C @ T_amb=40 °C  ✓
  Mejora: ~26 °C de reducción de temperatura de unión sin disipador externo.
```

**Instrucción KiCad v8:**
```
1. Dibujar Relleno de Zona en F.Cu, net PGND, polígono bajo Q1 (12×8mm)
2. Agregar Vías manualmente o via script en grilla 1.2mm × 1.2mm dentro del polígono
3. Dibujar Relleno de Zona en B.Cu, net PGND, mismo polígono 12×8mm (espejo)
4. Ejecutar Fill All Zones → verificar que ambas zonas se llenan correctamente
5. Verificar en 3D View que el bloque de vías sea visible en ambas caras
```

### 4.4 Regla de oro DRC: Prohibición absoluta de cruzar la ranura de aislamiento

```
DEFINICIÓN DE RANURA: La zona de clearance de 0.5mm entre AGND_zone y PGND_zone
(en X ≈ 39.5 a X ≈ 40.5 mm, o dondequiera que las zonas se aproximen).

REGLA: NINGUNA pista de señal, pista de potencia o componente (salvo NT1)
puede cruzar esta ranura de AGND a PGND.

Consecuencia si se viola:
  Una pista que cruce la ranura proporciona un camino de retorno de corriente
  de ruido de alta frecuencia desde la zona de potencia hacia la zona analógica.
  La corriente de switching de Q1 (dI/dt muy alto) encontraría retorno a través
  de la capacitancia parásita entre las pistas y el plano, creando rizado en
  AGND que afecta directamente a los ADC GP26/GP27.

Implementación en KiCad v8 (opcional pero recomendado):
  Herramienta → Añadir Área de Keepout (Keepout Area)
    Polígono: franja vertical de X=39mm a X=41mm, Y=0 a Y=55mm
    Restricciones: "No Tracks", "No Vias"
    EXCEPCIÓN: el keepout debe tener un hueco en Y=14 a Y=16mm para permitir NT1.

Verificación DRC:
  Ejecutar DRC → en la sección "Keepout" deben aparecer 0 violaciones.
  Si aparece alguna: localizar la pista que cruza → redirigirla por arriba o debajo
  del keepout, manteniéndose en su propio hemisferio de tierra.
```

### 4.5 Net-Tie NT1 — Reglas de layout del punto estrella

```
NT1 es el ÚNICO punto de cruce entre AGND y PGND permitido por el diseño.

Footprint sugerido en KiCad v8:
  Buscar: NetTie-2_Pads o NetTie_2_Angled
  Si no existe: crear footprint con 2 pads de 1.5mm × 1.5mm separados 0.3mm,
  ambos en F.Cu, con la marca de serigrafía "NT1" y "AGND←→PGND"

Pads del footprint NT1:
  Pad 1 → net AGND | Pad 2 → net PGND
  Los dos pads se tocan en cobre (sin máscara de soldadura entre ellos)
  → KiCad marca esto como net-tie, no como cortocircuito DRC.

Pistas hacia NT1:
  NT1.Pad1 → pista 1.5mm hacia AGND_zone (mínima longitud posible)
  NT1.Pad2 → pista 1.5mm hacia PGND_zone (mínima longitud posible)
  Longitud máxima de cada segmento: 3 mm.

No agregar vías en las pistas que conectan NT1 a cada zona.
El cambio de capa en el punto estrella introduciría inductancia en el retorno.
```

### 4.6 Configuración de relleno de zonas — Secuencia de ejecución

```
Secuencia OBLIGATORIA al final del ruteado para rellenar zonas correctamente:

  1. Colocar todos los componentes y completar TODAS las pistas.
  2. Board Setup → Design Rules → Constraints:
       Minimum Clearance: 0.15mm (valor global, override por .kicad_dru)
       Minimum Track Width: 0.2mm
       Copper to Edge Clearance: 0.3mm
  3. Cargar jaguar_extractor.kicad_dru (Board Setup → Rules → DRC Rules → Cargar)
  4. Ejecutar DRC sin zonas rellenas → corregir todos los errores antes de rellenar.
  5. Seleccionar "Fill All Zones" (tecla B).
  6. Verificar visualmente:
       F.Cu: AGND zona continua a la izquierda, PGND a la derecha.
       B.Cu: espejo de F.Cu.
       NT1: conexión visible entre los dos planos (sin islotes aislados).
       Q1: array de vías visible y conectado a B.Cu/PGND.
  7. Ejecutar DRC final → resultado esperado: 0 errores, solo advertencias suprimidas.
  8. Inspeccionar Net Inspector:
       AGND → ≥ 26 nodos conectados ✓
       PGND → ≥ 8 nodos conectados ✓
       NT1 conectado a ambos ✓
```

---

## RESUMEN EJECUTIVO — Parámetros PCB de la Tarjeta de Control

| Parámetro global          | Valor                         |
|---------------------------|-------------------------------|
| Dimensiones               | 80 × 55 mm                    |
| Capas                     | 2 (F.Cu + B.Cu)               |
| Material                  | FR4, 1.6 mm, Tg ≥ 130 °C     |
| Cobre                     | 1 oz (35 µm) en ambas capas   |
| Acabado superficial       | HASL-LF o ENIG (prototipo)    |
| Solder Mask               | Verde (ambas caras)           |
| Silkscreen                | Blanco cara superior          |
| Mínima pista              | 0.15 mm (fab) / 0.2 mm (DRC) |
| Mínimo taladro            | 0.3 mm (vías señal)           |
| Mínima anular             | 0.15 mm                       |
| Cobre a borde             | 0.3 mm                        |

| Parámetro por clase       | Power_48V  | Power_5V   | Signal_Logic |
|---------------------------|------------|------------|--------------|
| Ancho pista [mm]          | 1.5        | 1.0–1.5    | 0.2–0.4      |
| Clearance [mm]            | 0.6        | 0.3        | 0.15         |
| Vía drill [mm]            | 0.8        | 0.6        | 0.3          |
| Vía pad [mm]              | 1.4        | 1.0        | 0.7          |
| I_max en pista [A]        | 3.21       | 2.39       | 1.23 (+3V3)  |
| ΔT en I_diseño [°C]       | < 10       | < 10       | < 2          |

---

*Documento generado como parte de la Evaluación Técnica Jaguar de México — Ing. Jair Molina Arce*
*Uso de IA documentado en ETISEJr_JairMolina.md — Herramienta: Claude (Anthropic)*
*Fase 4 basada en Fase 3 (ERC limpio liberado) y Fase 2.1 (Netlist definitivo)*
