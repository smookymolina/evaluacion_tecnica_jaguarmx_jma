# INFORME FASE A — Revisión de Esquemático + Referencias de Layout
**Proyecto:** Jaguar MX — Extractor de aire caliente | **Fecha:** 2026-07-02
**Archivo revisado:** `kicad/PCB/PCB.kicad_sch` (netlist generada con kicad-cli 10.0; ERC = 0 errores)

> ⚠️ **VEREDICTO: PAUSAR ANTES DE FASE B.** Se encontraron **2 errores críticos** (E1, E2) que deben corregirse en el esquemático antes de iniciar el layout.

---

## Sección 1: Verificación de Esquemático

### Bloque 1 — Sensores NTC y DIP switch

| Ítem | Estado | Evidencia |
|---|---|---|
| Divisor 10kΩ+10kΩ ambos canales | ✅ CUMPLE | R1/R2 (10k 0.1%) a +3V3; NTC externa a AGND vía J1/J2 |
| Pull-ups DIP en GP6/GP7/GP0 | ✅ CUMPLE | R9/R10/R11 10k a +3V3 + C12–C14 100nF (debounce). SW1→D4(GP6), SW2→D5(GP7), SW3→D6(GP0) ✓ |
| Filtro RC 1kΩ + capacitor | ✅ CUMPLE | R3/R4 1k + C5/C6 100nF a AGND (fc ≈ 1.6 kHz) |
| Diodos BAT54S | ✅ CUMPLE | D1/D2 en clamp correcto: pin1→AGND, pin2→+3V3, pin3→señal filtrada |

### Bloque 2 — TB6612FNG

| Ítem | Estado | Evidencia |
|---|---|---|
| AIN1→GP2, AIN2→GP1 | ✅ CUMPLE | NET_AIN1→U1.9(D8=GP2)→U3.21; NET_AIN2→U1.8(D7=GP1)→U3.22 |
| MOTOR_EN→GP3 | ❌ **NO CUMPLE — CRÍTICO E1** | NET_MOTOR_EN conectado a U1.10 = **D9 = GP4** (debe ser D10=GP3). Está **intercambiado con VENT** |
| STBY en HIGH | ✅ CUMPLE | R5 10k a +3V3 (pull-up, mejor que tie directo) |
| Desacoplo VM y VCC | ✅ CUMPLE | VM: C7 47µF + C8 100nF; VCC: C9 100nF |
| TVS en entradas | ❌ NO CUMPLE | No existe ningún SMBJ3.3A en el esquemático (CLAUDE.md lo exige en GP26/GP27). Mitigación parcial: BAT54S |

**Bonus verificado correcto:** canal B deshabilitado (PWMB/BIN1/BIN2 a GND), salidas A en paralelo (pines 1-2 y 5-6), PGND1/2 (pines 3,4,9,10) a PGND y GND lógico (pin 18) a AGND — separación de retornos bien pensada.

### Bloque 3 — Etapa ventilador (MOSFET)

| Ítem | Estado | Evidencia |
|---|---|---|
| NMOS accionable a 3.3V | ✅ CUMPLE | Q1 IRL520N (TO-220) |
| Pull-down 10k en gate | ✅ CUMPLE | R7 a PGND |
| R serie en gate | ⚠️ CUMPLE c/desviación | R6 = **330Ω** (checklist pedía 100Ω). Aceptable; documentar. Footprint del símbolo se llama "10k_0402" para un valor 330R → confuso para BOM |
| Diodo flyback | ✅ CUMPLE (mejorado) | D3 = **US1M** (ultrafast, SMA) en vez de 1N4007; orientación correcta (K→+48V, A→drain) |
| 100µF + 100nF en +48V | ✅ CUMPLE | C10 100µF/63V + C11 100nF/63V |
| VENT→GP4 | ❌ **NO CUMPLE — CRÍTICO E1** | NET_VENT conectado a U1.11 = **D10 = GP3**. Intercambiado con MOTOR_EN |
| Driver de gate U4 | ❌ **CRÍTICO E2** | Pinout del símbolo custom TC4420 **no corresponde al DIP-8 real** |

