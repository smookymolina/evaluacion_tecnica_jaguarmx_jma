# Instrucciones de Simulación en Wokwi - Sistema de Extracción de Aire Caliente

## Lógica General del Sistema

El sistema implementa una Máquina de Estados Finitos (FSM) que controla la temperatura interna de un gabinete de telecomunicaciones. Su objetivo es asegurar que el aire caliente se extraiga abriendo unas compuertas y encendiendo un ventilador, basado en la comparación entre las temperaturas interna y externa, así como un _setpoint_ de configuración.

1. **Lectura de Temperaturas**: El sistema lee periódicamente (cada 1 segundo) la temperatura de los sensores NTC (Interno y Externo). Se aplica un filtro de promedio recortado (Trimmed Mean) sobre las últimas 8 muestras para eliminar posibles picos de ruido en la lectura analógica.
2. **Evaluación de Enfriamiento (Estado COOLING)**:
   - Se activa **SOLO SI** la temperatura interna supera la temperatura externa **Y ADEMÁS** supera el *setpoint* de configuración (más un margen de histéresis de 1°C).
   - Secuencia de activación: El puente H es comandado para abrir las compuertas (activación durante 3 segundos sin bloquear el código). Una vez abierta la compuerta, se enciende el ventilador.
   - **Simulación de Retroalimentación Térmica**: Mientras el sistema se encuentra en modo enfriamiento (ventilador y compuerta activos), el código simula un descenso gradual (1°C por segundo) de la temperatura interna. De esta forma, el sistema "enfría" virtualmente el ambiente dentro de la simulación de Wokwi, aun cuando el deslizador del sensor permanezca estático.
3. **Detención (Estado IDLE)**:
   - Se activa cuando la temperatura interna desciende hasta igualar o caer por debajo de la temperatura externa. En este diseño, el enfriamiento continuará hasta alcanzar el equilibrio con el exterior.
   - Secuencia de detención: Se apaga inmediatamente el ventilador y el puente H es comandado para cerrar las compuertas.
4. **Manejo de Errores**:
   - Si un sensor se desconecta o reporta una lectura fuera del rango físico (-40 a 105°C), se registra un error. Tras 3 lecturas inválidas consecutivas, el sistema pasa a un estado seguro (**SAFE STATE**): detiene el motor y apaga el ventilador.
   - El sistema intentará recuperarse automáticamente después de 30 segundos, con un máximo de 5 intentos antes de bloquearse de manera permanente.

---

## Configuración del DIP Switch

El sistema cuenta con un DIP switch de 3 posiciones, el cual define el _setpoint_ o temperatura de activación utilizada por el firmware. 

**En la simulación en Wokwi:** 
- Cuando el interruptor está en la posición superior (**OFF** o circuito abierto), el pin del microcontrolador es llevado a `HIGH` por una resistencia interna _pull-up_. Esto se interpreta como un **0**.
- Cuando el interruptor se desliza hacia abajo (posición **ON**), el circuito se cierra hacia `GND`, por lo que el pin lee `LOW`. Esto se interpreta como un **1**.

La siguiente tabla refleja fielmente el comportamiento especificado en los requerimientos. Para cambiar el umbral de activación, deslice los interruptores del DIP Switch de acuerdo a las siguientes combinaciones:

| SW3 (MSB) | SW2 | SW1 (LSB) | Setpoint de Temperatura (°C) |
| :---: | :---: | :---: | :---: |
| 0 (OFF) | 0 (OFF) | 0 (OFF) | **40** |
| 0 (OFF) | 0 (OFF) | 1 (ON)  | **45** |
| 0 (OFF) | 1 (ON)  | 0 (OFF) | **50** |
| 0 (OFF) | 1 (ON)  | 1 (ON)  | **55** |
| 1 (ON)  | 0 (OFF) | 0 (OFF) | **60** |
| 1 (ON)  | 0 (OFF) | 1 (ON)  | **65** |
| 1 (ON)  | 1 (ON)  | 0 (OFF) | **70** |
| 1 (ON)  | 1 (ON)  | 1 (ON)  | **75** |

*(Nota: En el diagrama de Wokwi, **SW1** corresponde al interruptor 1, **SW2** al 2, y **SW3** al 3).*

---

## Comandos por Consola (Monitor Serial)

Para facilitar las pruebas y demostraciones en la simulación sin tener que manipular constantemente los deslizadores de los NTC o el DIP switch, el sistema permite la inyección de comandos vía **Monitor Serial**. Esto te otorga un control directo sobre las variables térmicas y el umbral de configuración:

*   **`SET:XX`**: Fija manualmente la temperatura de activación (Setpoint). Reemplaza la lectura del DIP switch. 
    *   _Ejemplo_: `SET:35` establece el umbral en 35°C.
    *   Para volver a ceder el control al DIP switch, ingresa `SET:0`.
*   **`TEMP:XX`**: Inyecta y sobrescribe instantáneamente la **temperatura interna** de la cabina. El sistema asimilará este valor y, de ser necesario, arrancará el ciclo de enfriamiento de inmediato.
    *   _Ejemplo_: `TEMP:80` forzará a la máquina de estados a detectar que el interior está a 80°C.
*   **`EXT:XX`**: Fija de manera manual la **temperatura exterior**. El enfriamiento de la cabina se detendrá al empatar con esta temperatura límite. 
    *   _Ejemplo_: `EXT:15` finge que la temperatura de la calle es de 15°C.
    *   Para regresar a la lectura del sensor NTC (potenciómetro/slider de Wokwi), envía `EXT:AUTO` o `EXT:OFF`.
