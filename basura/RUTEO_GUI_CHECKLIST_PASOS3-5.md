# Checklist de Ruteo Interactivo (Pasos 3-5) — Jaguar MX

> Complemento de `PLAN_RUTEO_PCB_5PASOS.md`. Pasos 1-2 ya aplicados y verificados (placement + planos AGND/PGND, DRC eléctrico = 0).
> Faltan **74 conexiones** (redes de potencia y señal). Estas se rutean **a mano en el editor de PCB de KiCad** con el router interactivo — es rápido (~30-45 min) y queda 100% limpio.
> Coordenadas = **absolutas en mm** del archivo actual (post-Paso 2). `·TH` = pad pasante (existe en ambas capas); sin marca = SMD (solo F.Cu).

---

## Cómo rutear (flujo recomendado en KiCad 10)

1. **Define Net Classes** (Archivo → Configuración de la placa → Net Classes) con los anchos de `PLAN_RUTEO` (48V 1.5 / 5V 1.0 / motor 1.0 / 3V3 0.4 / señal 0.2). Así el router usa el ancho correcto automáticamente.
2. **Router interactivo:** tecla `X`, clic en un pad, sigue el ratsnest. Con "Highlight Collisions / Shove" activo (Preferencias → PCB Editor → Interactive Router → *Walk around* o *Shove*), KiCad esquiva pads solo.
3. **Orden:** primero potencia (Paso 3), luego analógico NTC (Paso 4, lo más delicado), luego control/DIP, y al final rellenos de +3V3/resto (Paso 5).
4. Tras cada red: `B` (rellenar zonas) y DRC. Comando headless equivalente:
   `"C:\Program Files\KiCad\10.0\bin\kicad-cli.exe" pcb drc --refill-zones --save-board --format json --output drc.json kicad/PCB/PCB.kicad_pcb`

### Técnicas clave
- **Strap entre pines adyacentes** (marcado ⚠): une los 2 pads del mismo net con un segmento corto de 0.3-0.4 mm *a lo largo* de la columna; no lo hagas con el ancho de potencia (choca con el pin vecino).
- **Escape de pin de IC (U2/U3 paso 0.65 mm):** sal del pad **perpendicular a la fila**, aléjate ~1 mm de la columna, y recién ahí ensancha/gira. Nunca cruces en diagonal por delante de la fila de pines.
- **Cruce de frontera AGND/PGND (X≈150):** las señales de control **sí** pueden cruzar por F.Cu (retorno lento, no crítico). Mantén el cruce perpendicular y corto. **No** cruces las 4 pistas NTC_FILT.

---

## ✅ 3 componentes reubicados (ya hecho — DRC eléctrico = 0)

Se movieron para eliminar pistas larguísimas innecesarias (anótalo en `ETISEJr_JairMolina.md`):

| Componente | Antes | Ahora | Mejora |
|---|---|---|---|
| `TP3` (test 48V) | (141.9,72.8) zona lógica | **(180.5,90.5)** junto al bus 48V | 37 mm → ~4 mm |
| `TP8` (test Q1_GATE) | (135.9,75.8) zona lógica | **(183.0,103.0)** junto a Q1 | 48 mm → ~4 mm |
| `R_LED1` (a LED1) | (171.4,100.8) zona potencia | **(126.5,120.3)** junto a LED1 | LED_ANODE 53 mm → ~4 mm |

---

## POTENCIA (Paso 3)

### `/NET_AO1`  — ancho **1.0 mm**
- **Pads:** `J3.1`(155.9,118.3·TH), `U3.1`(161.4,86.1), `U3.2`(161.4,86.8)
- **Segmentos (MST):** J3.1→U3.2 (32mm); U3.2→U3.1 (1mm)
- ⚠ U3.2↔U3.1: strap corto entre pines adyacentes

### `/NET_AO2`  — ancho **1.0 mm**
- **Pads:** `J3.2`(159.4,118.3·TH), `U3.5`(161.4,88.7), `U3.6`(161.4,89.4)
- **Segmentos (MST):** J3.2→U3.6 (29mm); U3.6→U3.5 (1mm)
- ⚠ U3.6↔U3.5: strap corto entre pines adyacentes

### `/NET_FAN_HS`  — ancho **1.5 mm**
- **Pads:** `Q1.2`(179.9,98.0·TH), `D3.2`(178.9,111.8), `J5.2`(181.0,118.4·TH)
- **Segmentos (MST):** Q1.2→D3.2 (14mm); D3.2→J5.2 (7mm)

### `/+48V`  — ancho **1.5 mm**
- **Pads:** `J6.1`(183.9,82.6·TH), `C11.1`(183.8,88.3), `TP3.1`(180.5,90.5), `C10.1`(175.0,89.0·TH), `D3.1`(174.9,111.8), `J5.1`(177.5,118.4·TH)
- **Segmentos (MST):** J6.1→C11.1 (6mm); C11.1→TP3.1 (4mm); C11.1→C10.1 (9mm); C10.1→D3.1 (23mm); D3.1→J5.1 (7mm)
- ⚠ cruza frontera AGND/PGND (X≈150) — ok en señal, minimizar

