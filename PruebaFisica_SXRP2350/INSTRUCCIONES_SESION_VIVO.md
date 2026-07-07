# Instrucciones para la Sesión en Vivo (Prueba Física)

## 1. Hardware y Microcontrolador
La prueba física utiliza una placa **Seeed Studio XIAO RP2350** en lugar del Raspberry Pi Pico RP2040 usado en Wokwi. Consideraciones clave:

* **Pines físicos vs GPIOs:** En el XIAO, la serigrafía (D0, D1, D4...) NO equivale al número de GPIO del RP2350. El firmware usa numeración interna de GPIO (`digitalWrite(4)` = GPIO4), que es lo que el core Arduino-Pico (Earle Philhower) espera de forma nativa.
* **Lectura ADC (Beta):** El firmware usa `BETA = 3435 K`, el valor de datasheet del NTC TEWA TT05-10KC8-1S-T105-1500 real (en Wokwi se usaba 3950, el Beta del NTC genérico del simulador).
* **Sin lógica de simulación:** Esta versión lee temperatura real de los NTC. Se eliminó todo el modelo térmico simulado de la versión Wokwi. Para forzar condiciones durante la demo existen comandos Serial (ver sección 4).

## 2. Mapa de Conexiones Físicas (XIAO RP2350)
Verificado contra la variante oficial `seeed_xiao_rp2350` del core Arduino-Pico:

| Señal del Proyecto | GPIO Firmware | Pin Físico XIAO (Serigrafía) |
| :--- | :--- | :--- |
| `TEMP_INT` (NTC 1) | `GPIO26` | **A0 / D0** |
| `TEMP_EXT` (NTC 2) | `GPIO27` | **A1 / D1** |
| `SW1` (DIP bit 0) | `GPIO6` | **D4** |
| `SW2` (DIP bit 1) | `GPIO7` | **D5** |
| `SW3` (DIP bit 2) | `GPIO0` | **D6** |
| `AIN2` (TB6612FNG) | `GPIO1` | **D7** |
| `AIN1` (TB6612FNG) | `GPIO2` | **D8** |
| `VENT` (MOSFET) | `GPIO4` | **D9** |
| `MOTOR_EN` (PWMA) | `GPIO3` | **D10** |

Nota: D3 del XIAO es **GPIO5** (no GPIO29 como en otras placas XIAO) — no se usa en este proyecto, pero no asumir equivalencias con el Pico.

## 3. Preparación del Entorno (PlatformIO en VS Code)
1. Abre VS Code → icono de PlatformIO → **"Open Project"** → carpeta `PruebaFisica_SXRP2350`.
2. `platformio.ini` ya apunta al board `seeed_xiao_rp2350` con el core Arduino de Earle Philhower (soporte RP2350 Cortex-M33).
3. **Primera carga:** con la placa desconectada, mantén presionado el botón **BOOT (B)** del XIAO, conéctalo por USB y suéltalo — aparece la unidad `RP2350` en modo bootloader UF2. Después de la primera carga, PlatformIO puede resetear la placa automáticamente (protocolo `picotool`).
4. Clic en **Upload** y abre el **Serial Monitor** a 115200 baudios.

## 4. Comandos Serial para la Demo
El loop de control corre a 1 Hz y publica una línea de telemetría por ciclo. Comandos disponibles (terminados en Enter):

| Comando | Efecto |
| :--- | :--- |
| `SET:55` | Fija el setpoint manual a 55 °C (ignora el DIP) |
| `SET:0` | Regresa el setpoint al DIP switch |
| `TEMP:62` | Fuerza la temperatura interna a 62 °C (marca `(OVR)` en telemetría) |
| `TEMP:AUTO` | Regresa a la lectura real del NTC interno |
| `EXT:25` | Fuerza la temperatura externa a 25 °C |
| `EXT:AUTO` | Regresa a la lectura real del NTC externo |

Secuencia de demo sugerida: `EXT:25` → `TEMP:62` (con SP=55 dispara COOLING: compuertas abren ~3 s y luego ventilador ON) → `TEMP:24` (INT ≤ EXT dispara IDLE: ventilador OFF y compuertas cierran). Para demostrar ERROR/safe state: desconectar el cable de señal de un NTC (3 lecturas inválidas → ERROR, recovery a los 30 s, LOCKOUT tras 5 recoveries).

## 5. Subproyecto `SimuladorTermico/` (demo con planta simulada)
Firmware alternativo para demostrar el ciclo completo sin depender de condiciones térmicas reales: la FSM, el puente H, el ventilador y el DIP switch operan sobre los GPIOs físicos, pero las temperaturas provienen de un modelo térmico interno (el gabinete "se calienta" solo a 0.5 °C/s y se enfría a 1.5 °C/s cuando el ventilador extrae aire). Los NTC no se leen en esta variante.

* Se abre como proyecto PlatformIO independiente (carpeta `SimuladorTermico`), mismo board y procedimiento de carga que el principal.
* Comandos Serial adicionales:

| Comando | Efecto |
| :--- | :--- |
| `TEMP:62` | Fija la temperatura interna del modelo |
| `EXT:25` | Fija la temperatura exterior del modelo |
| `RATE:1.0` | Tasa de calentamiento del gabinete (°C/s) |
| `COOL:2.0` | Tasa de enfriamiento con extracción activa (°C/s) |
| `FALLA:INT` / `FALLA:EXT` / `FALLA:AMBOS` | Simula NTC desconectado (demuestra ERROR → recovery → LOCKOUT) |
| `FALLA:OFF` | Restaura los sensores simulados |
| `SET:55` / `SET:0` | Setpoint manual / regresar al DIP |

* Demo sin tocar nada: el modelo arranca en 30 °C y sube solo hasta cruzar el setpoint → COOLING (compuertas + ventilador reales se activan) → enfría hasta la temperatura exterior → IDLE → vuelve a calentarse, ciclando indefinidamente.
* La telemetría se marca `TLM(SIM)` para distinguirla del firmware físico en cualquier captura.

## 6. Checklist de Verificación en Sitio (antes de energizar 48 V)
1. **Divisores NTC:** confirmar con multímetro que cada divisor es 3.3 V — R 10 kΩ — nodo ADC — NTC — GND. A ~25 °C ambiente el nodo debe medir ≈ 1.65 V y la telemetría debe reportar la temperatura ambiente real (±2 °C).
2. **TB6612FNG:** verificar que **STBY está a nivel alto** (el firmware no lo controla; si queda flotante o a GND el motor no se moverá aunque AIN1/AIN2/PWMA sean correctos). VM = 5 V para el FIT0803, VCC = 3.3 V.
3. **Ventilador 48 V:** confirmar que el gate del MOSFET tiene pull-down a GND (con el XIAO en reset/bootloader el GPIO4 queda en alta impedancia y el ventilador no debe arrancar solo).
4. **DIP switch:** los 3 polos conmutan a GND (el firmware usa pull-ups internos; posición ON = bit 1). Verificar continuidad de cada polo a su pin antes de confiar en el setpoint.
5. **Travel del actuador:** el FIT0803 a 5 V recorre ~1.7 s; el firmware corta a los 3 s. El actuador tiene fin de carrera interno, así que el margen extra es seguro, pero confirmar en la primera apertura que llega al extremo.
6. **Masas comunes:** GND del XIAO, del TB6612FNG, del MOSFET y de la fuente de 48 V deben estar unidas.
