# Instrucciones para la Sesión en Vivo (Prueba Física)

## 1. Hardware y Microcontrolador
La prueba física en la sesión en vivo utilizará una placa **Seeed Studio XIAO RP2350** en lugar del Raspberry Pi Pico RP2040 utilizado en Wokwi. Las consideraciones clave de este cambio son:

* **Pines Físicos vs GPIOs:** En la placa XIAO, las serigrafías de los pines (D0, D1, D4, etc.) NO equivalen al número de GPIO del microcontrolador (a diferencia del Pico donde el pin GP26 es el GPIO26). 
* **Compatibilidad de Código:** El firmware utiliza la numeración interna del GPIO. El código migrado a esta carpeta mantiene los mismos números de GPIO (por ejemplo, `PIN_TEMP_INT = 26`), los cuales corresponden a pines físicos específicos en el XIAO según su datasheet oficial.
* **Lectura ADC (BETA):** En Wokwi se configuraba el NTC virtual con un valor Beta de 3950. En esta versión física, el archivo `main.cpp` ha sido reconfigurado para usar el valor real `BETA_HW = 3435.0` correspondiente a los sensores NTC TEWA TT05 provistos para la prueba física.

## 2. Mapa de Conexiones Físicas (XIAO RP2350)
Basado en el pinout oficial y el datasheet del XIAO RP2350:

| Señal del Proyecto | GPIO Firmware | Pin Físico XIAO (Serigrafía) |
| :--- | :--- | :--- |
| `TEMP_INT` (NTC 1) | `GPIO26` | **A0 / D0** |
| `TEMP_EXT` (NTC 2) | `GPIO27` | **A1 / D1** |
| `SW1` (DIP bit 0) | `GPIO6` | **D4** |
| `SW2` (DIP bit 1) | `GPIO7` | **D5** |
| `SW3` (DIP bit 2) | `GPIO0` | **D6** |
| `AIN1` (TB6612FNG) | `GPIO2` | **D8** |
| `AIN2` (TB6612FNG) | `GPIO1` | **D7** |
| `MOTOR_EN` (PWMA) | `GPIO3` | **D10** |
| `VENT` (MOSFET) | `GPIO4` | **D9** |

## 3. Preparación del Entorno (PlatformIO en VS Code)
Esta carpeta contiene la estructura estándar para abrir el proyecto en PlatformIO:
1. Abre VS Code y navega al icono de PlatformIO.
2. Selecciona **"Open Project"** y elige la carpeta `PruebaFisica_SXRP2350`.
3. El archivo `platformio.ini` ya está configurado para utilizar el core Arduino de Earle Philhower, el cual brinda soporte completo para el RP2040 y la nueva arquitectura RP2350 (Cortex-M33 / Hazard3).
4. Conecta el XIAO RP2350 por USB, haz clic en el botón de **Upload** (la flecha apuntando a la derecha en la barra inferior) y abre el **Serial Monitor** (el ícono de enchufe) a 115200 baudios para interactuar con los comandos de prueba (`SET:XX`, `TEMP:XX`, `EXT:XX`).
