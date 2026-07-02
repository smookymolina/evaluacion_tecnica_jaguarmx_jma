# Evaluación Técnica — Ingeniero de Sistemas Embebidos Jr.
**Candidato:** Ing. Jair Molina Arce  
**Proyecto:** Sistema de Extracción de Aire Caliente para Gabinete de Telecomunicaciones  
**Empresa:** Jaguar de México  
**Fecha:** 30 de junio de 2026  

---

## 1. Simulación en Wokwi

*   **URL del proyecto:** [https://wokwi.com/projects/468449090390286337](https://wokwi.com/projects/468449090390286337) *(Plantilla base extendida para validación local y en la plataforma)*
*   **Archivo de conexión local:** [diagram.json](file:///C:/Users/GIRTEC/Claude/Projects/Jaguar%20MX/diagram.json)

### Descripción de la simulación y componentes equivalentes
La simulación en Wokwi utiliza un microcontrolador **Raspberry Pi Pico (RP2040)** para verificar el comportamiento de la máquina de estados finitos (FSM) y la adquisición analógica. A continuación, se describen los componentes del circuito:
1.  **Sensores de temperatura (TEMP_INT y TEMP_EXT):** Se simulan utilizando dos potenciómetros/sensores de temperatura analógicos en Wokwi conectados a las entradas analógicas GP26 (ADC0) y GP27 (ADC1).
2.  **Puente H (TB6612FNG):** Se utiliza un chip custom de Wokwi (`chip-tb6612fng-sim`) provisto por Jaguar de México. Este chip de simulación emula los pines de dirección `AIN1`, `AIN2`, la habilitación `PWMA` y el pin de standby `STBY`.
3.  **Indicadores del motor compuertas:** Se conectan dos LEDs en antiparalelo en las salidas `AO1` y `AO2` del puente H custom:
    *   **LED Verde (MOTOR A ABRE):** Se enciende cuando el motor gira hacia adelante (compuertas abriendo, `AO1 = LOW` y `AO2 = HIGH`).
    *   **LED Rojo (MOTOR A CIERRA):** Se enciende cuando el motor gira en reversa (compuertas cerrando, `AO1 = HIGH` y `AO2 = LOW`).
4.  **DIP Switch (Configuración de Setpoint):** Un DIP switch de 8 posiciones (`dip1`) se cablea de modo que los interruptores 1, 2 y 3 actúen como SW1, SW2 y SW3. Los pines del microcontrolador se configuran con pull-up interno, por lo que el DIP switch conecta a GND (conmutación activa en nivel bajo, lógica invertida en el código).
5.  **Extractor de Aire (Ventilador):** Se utiliza un **LED Azul (VENTILADOR)** conectado a GP4 (`VENT`) que actúa como indicador visual de activación del extractor (ventilador ON / MOSFET conductor).

---

## 2. Cuestionario Técnico

### Q1: ¿Cuánto tiempo dedicaste a cada entregable?
El desarrollo del proyecto se desglosa de la siguiente manera:
*   **Arquitectura y Diseño de Firmware:** 8 horas. Esto incluye el diseño de la FSM, la implementación de la ecuación Beta de calibración NTC, la estructuración en MicroPython orientado a objetos y la configuración del watchdog timer.
*   **Simulación en Wokwi:** 4 horas. Conexión del circuito, desarrollo y depuración de los componentes equivalentes (leds bidireccionales para el motor, mapeo de pines) y testing de los escenarios de fallo.
*   **Diseño de Esquemático y PCB en KiCad (Planificado/Proyectado):** 8 horas. Separación analógica/digital, cálculo de filtros RC y trazado de pistas de potencia para motor y extractor.
*   **Registro de IA, Pruebas y Documentación:** 3 horas. Creación de scripts de prueba automatizados con mocks locales en Python y redacción de este reporte.

### Q2: ¿En qué momento del desarrollo te bloqueaste y cómo lo resolviste?
Me encontré con dos bloqueos principales durante la fase de desarrollo:
1.  **Discrepancia en la constante Beta del NTC:** El enunciado del cronograma inicial indicaba un valor de $B = 3950\text{ K}$, pero al revisar el datasheet provisto de TEWA (`NTC_TT05_TEWA.pdf`) y las tiendas oficiales, se confirmó que el part number `TT05-10KC8-1S-T105-1500` tiene un coeficiente Beta de $3435\text{ K}$. Utilizar 3950 K habría provocado un error de cálculo sistemático de más de $3\text{°C}$ a temperaturas cercanas a $50\text{°C}$. Lo resolví guiándome bajo el principio de "el datasheet del fabricante manda" y corrigiendo la constante en `adc_ntc.py` a `3435`.
2.  **Expiración del Watchdog Timer durante el viaje del actuador:** El recorrido del actuador lineal FIT0803 a 5V tarda aproximadamente $1.72\text{ s}$. Para asegurar una apertura total, se determinó un tiempo de alimentación de $3\text{ s}$ (`ACTUATOR_TRAVEL_MS = 3000`). Como este proceso es bloqueante, el Watchdog de $8\text{ s}$ corría el riesgo de expirar si coincidía con otras demoras o si se reducía el timeout del WDT en producción. Lo resolví registrando un callback `set_wdt_feed(self._alimentar_wdt)` desde la clase FSM hacia la clase `HBridge`, de modo que el retardo del motor se realiza en ráfagas de $500\text{ ms}$ alimentando activamente al WDT entre intervalos (`_safe_sleep_ms`).

### Q3: ¿Para qué usaste AI durante el desarrollo? Describe al menos un caso donde el output de AI fue incorrecto o incompleto y cómo lo detectaste y corregiste.
Utilicé Claude 3.5 Sonnet como asistente de programación en pareja para generar los módulos de hardware en MicroPython y acelerar la creación de casos de prueba.

**Caso de Output Incorrecto de la AI:**
La AI inicialmente propuso un método de promediado de ADC (`_raw_average`) que realizaba 8 lecturas secuenciales consecutivas dentro de la misma llamada `read()` mediante un ciclo bloqueante. 
*   *Problema:* Esto no es un buffer circular real (es un promedio por bloques). Además, violaba la arquitectura de tiempo real al bloquear el hilo de ejecución para tomar 8 muestras de golpe en cada ciclo del loop principal de 1 Hz. También, el rango de temperatura válida se autolimitó en el código analógico a $[-40\text{°C}, 105\text{°C}]$ basándose en los límites físicos del sensor NTC.
*   *Cómo lo detecté:* Al realizar la revisión estática del código y confrontarlo con `instrucciones.txt` ("buffers ADC circular (N=8 muestras)" y "sensor desconectado <10°C o >130°C = inválido"), identifiqué que:
    1.  No se utilizaba la variable de instancia `self._buf` declarada en `__init__`.
    2.  El sistema no entraría en estado de `ERROR` si se forzaba una lectura de $5\text{°C}$ (ya que el código del sensor la consideraba válida por estar sobre $-40\text{°C}$).
*   *Cómo lo corregí:* Modifiqué `adc_ntc.py` para implementar un búfer circular real usando una lista de Python de tamaño máximo 8, donde en cada ciclo se añade únicamente una nueva lectura analógica (`pop(0)` para descartar la más antigua). Implementé una precarga de 8 muestras únicamente en la primera ejecución para evitar inestabilidad en el arranque, y modifiqué los límites de error estrictamente a $10.0\text{°C}$ y $130.0\text{°C}$ como lo pedía la especificación del cliente.

### Q4: ¿Qué decisión técnica fue la más difícil de tomar y por qué?
La decisión más difícil fue definir la estrategia de bloqueo vs no-bloqueo para el actuador FIT0803. Un actuador lineal consume corriente significativa durante su movimiento y no posee switches de límite internos configurables por software directos (es de bucle abierto por tiempo).
*   *Opción A (Asíncrona):* Crear un sub-estado `OPENING_DAMPERS` y `CLOSING_DAMPERS` en la FSM para que el loop continuara corriendo a 1 Hz mientras el motor se movía en segundo plano.
*   *Opción B (Síncrona con WDT):* Alimentar el puente H y bloquear el loop durante $3\text{ s}$ asegurando que nada interrumpa el movimiento físico, alimentando el Watchdog de forma controlada.
*   *Elección:* Elegí la **Opción B**. En gabinetes industriales de telecomunicaciones, es crucial asegurar que la ventilación no se encienda si las compuertas están obstruidas o parcialmente abiertas. Bloquear el flujo principal por $3\text{ s}$ garantiza una operación transaccional y determinista: el motor completa su carrera antes de que el extractor de aire se active (`fan.on()`), previniendo sobrepresión o contrapresión. Al acoplar el callback del watchdog en el retraso síncrono, se mantiene el fail-safe del hardware.

### Q5: ¿Qué mejoras harías a tu solución si tuvieras más tiempo?
1.  **Retroalimentación del Actuador (Bucle Cerrado):** Añadiría switches de fin de carrera físicos (limit switches) o leería la corriente del puente H (sensado de corriente en el pin `SEN` del chip o mediante shunt) para detectar mecánicamente si el actuador se ha bloqueado o ha completado su recorrido, apagando el motor de inmediato y evitando stall currents.
2.  **Sensor Digital I2C redundante:** Usar sensores analógicos NTC requiere calibración y es muy susceptible a ruido electromagnético inducido por los 48V del ventilador. Un sensor digital como el TMP117 (I2C) con precisión de $\pm0.1\text{°C}$ simplifica el firmware y aumenta la inmunidad al ruido.
3.  **Control PWM del ventilador:** En lugar de control ON/OFF, usaría control por ancho de pulso (PWM) en el MOSFET para arrancar el ventilador de forma suave (soft-start) y ajustar la velocidad proporcionalmente a la diferencia $\Delta T = T_{int} - T_{ext}$, reduciendo el consumo energético y el desgaste acústico.

### Q6: Del 1 al 10, ¿qué tan confiable sería tu sistema en un entorno industrial real?
Le asigno una calificación de **8.5/10**.
*   **Fortalezas (Por qué es confiable):**
    *   **Watchdog por Hardware:** El watchdog timer de $8\text{ s}$ garantiza que ante cualquier fallo de ejecución o congelamiento de MicroPython, el procesador se reinicie y aplique el estado seguro.
    *   **Watchdog en sleep:** La alimentación del WDT durante el movimiento síncrono del actuador evita reinicios falsos por software lento.
    *   **Transiciones Seguras:** El estado seguro se aplica tanto en la inicialización (`INIT`) como en fallos de lectura analógica (`ERROR` y `LOCKOUT`), deteniendo el puente H y el ventilador.
    *   **Manejo de Transientes:** El promedio móvil con rechazo de valores máximos y mínimos (trimmed mean) en el buffer circular analógico previene falsas alarmas por picos de ruido eléctrico de conmutación.
*   **Debilidades (Por qué no es un 10/10):**
    *   **Operación a Lazo Abierto:** El actuador FIT0803 corre por tiempo fijo ($3\text{ s}$). Si se atasca mecánicamente, el puente H seguirá aplicando corriente al motor de stall, calentándolo.
    *   **Sensores NTC expuestos:** Si la línea de tierra analógica de los NTC se contamina con corrientes de retorno de potencia del extractor de 48V, las lecturas ADC se verán gravemente alteradas a pesar del filtrado por software.

---

## 3. Uso de AI (AI Log)

Se documenta de forma transparente el uso del modelo **Claude 3.5 Sonnet** (a través de Antigravity):

| Fecha | Propósito | Prompt / Tarea | Resultado / Corrección aplicada |
| :--- | :--- | :--- | :--- |
| 2026-06-30 | Validación de Código y Análisis de Bugs | "Revisar la implementación del firmware y compararlo con instrucciones.txt" | Se identificaron dos bugs de diseño: la omisión del buffer circular analógico y los límites de temperatura incorrectos en `adc_ntc.py`. Se aplicó la refactorización correspondiente. |
| 2026-06-30 | Diseño del conexionado de simulación | "Generar las conexiones del archivo diagram.json para Wokwi" | Se calculó el ruteado de cables en formato JSON para Wokwi, incluyendo el truco de LEDs en antiparalelo para emular el sentido de giro del actuador lineal. |
| 2026-06-30 | Testing Automatizado | "Crear un runner de pruebas locales con mocks de MicroPython" | Se implementaron los archivos `mock_machine.py`, `mock_time.py` y `test_firmware.py` para validar el firmware en el host Windows sin necesidad de hardware físico. |
