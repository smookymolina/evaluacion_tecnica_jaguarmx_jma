# IRL520N — MOSFET NMOS de Potencia (Infineon / IR)

**Función en el sistema:** Switch de potencia para el ventilador MR1238E48B-FSR (48V DC)

---

## ¿Por qué NMOS y no PMOS?

En este diseño el GPIO3.3V controla el gate del NMOS:
- GPIO=HIGH → MOSFET ON → ventilador encendido
- GPIO=LOW  → MOSFET OFF → ventilador apagado

El IRL520N tiene Vgs(th) = 1.0–2.0 V (típico 1.3V), accionable directamente por GPIO 3.3V.
La resistencia pull-down de 10kΩ en el gate garantiza apagado si el GPIO queda flotante.

---

## Parámetros eléctricos clave

| Parámetro | Símbolo | Valor | Condición |
|---|---|---|---|
| Max drain-source voltage | VDSS | **100 V** | |
| Max drain current (continua) | ID | **10 A** | @ TC = 25°C |
| Max drain current (pulsada) | IDM | 40 A | |
| Gate threshold voltage | Vgs(th) | 1.0 – 2.0 V | ID=250µA; **compatible 3.3V GPIO** |
| On-state drain-source resistance | RDS(on) | **0.18 Ω** | @ VGS=10V, ID=5A |
| Disipación máx | PD | 42 W | @ TC=25°C |
| Temperatura de operación | Tj | -55°C a +175°C | |
| Encapsulado | TO-220 | — | Through-hole |

---

## Carga en este proyecto

| Parámetro | Valor ventilador |
|---|---|
| Tensión de operación | 48V DC |
| Corriente típica (MR1238E48B) | ~0.30 A |
| Potencia disipada en MOSFET | Pd = ID² × RDS(on) = 0.3² × 0.18 ≈ **16 mW** |

Margen de seguridad: ID del MOSFET (10A) vs ID real (0.3A) → **ratio 33×**. Sin problema térmico.

---

## Circuito de conexión

```
GPIO4 (VENT) ──[100Ω resistencia gate]──┬── Gate (IRL520N)
                                         │
                                   [10kΩ pull-down]
                                         │
                                        GND

48V DC ──(+ventilador)──(−ventilador)── Drain (IRL520N)
                                         │
                              [1N4007 flyback, cátodo a 48V]
                                         │
                                        Source (IRL520N) ── GND
```

**Protección:**
- Resistencia de gate (100Ω): limita corriente de commutación, protege GPIO
- Pull-down (10kΩ): estado seguro (OFF) cuando GPIO es alta impedancia
- Diodo flyback 1N4007: absorbe pico inductor del motor al apagar

---

## Links de descarga del datasheet

| Documento / Fuente | URL | Estado | Archivo Local | Tamaño | Páginas |
|---|---|---|---|---|---|
| **Infineon** | https://www.infineon.com/dgdl/Infineon-IRL520N-DataSheet-v01_01-EN.pdf?fileId=5546d462533600a40153565f9b62255b | Success | `IRL520N_Infineon.pdf` | 314.4 KB | 10 |
| **Vishay** | https://www.vishay.com/docs/91298/irl520.pdf | Success | `IRL520N_Vishay.pdf` | 236.5 KB | 8 |
| **Vishay IRL540** | https://www.vishay.com/docs/91300/irl540.pdf | Success | `IRL520N_Vishay_IRL540.pdf` | 230.7 KB | 8 |
| **Vishay failed** | https://www.vishay.com/docs/91015/sihrl520.pdf | Failed (HTTP Error 404: Not Found) | `IRL520N_Vishay_failed.pdf` | - | - |
