# Mapa GPIO - Wokwi

| Senal | GPIO | Componente Wokwi |
|---|---:|---|
| TEMP_INT | GP26 / ADC0 | `ntc_in` |
| TEMP_EXT | GP27 / ADC1 | `ntc_out` |
| SW1 | GP6 | `dip1` |
| SW2 | GP7 | `dip1` |
| SW3 | GP0 | `dip1` |
| VENT | GP4 | `r_vent` + `led_vent` |
| AIN1 | GP2 | `hbridge` |
| AIN2 | GP1 | `hbridge` |
| PWMA | GP3 | `hbridge` |
| STBY | `3V3` | `hbridge` |

## Motor

- `AO1` -> `motor1:1` y `r_motor_cierra`
- `AO2` -> `motor1:2` y `r_motor_abre`

## LEDs

- `led_vent` con `r_vent`
- `led_motor_a_abre` con `r_motor_abre`
- `led_motor_a_cierra` con `r_motor_cierra`
