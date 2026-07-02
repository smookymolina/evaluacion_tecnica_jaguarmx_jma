# TB6612FNG — Puente H Dual (Toshiba)

**Función en el sistema:** Control bidireccional del actuador lineal FIT0803 (compuertas)

---

## Parámetros eléctricos clave

| Parámetro | Valor | Condición |
|---|---|---|
| VM (motor supply) | 2.5V – 13.5V | Tensión de alimentación del motor |
| VCC (logic supply) | 2.7V – 5.5V | Tensión lógica — **usar 3.3V del RP2350** |
| IO continua por canal | 1.2 A | Corriente continua por canal A ó B |
| IO pico por canal | 3.2 A | Pico < 2ms |
| MOSFET ON resistance | 0.5 Ω | Típico @ ID=1A, VCC=5V |
| Temperatura de operación | -20°C a +85°C | |
| Frecuencia PWM máx | 100 kHz | Para control de velocidad (no usado en este proyecto) |
| Consumo standby | 0 µA | Con STBY=LOW |

---

## Tabla de verdad — Canal A (FIT0803)

| AIN1 | AIN2 | PWMA / MOTOR_EN | Salida A | Función |
|---|---|---|---|---|
| H | H | H | Freno | Short-brake |
| L | H | H | Forward | **Abrir compuertas** |
| H | L | H | Reverse | **Cerrar compuertas** |
| L | L | H | Stop | Free-run (alta impedancia) |
| X | X | L | Stop | **Estado seguro** |
| X | X | — STBY=L | Standby | Consumo cero |

> **CRÍTICO:** Pin STBY debe estar HIGH para que el puente H funcione.
> En este proyecto STBY se conecta a 3.3V directamente (sin control GPIO).

---

## Mapa de pines usado en este proyecto

| Pin TB6612FNG | GPIO RP2040/2350 | Función |
|---|---|---|
| AIN1 | GPIO2 | Dirección 1 |
| AIN2 | GPIO1 | Dirección 2 |
| PWMA (MOTOR_EN) | GPIO3 | Habilitación |
| VM | 5V rail | Alimentación motor (FIT0803 @ 5V) |
| VCC | 3.3V rail | Alimentación lógica |
| STBY | 3.3V rail | **Siempre HIGH — crítico** |
| GND | GND | Tierra común |

---

## Desacoplamiento recomendado (PCB)

- 100 nF cerámico (C0G o X5R) entre VM y GND — lo más cerca al IC
- 47 µF electrolítico entre VM y GND — bulk decoupling
- 100 nF cerámico entre VCC y GND

---

## Links de descarga del datasheet

| Documento / Fuente | URL | Estado | Archivo Local | Tamaño | Páginas |
|---|---|---|---|---|---|
| **SparkFun** | https://cdn.sparkfun.com/datasheets/Robotics/TB6612FNG.pdf | Success | `TB6612FNG_SparkFun.pdf` | 202.6 KB | 11 |
| **Pololu** | https://www.pololu.com/file/0J86/tb6612fng.pdf | Success | `TB6612FNG_Pololu.pdf` | 300.9 KB | 11 |
| **Adafruit** | http://www.adafruit.com/datasheets/TB6612FNG_datasheet_en_20121101.pdf | Success | `TB6612FNG_Adafruit.pdf` | 355.8 KB | 11 |
| **Toshiba** | https://toshiba.semicon-storage.com/info/TB6612FNG_datasheet_en_20141001.pdf | Failed (HTTP Error 404: Not Found) | `TB6612FNG_Toshiba.pdf` | - | - |
