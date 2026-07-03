# Guía Paso a Paso: Enrutado y Layout PCB - Jaguar MX
*Basado en la Fase 4 y normativas IPC-2152 / IPC-2221B*

Esta guía te ayudará a conectar cada componente de forma segura, respetando la separación de señales analógicas y de potencia.

## 1. Configuración de Pistas (Net Classes) en KiCad
Antes de rutear, configura los anchos en **Archivo → Configuración del Esquema → Clases de Red**:
* **Power_48V** (`+48V`, `NET_FAN_HS`): Ancho **1.5 mm**. Separación (Clearance) 0.6 mm. Vías: 0.8 mm (drill).
* **Power_5V** (`+5V`, `NET_AO1`, `NET_AO2`, `PGND`): Ancho **1.0 mm** (1.5 mm para el riel +5V). Clearance 0.3 mm.
* **Signal_Logic** (`+3V3`, señales lógicas/analógicas, `AGND`): Ancho **0.2 mm** (0.4 mm para `+3V3`). Clearance 0.15 mm.

---

## 2. Posicionamiento (Floorplanning)
Divide tu PCB (80x55 mm) en dos mitades (línea imaginaria en X = 40 mm):
* **Hemisferio Lógico (Izquierda):** Microcontrolador XIAO RP2350 (U1), LDO AP2112K (U2), conectores de sensores NTC (J1, J2), DIP Switch (SW4), filtros RC y diodos BAT54S.
* **Hemisferio de Potencia (Derecha):** MOSFET IRL520N (Q1 con su placa de disipación hacia afuera), conectores de 48V y Ventilador (J6, J8, J5), TB6612FNG (U3) y el conector del actuador (J3).

---

## 3. Enrutado de Potencia: Conmutación 48V (Prioridad #1)
*El lazo del ventilador genera los mayores picos inductivos. Debe ser lo más corto posible.*
1. **Entrada +48V:** Conecta `J6.Pin1` → condensadores `C10` y `C11` → `J5.Pin1`. Usa pista de **1.5 mm**, recta y corta.
2. **Diodo Flyback (D3):** Coloca el diodo US1M a menos de 5 mm del conector del ventilador (J5). Conecta su Cátodo a `J5.Pin1` (pista 1.5 mm).
3. **Conmutación MOSFET (`NET_FAN_HS`):** Conecta el Drain de `Q1` (pin central) → Ánodo de `D3` → `J5.Pin2`. Usa pista de **1.5 mm**.
4. **Retorno:** Desde el Source de `Q1` usa vías directas y gruesas hacia el plano `PGND`.

---

## 4. Enrutado de Potencia: Motores y 5V (Prioridad #2)
1. **Entrada 5V:** De `J7.Pin1` al LDO `U2` y a los pines `VM` del puente H `U3`. Usa pista de **1.5 mm**.
2. **Actuador (`NET_AO1` y `NET_AO2`):** Desde el TB6612FNG (`U3`) a `J3`. Une los pines duplicados del integrado con un pequeño relleno de cobre o pistas en paralelo, y luego tira una pista de **1.0 mm** hacia el conector `J3`.

---

## 5. Enrutado Analógico: NTCs (Extremadamente Sensible)
*Cualquier ruido aquí arruinará la medición de temperatura. Usa pista de **0.2 mm** solo en la capa superior (F.Cu), sin vías de ser posible.*
1. **Divisor:** Desde `J1/J2` tira una pista hacia las resistencias `R3` y `R4` (hasta 30 mm de largo es aceptable).
2. **Post-Filtro (El tramo intocable):** La ruta desde `R3` → `D1` (BAT54S) → `C5` → `U1.GP26` **NO debe superar los 10 mm**.
3. Ubica `D1`, `D2`, `C5` y `C6` literalmente **pegados** a los pines del XIAO RP2350. NUNCA del lado del conector de los sensores.
4. **Alejamiento:** Mantén al menos 2.0 mm de distancia respecto al MOSFET `Q1` y 1.0 mm respecto al TB6612FNG. Prohibido rutear estas pistas analógicas en paralelo a las pistas de los motores.

---

## 6. Enrutado Lógico: Control de MOSFET y Puente H
1. **Gate Resistor (R6):** Coloca la resistencia de 100Ω **pegada al pin Gate de Q1** (máximo 3 mm), NO cerca del microcontrolador ni del selector J9.
2. **Pull-Down (R7):** Coloca esta resistencia de 10kΩ conectando el Gate de `Q1` directamente a la tierra de potencia (`PGND`), muy cerca del MOSFET.
3. **Control Gate:** Tira una pista de **0.2 mm** (`NET_VENT_GATE`) desde `R6` hacia el selector `J9`.
4. **Puente H y DIP Switch:** Conecta las señales de control (AIN1, AIN2, MOTOR_EN, DIP Switch) usando pistas de **0.2 mm**.

---

## 7. Planos de Tierra (AGND y PGND) y Vías
1. **Zonas de Cobre:** Dibuja un polígono de relleno (Fill Zone) en la mitad izquierda, configúralo como **AGND** (ambas capas). Dibuja otro polígono en la mitad derecha, configúralo como **PGND** (ambas capas).
2. **Vías Térmicas (MOSFET Q1):** Debajo de la pestaña (tab) del MOSFET `Q1`, llena la zona con vías (0.4 mm drill / 0.8 mm pad) para transferir el calor de la capa superior a la inferior.
3. **Vías de Stitching (Cosido):** Reparte vías uniendo AGND (arriba) con AGND (abajo) cada 5 mm. Haz lo mismo para PGND cada 3 mm (densificando la cantidad debajo del puente H U3 para mejor conducción térmica).

---

## 8. El Toque Maestro: La Conexión Estrella (Net-Tie NT1)
*Tienes una separación física total entre la tierra analógica y la de potencia. Solo pueden unirse en un único lugar.*
1. Coloca el componente `NT1` (Net-Tie-2) exactamente en la frontera de las dos tierras (X = 40 mm, parte baja cerca de Y = 15 mm, donde retornan los 5V).
2. Conecta el pad izquierdo a la zona AGND y el pad derecho a la zona PGND. **Usa pistas cortas, gruesas y SIN vías.**
3. **Regla de Oro:** ¡Ninguna pista de cobre debe cruzar la frontera o el espacio vacío entre AGND y PGND, excepto a través de NT1!
