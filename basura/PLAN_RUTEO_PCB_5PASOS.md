# Plan de Ruteo PCB en 5 Pasos — Extractor Jaguar MX

> **Objetivo:** completar el layout de `kicad/PCB/PCB.kicad_pcb` (KiCad 10).
> El PCB tiene los 53 footprints colocados y la netlist asignada, pero **cero cobre** (sin pistas, vías ni zonas).
> Cada paso es un **prompt autocontenido**: se puede pegar en una IA nueva (sin contexto previo) y ejecutar de forma independiente.
> Ejecutar **en orden** (cada paso asume que el anterior pasó su criterio de aceptación).

---

## Hechos base del proyecto (contexto común para TODOS los pasos)

- **Archivo:** `kicad/PCB/PCB.kicad_pcb` — KiCad 10, formato `(version 20260206)`.
- **Nets por nombre** (KiCad 10): las pistas/vías/zonas referencian la red como `(net "/NOMBRE")`, **sin número**. Ej: `(net "/+48V")`.
- **Placa:** 80 × 55 mm, 2 capas (F.Cu + B.Cu), FR4 1.6 mm, Cu 1 oz.
- **Origen absoluto (esquina sup-izq del contorno):** X=109.95, Y=69.84 mm. → `X_local = X_abs − 109.95`, `Y_local = Y_abs − 69.84`. (En KiCad Y crece hacia **abajo**.)
- **Frontera lógica/potencia:** X_abs ≈ 150 mm (X_local ≈ 40). Izquierda = analógico/lógico; derecha = potencia.
- **Herramienta de verificación (DRC headless):**
  ```bash
  "C:\Program Files\KiCad\10.0\bin\kicad-cli.exe" pcb drc --refill-zones --save-board \
      --format json --output drc.json kicad/PCB/PCB.kicad_pcb
  ```
  `--refill-zones --save-board` rellena las zonas y guarda; el JSON trae `violations` y `unconnected_items`.
- **Formato de una pista (segmento):**
  ```
  (segment (start X1 Y1) (end X2 Y2) (width W) (layer "F.Cu") (net "/NOMBRE") (uuid "..."))
  ```
- **Formato de una vía:**
  ```
  (via (at X Y) (size 0.7) (drill 0.3) (layers "F.Cu" "B.Cu") (net "/NOMBRE") (uuid "..."))
  ```
- **Anchos por clase de red (de FASE4, IPC-2152):** 48V/FAN_HS = **1.5 mm**; +5V/PGND = **1.0–1.5 mm**; motor AO1/AO2 = **1.0 mm**; +3V3 = **0.4 mm**; señales lógicas/analógicas = **0.2 mm**. Clearance mínimo global 0.2 mm (DRC "Default").
- **Método recomendado:** rutear en el **GUI de KiCad** (mucho más rápido y seguro que editar el `.kicad_pcb` a mano). Los prompts sirven igual para una IA que edite el archivo, pero **cada segmento debe validarse contra los pads vecinos** (clearance) o el DRC fallará.

> ⚠️ **Aviso importante (topología de tierra):** la netlist tiene pines de tierra "cruzados" respecto al floorplan (ver Paso 2). Resolver eso ANTES de rutear señales.

---

## PASO 1 — Corregir colocación (placement) y dejar DRC eléctrico en 0

**Prompt para IA:**

> Eres ingeniero de PCB. Abre `kicad/PCB/PCB.kicad_pcb` (KiCad 10). Los footprints están colocados pero hay **colisiones que producen cortos y solapes de courtyard**. Corrige SOLO posiciones de footprints (edita el `(at x y rot)` de nivel footprint, no los pads). Colisiones detectadas (coordenadas absolutas mm):
>
> 1. **CRÍTICO — corto:** `SW1` (DIP, columna derecha de pads en X≈127.57, Y 111–116) se solapa con las resistencias pull-up `R9`(126.95,110.84) `R10`(126.95,113.84) `R11`(126.95,116.84). Los pads se tocan → cortos +3V3/NET_SW2, AGND/+3V3, etc. **Mueve R9/R10/R11** a una zona libre a la derecha de los capacitores C12/C13/C14 (que están en X≈129.95), p.ej. X≈133.5, Y=110.84/113.84/116.84, rot 90.
> 2. `J1`(NTC) vs `R1`: separa R1 en Y (p.ej. a Y≈91.8) para que su courtyard no toque J1 ni R3.
> 3. `J2`(NTC) vs `R2`: R2 no cabe entre J2 y R4 en X; muévela en Y (p.ej. a Y≈98.2).
> 4. `F1` vs `J7`: aleja F1 de J7 (p.ej. X≈131.5).
> 5. `J9` vs `U4`(DNP) y `D3`: coloca J9 en el hueco entre U4 (borde der. X≈168.6) y D3 (borde izq. X≈173.4), p.ej. X≈170.7.
> 6. `C10`(100µF/48V) vs `Q1` y `J6`: coloca C10 a la izquierda de J6 y arriba de Q1, p.ej. X≈175.0, Y≈89.0.
>
> No muevas U1, U3, conectores de borde ni NT1. Tras editar, ejecuta el DRC (comando de "Hechos base").

