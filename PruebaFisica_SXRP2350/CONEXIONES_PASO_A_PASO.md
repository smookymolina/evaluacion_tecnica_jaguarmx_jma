# Guía de Conexiones Paso a Paso — Prueba Física XIAO RP2350

Sistema de extracción de aire caliente — Jaguar de México
Aplica tanto al firmware físico (`src/`) como al simulador (`SimuladorTermico/`); ambos usan el mismo mapa de pines.

---

## 0. Material necesario

| Cant. | Componente | Notas |
| :--- | :--- | :--- |
| 1 | Seeed Studio XIAO RP2350 | MCU, alimentado por USB-C |
| 2 | NTC TEWA TT05-10KC8-1S-T105-1500 | 10 kΩ @ 25 °C, Beta 3435 K |
| 2 | Resistencia 10 kΩ (1 % recomendado) | Parte alta del divisor de cada NTC |
| 1 | Módulo TB6612FNG | Puente H, canal A |
| 1 | Actuador lineal FIT0803 (5 V) | Compuertas; fin de carrera interno |
| 1 | Ventilador MR1238E48B-FSR (48 V) | Etapa de potencia aislada |
| 1 | MOSFET NMOS *logic-level* | Debe saturar con Vgs = 3.3 V (ej. IRLZ44N, AO3400 según corriente) |
| 1 | Diodo flyback (ej. 1N5819/SS34) | En paralelo con el ventilador |
| 1 | Resistencia 100 Ω | En serie al gate del MOSFET |
| 1 | Resistencia 10 kΩ | Pull-down gate → GND |
| 1 | DIP switch de 3 posiciones | Selección de setpoint |
| 1 | Fuente 5 V | VM del TB6612FNG / actuador |
| 1 | Fuente 48 V | Ventilador |
| — | Protoboard/borneras, cables, multímetro | — |

**Regla general: todo el cableado se hace SIN energizar. Las fuentes se conectan hasta el paso 7.**

---

## 1. Referencia de pines del XIAO RP2350

Vista superior, con el conector USB-C hacia arriba:

```
                 ┌──── USB-C ────┐
   (GPIO26)  D0 ─┤1            14├─ 5V
   (GPIO27)  D1 ─┤2            13├─ GND
   (GPIO28)  D2 ─┤3            12├─ 3V3
   (GPIO5)   D3 ─┤4            11├─ D10 (GPIO3)
   (GPIO6)   D4 ─┤5            10├─ D9  (GPIO4)
   (GPIO7)   D5 ─┤6             9├─ D8  (GPIO2)
   (GPIO0)   D6 ─┤7             8├─ D7  (GPIO1)
                 └───────────────┘
```

| Señal del proyecto | GPIO | Serigrafía XIAO |
| :--- | :--- | :--- |
| TEMP_INT (NTC 1) | GPIO26 | A0 / D0 |
| TEMP_EXT (NTC 2) | GPIO27 | A1 / D1 |
| SW1 (DIP bit 0, LSB) | GPIO6 | D4 |
| SW2 (DIP bit 1) | GPIO7 | D5 |
| SW3 (DIP bit 2, MSB) | GPIO0 | D6 |
| AIN2 (TB6612FNG) | GPIO1 | D7 |
| AIN1 (TB6612FNG) | GPIO2 | D8 |
| VENT (gate MOSFET) | GPIO4 | D9 |
| MOTOR_EN (PWMA) | GPIO3 | D10 |

> Advertencia: en el XIAO la serigrafía NO es el número de GPIO (D9 = GPIO4, D10 = GPIO3). Cablear siempre por esta tabla, no por intuición del Pico.

---

## 2. Paso 1 — Tierras comunes

Unir en un solo nodo de GND:

1. GND del XIAO (pin 13).
2. GND del módulo TB6612FNG (ambos GND si el módulo trae dos).
3. Negativo de la fuente de 5 V.
4. Negativo de la fuente de 48 V.
5. Source del MOSFET y extremo inferior de los divisores NTC y del DIP switch.

Sin tierra común entre la etapa de 48 V y el MCU, el MOSFET no conmuta y las lecturas ADC flotan. Este es el error de cableado más común.

---

## 3. Paso 2 — Sensores NTC (divisores resistivos)

Cada NTC forma un divisor con su resistencia de 10 kΩ. **La resistencia va arriba (a 3V3) y el NTC abajo (a GND)** — el firmware asume esta topología:

```
3V3 (pin 12) ──[ 10 kΩ ]──●── nodo ADC ──> D0 (NTC interno) / D1 (NTC externo)
                          │
                        [ NTC ]
                          │
                         GND
```

1. NTC interno (dentro del gabinete): nodo → **D0** (GPIO26/ADC0).
2. NTC externo (aire ambiente): nodo → **D1** (GPIO27/ADC1).
3. Alimentar ambos divisores desde el **3V3 del XIAO** (pin 12), nunca desde 5 V: el ADC del RP2350 tolera máximo 3.3 V.
4. Cables del NTC lo más cortos posible y alejados del cableado del motor/ventilador (EMI).

**Verificación (con USB conectado, fuentes de potencia apagadas):** a ~25 °C ambiente cada nodo debe medir ≈ 1.65 V (mitad de 3.3 V, porque NTC ≈ 10 kΩ @ 25 °C). Si mide cerca de 3.3 V el NTC está desconectado; cerca de 0 V, en corto o el divisor está invertido.

---

## 4. Paso 3 — DIP switch (setpoint)

Cada polo del DIP conmuta su GPIO a GND (el firmware activa pull-ups internos; no se requieren resistencias externas):

