# Seeed Studio XIAO RP2350 — MCU (Sesión en Vivo)

**Función en el sistema:** MCU principal para la sesión en vivo con Jaguar de México
(En la simulación Wokwi se usa el Raspberry Pi Pico / RP2040)

---

## ⚠️ DIFERENCIA CRÍTICA vs Raspberry Pi Pico

> Los pines del XIAO RP2350 **NO son compatibles** con el Pico en encapsulado.
> El XIAO tiene 19 GPIOs expuestos en pitch 2.54mm, pero el **numbering de GPIO es diferente al silkscreen**.
> **Verificar siempre contra el pinout oficial antes de conectar hardware.**

---

## Especificaciones principales

| Parámetro | Valor |
|---|---|
| Microcontrolador | **Raspberry Pi RP2350** |
| Arquitectura | Dual Arm Cortex-M33 **o** dual RISC-V Hazard3 (switchable) |
| Velocidad de reloj | **150 MHz** |
| FPU | Sí (Cortex-M33) — útil para cálculos NTC en float |
| Flash | 4 MB (QSPI) |
| SRAM | 520 KB |
| GPIOs expuestos | 19 multifunction |
| ADC | 12-bit, 4 canales |
| PWM | 24 canales |
| I²C, SPI, UART | Sí (via PIO también) |
| USB | USB 1.1 Device/Host |
| Dimensiones | **21 × 17.8 mm** |
| RGB LED onboard | Sí (GPIO 16, 17, 25 aprox) |
| Battery Management | Sí — BMS onboard para LiPo |
| Voltaje operación | 3.3V (5V tolerante vía USB) |
| Corriente max por GPIO | 12 mA (RP2350 spec) |
| Lenguajes | MicroPython, C, C++ |

---

## Pinout — GPIOs usados en este proyecto

> **IMPORTANTE:** Los números de GPIO en el firmware corresponden al GPIO interno del RP2350,
> NO a la etiqueta Dn del silkscreen del XIAO. El XIAO RP2350 **no** sigue la convención
> Dn = GPIOn — el mapeo es diferente. Ver tabla y fuente oficial abajo.
>
> ⚠️ **CORRECCIÓN:** La tabla anterior tenía etiquetas XIAO incorrectas (usaba D0=GPIO0,
> D1=GPIO1, etc. que es el mapeo del RP2040/Pico, NO del XIAO RP2350).
> Tabla corregida contra: https://wiki.seeedstudio.com/xiao_rp2350_arduino/ (Pin Map oficial)

| GPIO RP2350 | Etiqueta XIAO (silkscreen) | Función en proyecto |
|---|---|---|
| GPIO26 | **D0 / A0** | ADC0 → TEMP_INT |
| GPIO27 | **D1 / A1** | ADC1 → TEMP_EXT |
| GPIO6  | **D4**       | SW1 — DIP switch bit 0 |
| GPIO7  | **D5**       | SW2 — DIP switch bit 1 |
| GPIO0  | **D6**       | SW3 — DIP switch bit 2 |
| GPIO2  | **D8**       | AIN1 — TB6612FNG dir 1 |
| GPIO1  | **D7**       | AIN2 — TB6612FNG dir 2 |
| GPIO3  | **D10**      | MOTOR_EN |
| GPIO4  | **D9**       | VENT — control MOSFET |

**Pin Map completo del XIAO RP2350 (fuente oficial Seeed Studio):**

| Etiqueta XIAO | GPIO RP2350 | Etiqueta XIAO | GPIO RP2350 |
|---|---|---|---|
| D0 / A0 | GPIO26 | D7  | GPIO1  |
| D1 / A1 | GPIO27 | D8  | GPIO2  |
| D2 / A2 | GPIO28 | D9  | GPIO4  |
| D3       | GPIO5  | D10 | GPIO3  |
| D4       | GPIO6  | D11 | GPIO21 |
| D5       | GPIO7  | D12 | GPIO20 |
| D6       | GPIO0  | D13 | GPIO17 |
|          |        | D14 | GPIO16 |

> Fuente: https://wiki.seeedstudio.com/xiao_rp2350_arduino/#pin-map

---

## Diferencias RP2350 vs RP2040 relevantes para el firmware

| Aspecto | RP2040 | RP2350 |
|---|---|---|
| WDT | Disponible, `machine.WDT` | Disponible, `machine.WDT` — **timeout max ~8s** |
| ADC | 12-bit, read_u16() | 12-bit, read_u16() — misma API |
| GPIO | 3.3V, 12mA max | 3.3V, 12mA max |
| Float | Cortex-M0+ (sin FPU HW) | **Cortex-M33 con FPU HW** — más rápido |
| MicroPython | `machine` API igual | `machine` API igual |

**El firmware es compatible sin cambios entre RP2040 y RP2350** en términos de API.
Solo verificar los GPIO numbers en hardware físico.

---

## Links de descarga del datasheet

| Documento / Fuente | URL | Estado | Archivo Local | Tamaño | Páginas |
|---|---|---|---|---|---|
| **Schematic** | https://files.seeedstudio.com/wiki/XIAO-RP2350/res/Seeed-Studio-XIAO-RP2350-v1.0.pdf | Success | `XIAO_RP2350_Schematic.pdf` | 295.6 KB | 5 |
| **RP2350 Datasheet** | https://datasheets.raspberrypi.com/rp2350/rp2350-datasheet.pdf | Success | `RP2350_Datasheet.pdf` | 7781.7 KB | 1380 |
| **RP2350 Product Brief** | https://datasheets.raspberrypi.com/rp2350/rp2350-product-brief.pdf | Success | `RP2350_Product_Brief.pdf` | 625.2 KB | 10 |