**Criterio de aceptación:** en `drc.json`, **0 violaciones de tipo** `shorting_items`, `clearance`, `courtyards_overlap`, `pth_inside_courtyard`, `solder_mask_bridge`. (Quedan permitidos `silk_overlap`/`silk_over_copper` — son cosméticos, se ajustan al final.) `unconnected_items` seguirá ~117 (aún sin cobre) — normal.

---

## PASO 2 — Netclasses + planos de tierra AGND/PGND + resolver pines de tierra huérfanos

**Prompt para IA:**

> Eres ingeniero de PCB. En `kicad/PCB/PCB.kicad_pcb` (KiCad 10, nets por nombre) crea los **planos de tierra** y resuelve la topología de tierra.
>
> **A) Zonas (4 en total):** rectángulos rellenos, una por capa y por red:
> - `AGND` en `F.Cu` y en `B.Cu`: rectángulo X 110.5→149.45, Y 70.4→124.3.
> - `PGND` en `F.Cu` y en `B.Cu`: rectángulo X 150.45→189.4, Y 70.4→124.3.
> - Deja el hueco de aislamiento de ~1 mm entre X=149.45 y 150.45. El net-tie **NT1** (pads en 149.45 y 150.45, Y≈109.84) es el ÚNICO puente AGND↔PGND.
> - Parámetros de zona: `(hatch edge 0.5)`, `(connect_pads (clearance 0.25))`, `(min_thickness 0.25)`, `(fill yes (thermal_gap 0.3) (thermal_bridge_width 0.5))`.
>
> **B) Pines de tierra huérfanos** (quedan fuera de su plano por el floorplan; conéctalos con pista corta al plano correcto, o mejor al punto estrella NT1):
> - **AGND huérfanos** (en la mitad de potencia): `U3.15`(168.45,91.95) `U3.16`(168.45,91.31) `U3.17`(168.45,90.66) `U3.18`(168.45,90.00). Une los 4 con un strap y llévalos a AGND vía `NT1.1`(149.45,109.84) — pista 0.5 mm.
> - **PGND huérfanos** (en la mitad lógica): `J7.2`(125.88,75.19) `TP4.1`(144.95,72.84) `C15.2`(140.43,79.84). Conéctalos a PGND vía `NT1.2`(150.45,109.84) — pista 0.8 mm.
>
> **Nota de diseño a documentar:** estos huérfanos revelan que el esquemático asignó pines de tierra que no encajan con el floorplan (los pines "AGND" del TB6612 quedan en el borde de potencia; el retorno de J7 +5V quedó en la zona lógica). Alternativa válida y más limpia: **reasignar en el esquemático** U3.15-18 a PGND (son GND del driver, no analógico) y ubicar la entrada +5V (J7) en la mitad de potencia — evitaría los straps largos. Decidir y anotar en `ETISEJr_JairMolina.md`.
>
> Ejecuta el DRC con `--refill-zones --save-board`.

**Criterio de aceptación:** las zonas rellenan (se guardan `filled_polygon`); `unconnected_items` de **AGND y PGND = 0**; sin nuevas violaciones eléctricas. (`unconnected` total baja de ~117 a ~78 tras conectar los huérfanos.)

---

## PASO 3 — Ruteo de potencia (hemisferio derecho)

**Prompt para IA:**