### `/+5V`  — ancho **1.0 mm**
- **Pads:** `C1.1`(114.7,82.3), `C3.2`(119.2,84.3), `C7.1`(159.0,95.5), `TP2.1`(138.9,72.8), `J7.1`(122.4,75.2·TH), `C8.1`(163.0,95.3), `U2.1`(119.0,80.7), `U2.3`(119.0,82.6), `U4.5`(167.6,111.5·TH), `U4.7`(167.6,106.4·TH), `U4.8`(167.6,103.8·TH), `U3.13`(168.4,93.3), `U3.14`(168.4,92.6), `U3.24`(168.4,86.1), `C15.1`(139.5,79.8)
- **Segmentos (MST):** C1.1→U2.3 (4mm); U2.3→C3.2 (2mm); U2.3→U2.1 (2mm); U2.1→J7.1 (6mm); J7.1→TP2.1 (17mm); TP2.1→C15.1 (7mm); C15.1→C7.1 (25mm); C7.1→C8.1 (4mm); C8.1→U3.13 (6mm); U3.13→U3.14 (1mm); U3.14→U3.24 (6mm); C8.1→U4.8 (10mm); U4.8→U4.7 (3mm); U4.7→U4.5 (5mm)
- ⚠ U3.13↔U3.14: strap corto entre pines adyacentes; cruza frontera AGND/PGND (X≈150) — ok en señal, minimizar


## ANALOGICO NTC (Paso 4)

### `/NET_TEMP_INT_DIV`  — ancho **0.2 mm**
- **Pads:** `J1.1`(114.4,88.0·TH), `R1.2`(121.7,91.8), `R3.1`(122.3,88.9)
- **Segmentos (MST):** J1.1→R3.1 (8mm); R3.1→R1.2 (3mm)

### `/NET_TEMP_INT_FILT`  — ancho **0.2 mm**
- **Pads:** `D1.3`(127.1,88.8), `C5.2`(126.1,91.8), `U1.1`(129.7,87.2·TH), `TP6.1`(119.9,87.6), `R3.2`(123.3,88.9)
- **Segmentos (MST):** D1.3→U1.1 (3mm); D1.3→C5.2 (3mm); D1.3→R3.2 (4mm); R3.2→TP6.1 (4mm)

### `/NET_TEMP_EXT_DIV`  — ancho **0.2 mm**
- **Pads:** `J2.2`(116.4,101.8·TH), `R4.1`(122.3,100.8), `R2.1`(120.0,98.2)
- **Segmentos (MST):** J2.2→R2.1 (5mm); R2.1→R4.1 (3mm)

### `/NET_TEMP_EXT_FILT`  — ancho **0.2 mm**
- **Pads:** `TP7.1`(120.0,103.8), `U1.2`(129.7,89.8·TH), `D2.3`(127.1,100.8), `R4.2`(123.3,100.8), `C6.1`(125.5,97.8)
- **Segmentos (MST):** TP7.1→R4.2 (4mm); R4.2→C6.1 (4mm); C6.1→D2.3 (3mm); C6.1→U1.2 (9mm)


## CONTROL + DIP (Paso 4)

### `/NET_AIN1`  — ancho **0.2 mm**
- **Pads:** `U1.9`(144.9,99.9·TH), `U3.21`(168.4,88.1)
- **Segmentos (MST):** U1.9→U3.21 (26mm)
- ⚠ cruza frontera AGND/PGND (X≈150) — ok en señal, minimizar

### `/NET_AIN2`  — ancho **0.2 mm**
- **Pads:** `U1.8`(144.9,102.5·TH), `U3.22`(168.4,87.4)
- **Segmentos (MST):** U1.8→U3.22 (28mm)
- ⚠ cruza frontera AGND/PGND (X≈150) — ok en señal, minimizar

### `/NET_MOTOR_EN`  — ancho **0.2 mm**
- **Pads:** `U1.11`(144.9,94.8·TH), `U3.23`(168.4,86.8)
- **Segmentos (MST):** U1.11→U3.23 (25mm)
- ⚠ cruza frontera AGND/PGND (X≈150) — ok en señal, minimizar

### `/NET_STBY`  — ancho **0.2 mm**
- **Pads:** `R5.2`(166.9,100.3), `U3.19`(168.4,89.4)
- **Segmentos (MST):** R5.2→U3.19 (11mm)

### `/NET_VENT`  — ancho **0.2 mm**
- **Pads:** `U1.10`(144.9,97.4·TH), `J9.1`(170.7,110.8·TH), `U4.3`(159.9,108.9·TH)
- **Segmentos (MST):** U1.10→U4.3 (19mm); U4.3→J9.1 (11mm)
- ⚠ cruza frontera AGND/PGND (X≈150) — ok en señal, minimizar

### `/NET_SW1`  — ancho **0.2 mm**
- **Pads:** `SW1.1`(120.0,111.2·TH), `U1.5`(129.7,97.4·TH), `C12.1`(129.9,111.3), `R9.1`(133.5,111.3)
- **Segmentos (MST):** SW1.1→C12.1 (10mm); C12.1→R9.1 (4mm); C12.1→U1.5 (14mm)

