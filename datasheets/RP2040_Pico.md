# RP2040 / Raspberry Pi Pico — MCU (Simulación Wokwi)

**Función en el sistema:** MCU objetivo para la simulación Wokwi (plantilla base de Jaguar)

---

## RP2040 — Especificaciones del chip

| Parámetro | Valor |
|---|---|
| Arquitectura | Dual Arm Cortex-M0+ |
| Velocidad de reloj | 133 MHz (hasta 240 MHz overclock) |
| Flash | 2 MB onboard (Pico) / externo |
| SRAM | 264 KB |
| GPIOs | 30 multifunction |
| ADC | 12-bit, 4 canales (ADC0–ADC3) + temperatura interna |
| PWM | 16 canales (8 slices × 2) |
| I²C / SPI / UART | Sí (PIO configurable) |
| USB | USB 1.1 Device/Host |
| Temperatura de operación | -20°C a +85°C |
| Tensión de operación | 1.8V – 3.3V (nominal 3.3V) |
| Corriente max por GPIO | 12 mA |

---

## Raspberry Pi Pico — Pinout relevante para este proyecto

| GPIO | Pin físico Pico | Función |
|---|---|---|
| GPIO26 | Pin 31 (ADC0) | TEMP_INT — sensor NTC interno |
| GPIO27 | Pin 32 (ADC1) | TEMP_EXT — sensor NTC externo |
| GPIO6  | Pin 9  | SW1 — DIP switch bit 0 |
| GPIO7  | Pin 10 | SW2 — DIP switch bit 1 |
| GPIO0  | Pin 1  | SW3 — DIP switch bit 2 |
| GPIO2  | Pin 4  | AIN1 — puente H TB6612FNG |
| GPIO1  | Pin 2  | AIN2 — puente H TB6612FNG |
| GPIO3  | Pin 5  | MOTOR_EN |
| GPIO4  | Pin 6  | VENT — control MOSFET |

---

## ADC en MicroPython (RP2040)

```python
from machine import ADC, Pin

adc = ADC(Pin(26))       # GPIO26 → ADC0
raw = adc.read_u16()     # Retorna 0–65535 (12-bit escalado a 16-bit por MicroPython)

# Conversión a voltaje:
# V = raw * 3.3 / 65535
```

**Nota:** `read_u16()` escala internamente el ADC de 12-bit a 16-bit.
En el firmware usamos `ADC_BITS = 65535` (no 4095) por esta razón.

---

## WDT en MicroPython (RP2040)

```python
from machine import WDT

wdt = WDT(timeout=8000)  # 8 segundos — máximo en RP2040/RP2350
wdt.feed()               # Debe llamarse periódicamente para no resetear
```

---

## Links de descarga del datasheet

| Documento / Fuente | URL | Estado | Archivo Local | Tamaño | Páginas |
|---|---|---|---|---|---|
| **RP2040 Datasheet** | https://datasheets.raspberrypi.com/rp2040/rp2040-datasheet.pdf | Success | `RP2040_Datasheet.pdf` | 5177.0 KB | 642 |
| **Pico Datasheet** | https://datasheets.raspberrypi.com/pico/pico-datasheet.pdf | Success | `Pico_Datasheet.pdf` | 16952.1 KB | 33 |
| **Pico C SDK** | https://datasheets.raspberrypi.com/pico/raspberry-pi-pico-c-sdk.pdf | Success | `Pico_C_SDK.pdf` | 5842.3 KB | 745 |