> Eres ingeniero de PCB. Rutea las **redes de potencia** en `kicad/PCB/PCB.kicad_pcb`. Pads (coord. abs mm):
> - **`/+48V`** (ancho 1.5 mm, F.Cu, lazo corto): `J6.1`(183.95,82.58) `C11.1`(183.79,88.35) `C10.1`(175.0,89.0) `D3.1`(174.95,111.82) `J5.1`(177.52,118.36). Orden: J6→C11→C10→D3→J5 (bus recto, esquinas 45°). `TP3.1`(141.95,72.84) es un test point de 48V en la zona lógica: llévalo con pista fina 0.4 mm o reubícalo.
> - **`/NET_FAN_HS`** (1.5 mm): `Q1.2`(179.95,97.97) `D3.2`(178.95,111.82) `J5.2`(181.02,118.36). Q1(Drain)→D3(ánodo)→J5.2. **Minimiza el área** del lazo de freewheeling.
> - **`/NET_AO1`** (1.0 mm): `U3.1`(161.45,86.11) `U3.2`(161.45,86.75) → `J3.1`(155.95,118.34). Une los dos pads de U3 y baja a J3.
> - **`/NET_AO2`** (1.0 mm): `U3.5`(161.45,88.71) `U3.6`(161.45,89.36) → `J3.2`(159.45,118.34).
> - **`/+5V`** (1.0 mm; árbol): `J7.1`(122.38,75.19) `U2.1`(119.01,80.73) `U2.3`(119.01,82.63) `C1.1`(114.7,82.34) `C3.2`(119.23,84.33) `C15.1`(139.47,79.84) `TP2.1`(138.95,72.84) `C7.1`(159.0,95.5) `C8.1`(162.97,95.34) `U3.13/14`(168.45,92.6/93.26) `U3.24`(168.45,86.11) `U4.5/7/8`(167.57,111.46/106.38/103.84). Cruza la frontera por F.Cu; aprovecha B.Cu con vías donde estorbe el TB6612.
>
> Aproxima los pines de U3 (columnas en X 161.45 y 168.45) **por fuera** de la columna (nunca en diagonal cruzando la fila de pines) para no violar clearance. Valida cada segmento vs pads vecinos. Ejecuta DRC.

**Criterio de aceptación:** `unconnected_items` de `/+48V`, `/NET_FAN_HS`, `/NET_AO1`, `/NET_AO2`, `/+5V` = 0; **0** violaciones `clearance`/`shorting_items`.

---

## PASO 4 — Ruteo analógico NTC + señales de control

**Prompt para IA:**

> Eres ingeniero de PCB. Rutea señales sensibles y de control en `kicad/PCB/PCB.kicad_pcb`. **Todo en F.Cu, ancho 0.2 mm**, salvo indicación. Pads (abs mm):
>
> **Analógico NTC (regla de oro: tramo R→filtro→MCU ≤ 10 mm, sin vías):**
> - `/NET_TEMP_INT_DIV`: `J1.1`(114.44,88.03) `R1.2`(120.69,90.04) `R3.1`(≈122.35,88.84).
> - `/NET_TEMP_INT_FILT`: `R3.2`→`D1.3`(125.18,87.79)→`C5.2`→`U1.1`(129.71,87.22); `TP6.1`(120.0,87.54) va **antes** del BAT54S D1.
> - `/NET_TEMP_EXT_DIV`: `J2.2`(116.44,101.84) `R2.1`(120.69,98.2) `R4.1`(≈122.35,100.84).
> - `/NET_TEMP_EXT_FILT`: `R4.2`→`D2.3`(125.18,101.79)→`C6.1`→`U1.2`(129.71,89.76); `TP7.1`(120.0,104.0).
> - Mantén estas 4 redes **≥0.5 mm de cualquier pista de conmutación** y no las rutees en paralelo a los motores.
>
> **Control (cruzan la frontera U1→U3/U4; F.Cu, 0.2 mm):**
> - `/NET_AIN1`: `U1.9`(144.95,99.92) → `U3.21`(168.45,88.06).
> - `/NET_AIN2`: `U1.8`(144.95,102.46) → `U3.22`(168.45,87.41).
> - `/NET_MOTOR_EN`: `U1.11`(144.95,94.84) → `U3.23`(168.45,86.75).
> - `/NET_STBY`: `R5.2`(166.95,100.33) → `U3.19`(168.45,89.36) (aproxima U3.19 por la derecha, X>168.6).
> - `/NET_VENT`: `U1.10`(144.95,97.38) → `U4.3`(159.95,108.92) → `J9.1`(170.7,110.84).
>
> **DIP switch (F.Cu, 0.2 mm):**
> - `/NET_SW1`: `SW1.1`(119.95,111.19) `U1.5`(129.71,97.38) `C12.1`(≈129.95,110.34) `R9.1`(133.5,111.35).
> - `/NET_SW2`: `SW1.5`(127.57,113.73) `U1.6`(129.71,99.92) `C13.1`(129.95,113.34) `R10.1`(133.5,114.35).
> - `/NET_SW3`: `SW1.3`(119.95,116.27) `U1.7`(129.71,102.46) `C14.1`(129.95,116.34) `R11.1`(133.5,117.35).
>   *(Ajusta R9/10/11 a la posición real que dejó el Paso 1.)*
>
> Ejecuta DRC.