```
D4 (GPIO6)  ──o/ o── GND     SW1 (bit 0, LSB)
D5 (GPIO7)  ──o/ o── GND     SW2 (bit 1)
D6 (GPIO0)  ──o/ o── GND     SW3 (bit 2, MSB)
```

Lógica: switch **ON (cerrado a GND) = bit 1**. Tabla de setpoints:

| SW3 | SW2 | SW1 | Setpoint |
| :-: | :-: | :-: | :--- |
| 0 | 0 | 0 | 40 °C |
| 0 | 0 | 1 | 45 °C |
| 0 | 1 | 0 | 50 °C |
| 0 | 1 | 1 | 55 °C |
| 1 | 0 | 0 | 60 °C |
| 1 | 0 | 1 | 65 °C |
| 1 | 1 | 0 | 70 °C |
| 1 | 1 | 1 | 75 °C |

**Verificación:** con el firmware corriendo, mover cada switch y confirmar en la telemetría que `SP=` cambia según la tabla.

---

## 5. Paso 4 — TB6612FNG + actuador FIT0803

Conexiones del módulo:

| Pin TB6612FNG | Conectar a | Notas |
| :--- | :--- | :--- |
| VM | +5 V (fuente de potencia) | Alimenta el motor del FIT0803 |
| VCC | 3V3 del XIAO (pin 12) | Lógica del driver |
| GND | Nodo común de GND | — |
| AIN1 | **D8** (GPIO2) | Dirección 1 |
| AIN2 | **D7** (GPIO1) | Dirección 2 |
| PWMA | **D10** (GPIO3) | MOTOR_EN — habilitación canal A |
| **STBY** | **3V3** | **Crítico: si queda flotante o a GND el motor NUNCA se mueve** |
| AO1 | Cable 1 del FIT0803 | — |
| AO2 | Cable 2 del FIT0803 | — |

Convención de dirección del firmware: `AIN1=0, AIN2=1` extiende (abre compuertas); `AIN1=1, AIN2=0` retrae (cierra). Si en la primera prueba el actuador se mueve al revés, **intercambiar AO1↔AO2** (no tocar el firmware).

El FIT0803 tiene fin de carrera interno: el firmware energiza 3 s por travel (recorrido real ~1.7 s) y el margen extra es seguro.

**Verificación:** antes de conectar el actuador, con el firmware en COOLING medir AO1/AO2: debe aparecer ~5 V entre ellos durante los 3 s del travel y 0 V al terminar.

---

## 6. Paso 5 — Ventilador 48 V (etapa MOSFET)

Configuración low-side (MOSFET entre el ventilador y GND):

```
+48 V ────────●──────────── cable rojo (+) del ventilador
              │
          [ diodo ]  ← flyback: cátodo (franja) a +48 V
              │
              ●──────────── cable negro (−) del ventilador
              │
            Drain
D9 ──[100Ω]── Gate   MOSFET NMOS (logic-level)
              │
           [10 kΩ]   ← pull-down gate→GND
              │
            Source ── GND común
```

1. Source del MOSFET → GND común.
2. Drain → negativo del ventilador; positivo del ventilador → +48 V.
3. Diodo flyback en paralelo con el ventilador: cátodo a +48 V, ánodo al drain. Sin él, el pico inductivo al apagar puede destruir el MOSFET.
4. Gate ← **D9** (GPIO4) a través de 100 Ω.
5. Pull-down de 10 kΩ de gate a GND: durante reset/bootloader el GPIO queda en alta impedancia y sin pull-down el ventilador puede arrancar solo.
6. El MOSFET debe ser *logic-level* (especificado para Vgs = 3.3 V, no solo Vgs(th) < 3.3 V). Un MOSFET estándar de 10 V de gate conmutará a medias y se calentará.

**Verificación (fuente de 48 V apagada):** con el firmware en COOLING, medir gate: 3.3 V con ventilador comandado ON, 0 V en OFF.

---

## 7. Paso 6 — Alimentación del XIAO

El XIAO se alimenta únicamente por **USB-C** desde la laptop (que además da el monitor Serial). No conectar 5 V externos al pin 14 mientras el USB esté conectado.

---

## 8. Paso 7 — Secuencia de energizado (en este orden)

1. **Revisión final en frío:** continuidad de GND común entre XIAO, TB6612FNG, source del MOSFET y ambas fuentes; ausencia de corto entre +48 V y GND, y entre +5 V y GND.
2. **USB al XIAO.** Abrir el monitor Serial (115200). Verificar banner, telemetría a 1 Hz y lecturas NTC coherentes con el ambiente (±2 °C). Probar el DIP.
3. **Fuente de 5 V** (TB6612FNG/actuador). Forzar un ciclo (`TEMP:62` con `SET:55`, o calentando el NTC interno) y verificar apertura/cierre de compuertas.
4. **Fuente de 48 V** (ventilador), al final y solo si los pasos anteriores pasaron. Verificar que el ventilador arranca al completarse la apertura de compuertas y se apaga al entrar a IDLE.

Para el apagado, orden inverso: 48 V → 5 V → USB.

---

## 9. Prueba de humo recomendada (sin sensores ni cargas)

Si se quiere validar la lógica antes de cablear todo, cargar primero el firmware de `SimuladorTermico/`: no necesita NTC (temperaturas simuladas internamente) y ejercita las salidas reales del puente H y del MOSFET. Con eso se verifica placa, cableado de salidas y secuencia FSM completa (COOLING → IDLE → ERROR/LOCKOUT vía `FALLA:INT`) antes de tocar la parte analógica.