**E2 detallado — TC4420 (Microchip DS21419, DIP-8 real):** 1,8=VDD · 2=IN · 3=NC · 4,5=VSS · 6,7=OUT.
El símbolo custom tiene: 1,2,4=GND · 3=IN · 5,7,8=VDD · 6=OUT. Con el footprint `DIP-8_W7.62mm` asignado esto produce: **+5V al pin 5 (VSS real) = cortocircuito +5V–GND**, señal IN al pin 3 (NC real) = entrada al aire, y pin 2 (IN real) clavado a GND. **Corregir el símbolo antes de FASE B.**

### Bloque 4 — Fuente de alimentación

| Ítem | Estado | Evidencia |
|---|---|---|
| LDO AP2112K-3.3 | ✅ CUMPLE | U2, EN atado a +5V (entrada por J7) |
| PPTC en salida del LDO | ✅ CUMPLE | F1 500mA (1812): LDO out → F1 → +3V3 |
| Desacoplo in/out | ✅ CUMPLE (eléctrico) | C1/C3 entrada, C2/C4 salida. Proximidad ≤3mm se verifica en FASE B |
| Alimentación del XIAO | ⚠️ OBSERVACIÓN | +3V3 se **retroalimenta al pin 3V3 del XIAO** (U1.12, salida del LDO interno); VBUS (pin 14) sin conectar. Si se conecta USB con alimentación externa, dos LDOs quedan en paralelo. Recomendación: alimentar VBUS desde +5V (idealmente con Schottky de ORing) o documentar la restricción "no conectar USB con fuente externa" |

### Bloque 5 — Tierras

| Ítem | Estado | Evidencia |
|---|---|---|
| Net-Tie AGND↔PGND | ✅ CUMPLE | NT1 (NetTie-2_SMD_Pad0.5mm), único punto de unión |
| Separación por zonas | ✅ CUMPLE (esquema) | AGND: XIAO, LDO, sensores, DIP, GND lógico TB6612. PGND: TB6612 potencia, Q1, U4, rail 48V. Partición física → FASE B |

**ERC (kicad-cli, severidad error): 0 violaciones.** Nota menor: kicad-cli advierte errores de anotación (numeración de referencias salta J4 y J8) — re-anotar en el editor, cosmético.

### Acciones recomendadas (orden)
1. **E1:** Intercambiar las nets de U1.10 y U1.11 → MOTOR_EN a D10 (GP3), VENT a D9 (GP4). Referencia: `datasheets/XIAO_RP2350.md` (D9=GPIO4, D10=GPIO3). El firmware ya está correcto; el error es del esquemático.
2. **E2:** Rehacer el símbolo `jaguar_power:TC4420` con el pinout real del DIP-8.
3. Agregar TVS SMBJ3.3A en GP26/GP27 (spec del proyecto) o documentar formalmente la desviación con BAT54S como protección alternativa.
4. Decidir estrategia de alimentación del XIAO (VBUS vs backfeed 3V3) y documentarla.
5. Corregir nombre de footprint de R6 y re-anotar referencias.

---

## Sección 2: Referencias de Layout (mixed-signal, 2 capas)

> Corrección de fuente: el "AN-95 de Analog Devices" citado en el prompt no existe con ese nombre. Las referencias reales de ADI son **MT-031**, **MT-101** y el artículo de Analog Dialogue sobre layout mixed-signal (abajo).