**Criterio de aceptación:** `unconnected_items` de las 12 redes anteriores = 0; **0** violaciones eléctricas; verificar en GUI que ningún tramo FILT analógico corra en paralelo a NET_VENT/motor >5 mm.

---

## PASO 5 — Redes restantes + via stitching + DRC final + fabricación

**Prompt para IA:**

> Eres ingeniero de PCB. Cierra el layout de `kicad/PCB/PCB.kicad_pcb`.
>
> **A) Redes restantes:**
> - `/+3V3` (0.4 mm, árbol): `F1.2`(131.5,76.5) `R1.1`(120.04,91.8) `R2.2`(121.69,98.2) `D1.2`(125.18,89.79) `D2.2`(125.18,101.79) `R9.2/R10.2/R11.2`(133.5,110.33/113.33/116.33) `C9.2`(144.43,84.84) `U1.12`(144.95,92.3) `R5.1`(166.95,101.35) `R_LED1.1`(170.4,100.84) `U3.20`(168.45,88.71) `TP1.1`(135.95,72.84).
> - `/NET_3V3_LDO` (0.4 mm): `U2.5`(121.61,80.73) `F1.1`(131.5,80.78) `C2.1`(121.7,84.85) `C4.1`(125.27,82.54).
> - `/NET_VENT_GATE` (0.2 mm): `R6.1`(174.94,102.84) → `J9.2`(170.7,113.38).
> - `/NET_VENT_DRV` (0.2 mm): `U4.6`(167.57,108.92) → `J9.3`(170.7,115.92).
> - `/NET_Q1_GATE` (0.2 mm): `Q1.1`(179.95,100.51) `R6.2`(175.96,102.84) `R7.2`(177.45,106.67); `TP8.1`(135.95,75.84) está lejos (zona lógica) — llévalo fino o reubícalo.
> - `/NET_LED_ANODE` (0.2 mm): `R_LED1.2`(171.42,100.84) → `LED1.2`(122.32,120.34). **Red muy larga y cruzada**: idealmente reubicar LED1/R_LED1 juntos antes de rutear.
>
> **B) Via stitching:** vías `(size 0.7)(drill 0.3)` en rejilla ~5 mm cosiendo AGND(F)↔AGND(B) en la mitad lógica, y ~3 mm cosiendo PGND en la mitad de potencia (densa bajo U3 y bajo el tab de Q1 para disipación). Evita ponerlas bajo U1 o bajo pistas analógicas.
>
> **C) Cierre:** `Fill All Zones`, corrige `silk_overlap` (mueve referencias), ejecuta DRC final.

**Criterio de aceptación:** `unconnected_items = 0`; `violations = 0` (o solo advertencias de silk justificadas). Exportar Gerbers + drill para verificación final.

---

## Tablero de progreso (marcar al cerrar cada paso)

| Paso | Descripción | DRC esperado | Estado |
|------|-------------|--------------|--------|
| 1 | Placement sin colisiones | 0 viol. eléctricas | ☐ |
| 2 | Zonas AGND/PGND + huérfanos | AGND/PGND unconnected = 0 | ☐ |
| 3 | Potencia (48V/5V/motor) | 5 redes unconnected = 0 | ☐ |
| 4 | NTC + control + DIP | 12 redes unconnected = 0 | ☐ |
| 5 | Resto + stitching + final | unconnected = 0, viol = 0 | ☐ |

> **Antes de empezar cada paso**, haz una copia: `cp kicad/PCB/PCB.kicad_pcb kicad/PCB/PCB_pasoN.bak`.
> Así puedes revertir sin depender de git.