### `/NET_SW2`  — ancho **0.2 mm**
- **Pads:** `R10.1`(133.5,114.3), `SW1.5`(127.6,113.7·TH), `U1.6`(129.7,99.9·TH), `C13.1`(129.9,114.3)
- **Segmentos (MST):** R10.1→C13.1 (4mm); C13.1→SW1.5 (2mm); SW1.5→U1.6 (14mm)

### `/NET_SW3`  — ancho **0.2 mm**
- **Pads:** `SW1.3`(120.0,116.3·TH), `U1.7`(129.7,102.5·TH), `C14.1`(129.9,117.3), `R11.1`(133.5,117.3)
- **Segmentos (MST):** SW1.3→C14.1 (10mm); C14.1→R11.1 (4mm); C14.1→U1.7 (15mm)


## RESTO (Paso 5)

### `/+3V3`  — ancho **0.4 mm**
- **Pads:** `R10.2`(133.5,113.3), `R1.1`(120.0,91.8), `D1.2`(125.2,89.8), `R5.1`(166.9,101.4), `C9.2`(144.4,84.8), `U1.12`(144.9,92.3·TH), `R_LED1.1`(125.5,120.3), `F1.2`(131.5,76.5), `R9.2`(133.5,110.3), `D2.2`(125.2,101.8), `R2.2`(121.7,98.2), `R11.2`(133.5,116.3), `TP1.1`(135.9,72.8), `U3.20`(168.4,88.7)
- **Segmentos (MST):** R10.2→R9.2 (3mm); R10.2→R11.2 (3mm); R11.2→R_LED1.1 (9mm); R9.2→D2.2 (12mm); D2.2→R2.2 (5mm); R2.2→R1.1 (7mm); R1.1→D1.2 (6mm); D1.2→F1.2 (15mm); F1.2→TP1.1 (6mm); TP1.1→C9.2 (15mm); C9.2→U1.12 (7mm); U1.12→U3.20 (24mm); U3.20→R5.1 (13mm)
- ⚠ cruza frontera AGND/PGND (X≈150) — ok en señal, minimizar

### `/NET_3V3_LDO`  — ancho **0.4 mm**
- **Pads:** `F1.1`(131.5,80.8), `C4.1`(125.3,82.5), `U2.5`(121.6,80.7), `C2.1`(121.7,84.8)
- **Segmentos (MST):** F1.1→C4.1 (6mm); C4.1→U2.5 (4mm); U2.5→C2.1 (4mm)

### `/NET_VENT_GATE`  — ancho **0.2 mm**
- **Pads:** `J9.2`(170.7,113.4·TH), `R6.1`(174.9,102.8)
- **Segmentos (MST):** J9.2→R6.1 (11mm)

### `/NET_VENT_DRV`  — ancho **0.2 mm**
- **Pads:** `J9.3`(170.7,115.9·TH), `U4.6`(167.6,108.9·TH)
- **Segmentos (MST):** J9.3→U4.6 (8mm)

### `/NET_Q1_GATE`  — ancho **0.2 mm**
- **Pads:** `R6.2`(176.0,102.8), `Q1.1`(179.9,100.5·TH), `TP8.1`(183.0,103.0), `R7.2`(177.4,106.7)
- **Segmentos (MST):** R6.2→R7.2 (4mm); R6.2→Q1.1 (5mm); Q1.1→TP8.1 (4mm)

### `/NET_LED_ANODE`  — ancho **0.2 mm**
- **Pads:** `R_LED1.2`(126.5,120.3), `LED1.2`(122.3,120.3)
- **Segmentos (MST):** R_LED1.2→LED1.2 (4mm)

---

## Paso 5 — Cierre (tras rutear todo)

1. **Via stitching:** vías `(size 0.7)(drill 0.3)` cosiendo AGND(F)↔AGND(B) cada ~5 mm en la mitad lógica, y PGND cada ~3 mm en la mitad de potencia (densas bajo U3 y bajo el tab de Q1 para disipación). Evita ponerlas bajo U1 o bajo pistas NTC.
2. `B` → **Rellenar todas las zonas**.
3. **Silk:** corrige los `silk_overlap` (mueve las referencias que se encimen).
4. **DRC final:** debe quedar `unconnected = 0` y `violations = 0` (o solo silk justificado).
5. **Fabricación:** Archivo → Fabricación → Gerbers + archivo de taladros. Verifica en el visor de Gerbers.

---

## Tablero
| Red | Segmentos | ✓ |
|---|---|---|
| Potencia (5 redes) | 48V, FAN_HS, AO1, AO2, +5V | ☐ |
| NTC (4 redes) | INT/EXT DIV+FILT | ☐ |
| Control+DIP (8 redes) | AIN1/2, MOTOR_EN, STBY, VENT, SW1/2/3 | ☐ |
| Resto (6 redes) | +3V3, 3V3_LDO, VENT_GATE/DRV, Q1_GATE, LED | ☐ |
| Stitching + DRC final | — | ☐ |

