# Wokwi

Simulacion del sistema de ventilacion de aire caliente para Jaguar MX.

## Objetivo

La simulacion reproduce la logica del PDF de evaluacion:

- leer `TEMP_INT` y `TEMP_EXT`
- abrir compuertas y encender ventilador cuando `TEMP_INT > TEMP_EXT`
- apagar ventilador y cerrar compuertas cuando `TEMP_INT <= TEMP_EXT`
- entrar en estado seguro si alguna lectura NTC es invalida
- usar el DIP switch de 3 bits para seleccionar el setpoint de activación

## Archivos

- `diagram.json`: conexionado completo de la simulacion
- `sketch.ino`: firmware Arduino para Wokwi
- `tb6612fng-sim.chip.json`, `tb6612fng-sim.chip.c`: modelo del TB6612FNG
- `main.py`, `adc_ntc.py`, `dip_switch.py`, `fan.py`, `fsm.py`, `hbridge.py`: referencia MicroPython
- `MAPA_GPIO.md`: mapa rapido de pines

## Notas

- `GP26` y `GP27` simulan los NTC.
- `GP6`, `GP7` y `GP0` leen el DIP switch con `INPUT_PULLUP`.
- `GP2`, `GP1` y `GP3` controlan el TB6612FNG.
- `GP4` controla el ventilador simulado.
- `STBY` del TB6612FNG va fijo a `3V3`.
- Los LEDs de estado usan resistores en serie de `220 ohm`.

