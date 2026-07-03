# Plano de Placement paso a paso — Jaguar MX

> Vamos a colocar los 53 componentes desde cero, en orden lógico. Coordenadas = **absolutas en mm** (las que ves abajo-izquierda en KiCad como `X … Y …`). No tienen que ser exactas: usa la rejilla y el ojo; lo importante es el **bloque** y que las líneas blancas queden cortas.

---

## Mapa de bloques (vista de la placa)

```
 X=110                    X=150 (frontera)                 X=190
  ┌──────────────────────────┬──────────────────────────────┐  Y=70
  │ J7  U2/F1  [caps LDO]     │        C10 C11  ── J6         │  (arriba)
  │ TP1 TP2 TP5               │        TP3                    │
  │ J1 ─[R1 R3 D1 C5]         │   C7 C8   R5                  │
  │        ╲                  │      ┌────────┐               │
  │      ┌──────┐             │      │  U3    │   Q1          │
  │      │  U1  │  C9         │      │ TB6612 │  R6 R7 TP8    │
  │      │ XIAO │             │      └────────┘               │
  │ J2 ─[R2 R4 D2 C6]         │   U4    J9      D3            │
  │        ╱                  │                               │
  │ SW1 [R9-11 C12-14]        │  J3 ───────────────  J5       │
  │ LED1 R_LED1               │       (actuador)  (ventilador)│  (abajo)
  │                        NT1│                               │
  └──────────────────────────┴──────────────────────────────┘  Y=125
        HEMISFERIO LÓGICO/ANALÓGICO        HEMISFERIO DE POTENCIA
```

**Regla de oro:** todo lo lógico/analógico a la IZQUIERDA (X<149), todo lo de potencia a la DERECHA (X>151). NT1 justo en la frontera.

---

## Orden de colocación (7 fases)

> Se colocan primero las "anclas" (chips grandes y conectores), luego los pasivos **alrededor** de su chip. Así las líneas blancas se acortan solas.

### FASE A — Las 2 anclas (define las mitades)
| Orden | Comp | Poner en (X,Y) | Nota |
|---|---|---|---|
| 1 | **U1** (XIAO MCU) | (133, 97) | Centro-izquierda. USB hacia arriba |
| 2 | **U3** (TB6612) | (165, 90) | Centro-derecha |

### FASE B — Conectores de borde
| Orden | Comp | (X,Y) | Nota |
|---|---|---|---|
| 3 | **J7** (5V in) | (115, 73) | Borde superior izq |
| 4 | **J1** (NTC int) | (113, 88) | Borde izq |
| 5 | **J2** (NTC ext) | (113, 104) | Borde izq |
| 6 | **J6** (48V in) | (184, 82) | Borde derecho |
| 7 | **J3** (actuador) | (157, 118) | Borde inferior centro |
| 8 | **J5** (ventilador) | (179, 118) | Borde inferior derecho |
| 9 | **SW1** (DIP) | (120, 114) | Borde inferior izq (acceso operador) |

### FASE C — ICs de soporte y potencia
| Orden | Comp | (X,Y) | Nota |
|---|---|---|---|
| 10 | **U2** (LDO) | (120, 80) | Arriba-izq, cerca de J7 |
| 11 | **Q1** (MOSFET) | (180, 100) | Derecha. Patas: Gate-Drain-Source |
| 12 | **U4** (driver, DNP) | (159, 106) | Entre U3 y Q1 |
| 13 | **J9** (selector) | (171, 111) | Junto a U4/Q1 |
| 14 | **NT1** (net-tie) | (150, 110) | EN la frontera X=150 |

### FASE D — Cadena NTC (¡lo más delicado, mantener corto!)
Cada cadena va del conector → resistencias → diodo → cap → pata del MCU.
| Orden | Comp | (X,Y) | Cadena |
|---|---|---|---|
| 15 | **R3** (1k int) | (123, 89) | J1→R3 |
| 16 | **R1** (10k int) | (120, 91) | divisor |
| 17 | **D1** (BAT54S int) | (126, 89) | protección |
| 18 | **C5** (filtro int) | (126, 92) | pegado al MCU |
| 19 | **R4** (1k ext) | (123, 101) | J2→R4 |
| 20 | **R2** (10k ext) | (120, 99) | divisor |
| 21 | **D2** (BAT54S ext) | (126, 102) | protección |
| 22 | **C6** (filtro ext) | (125, 98) | pegado al MCU |

### FASE E — Desacoplo y pasivos junto a su chip
| Orden | Comp | (X,Y) | Junto a |
|---|---|---|---|
| 23 | **C1,C3** | (114,82)(119,84) | entrada U2 |
| 24 | **C2,C4** | (122,84)(125,82) | salida U2 |
| 25 | **F1** (fusible) | (128, 78) | salida LDO |
| 26 | **C9** | (140, 88) | 3V3 de U1 |
| 27 | **C7,C8** | (159,95)(162,95) | VM de U3 |
| 28 | **C10** (100µF) | (177, 88) | bulk 48V, junto a J6 |
| 29 | **C11** (100nF) | (183, 88) | junto a C10 |
| 30 | **R5** (10k STBY) | (167, 100) | pull-up de U3 |
| 31 | **R6** (330R gate) | (176, 103) | pegado al Gate de Q1 |
| 32 | **R7** (10k pulldown) | (177, 107) | Gate→tierra, junto a Q1 |
| 33 | **D3** (flyback US1M) | (177, 112) | junto a J5 |

### FASE F — DIP: pull-ups y bypass (junto a SW1)
| Orden | Comp | (X,Y) |
|---|---|---|
| 34 | **R9,R10,R11** (pull-ups) | (134,111)(134,114)(134,117) |
| 35 | **C12,C13,C14** (bypass) | (130,111)(130,114)(130,117) |

### FASE G — LED, test points (al final)
| Orden | Comp | (X,Y) |
|---|---|---|
| 36 | **LED1** | (114, 120) |
| 37 | **R_LED1** | (118, 120) — junto a LED1 |
| 38 | **TP1,TP2,TP5** | (136,72)(140,72)(145,72) — borde sup |
| 39 | **TP6,TP7** | (120,88)(120,104) — antes de D1/D2 |
| 40 | **TP3** | (180, 91) — junto a bus 48V |
| 41 | **TP8** | (183, 103) — junto a Q1 |

---

## Después de colocar todo
1. Guarda (`Ctrl+S`) y avísame.
2. Yo: corro el **DRC** (cazo solapes de courtyard) + vuelvo a **verter las zonas de tierra** (AGND/PGND) sobre tu nuevo acomodo.
3. Ruteas siguiendo las líneas blancas (ancho automático). ✅