| # | Referencia | Tipo | Aporte clave para Jaguar |
|---|---|---|---|
| 1 | [SparkFun Dual TB6612FNG](https://github.com/sparkfun/Motor_Driver-Dual_TB6612FNG) (OSHW, Eagle, 2 capas) | Breakout mismo IC | Colocación de desacoplo VM pegado a pines 13/14/24, salidas de motor con pistas anchas y cortas, plano GND trasero continuo |
| 2 | [FanPico — tjko/fanpico](https://github.com/tjko/fanpico) (OSHW, KiCad, RP2040) | Controlador de ventiladores RP2040 | Partición conector-de-potencia-en-borde / MCU-al-centro; archivos KiCad completos para estudiar netclasses y zonas en FASE B |
| 3 | [Starfish — blog.thea.codes](https://blog.thea.codes/starfish-a-control-board-with-the-rp2040/) (RP2040 + drivers de motor) | Placa de control con motores | Flyback Schottky junto al conector del motor (lazo mínimo), separación señal/potencia documentada paso a paso |
| 4 | [MITAYI Pico RP2040 — CIRCUITSTATE](https://www.circuitstate.com/projects/mitayi-pico-rp2040-r0-2-open-source-microcontroller-development-board-schematic-pcb-and-assembly/) (KiCad, 2 capas) | Dev board RP2040 | Ruteo 2 capas con B.Cu como plano GND casi continuo; tratamiento de entradas ADC (pistas cortas en F.Cu) |
| 5 | [ADI MT-031](https://www.analog.com/media/en/training-seminars/tutorials/MT-031.pdf) + [Guía layout mixed-signal (Analog Dialogue)](https://www.analog.com/en/resources/analog-dialogue/articles/what-are-the-basic-guidelines-for-layout-design-of-mixed-signal-pcbs.html) | App notes ADI | **Plano de tierra único con partición por zonas y un solo punto de unión** (valida NT1); mantener retornos digitales fuera de la zona analógica; ADC tratado como componente analógico |

**Recomendaciones extraídas aplicables:**
- Un solo plano B.Cu particionado por corte (moat) con NT1 como puente único — exactamente la norma FASE4 (respaldo: MT-031).
- Lazo de freewheeling mínimo: D3 debe ir pegado al conector del ventilador **J6** (la norma FASE4 dice "J5", pero J5 es la entrada 48V y J6 es el fan — corregir en la norma) con retorno directo al source de Q1.
- Desacoplos a ≤3mm con vía a plano junto al pad (MT-101/práctica SparkFun).
- Pistas analógicas solo en F.Cu, sin vías, sobre zona AGND sin cruces digitales (MITAYI/Analog Dialogue).

---

## Sección 3: Plan para FASE B

| # | Elemento | Prioridad |
|---|---|---|
| 1 | Corregir E1 (swap MOTOR_EN/VENT en U1) y regenerar netlist | 🔴 CRÍTICO (bloqueo) |
| 2 | Corregir E2 (símbolo TC4420) y re-verificar con ERC + netlist | 🔴 CRÍTICO (bloqueo) |
| 3 | Partición 80×55mm: hemisferio lógico X 0–40 (AGND) / potencia X 40–80 (PGND), NT1 en X≈40, Y≈15 | 🔴 CRÍTICO |
| 4 | Lazo flyback: D3 a ≤5mm de **J6**, área <100mm², retorno directo a source de Q1 | 🔴 CRÍTICO |
| 5 | Netclasses/DRC: 48V 1.5mm/clearance 0.6mm; 5V 1.0–1.5mm; señal 0.2mm/0.15mm; vías 0.8/1.4 y 0.3/0.7 | 🔴 CRÍTICO |
| 6 | Rutas analógicas ≤10mm, solo F.Cu, sin vías, ≥0.5mm de cualquier nodo de conmutación | 🟡 IMPORTANTE |
| 7 | Desacoplos ≤3mm de pines (LDO, VM TB6612, VDD U4) con vía a plano junto al pad | 🟡 IMPORTANTE |
| 8 | Zonas GND B.Cu + via stitching en zona analógica; TVS SMBJ3.3A junto a J1/J2 (si se agregan) | 🟡 IMPORTANTE |
| 9 | Térmico: Q1 TO-220 con área de cobre en drain; pistas de motor A cortas hacia J3 | 🟢 ÓPTIMO |
| 10 | Testpoints accesibles en borde, 4 mounting holes, fiducials, silkscreen con polaridades | 🟢 ÓPTIMO |

**Estimado de tiempo en KiCad (layout completo):** 6–10 h → colocación por zonas 2h, ruteo potencia 1.5h, ruteo analógico/digital 1.5h, zonas + stitching 1h, DRC custom + iteraciones 1.5–3h, documentación 0.5–1h.
