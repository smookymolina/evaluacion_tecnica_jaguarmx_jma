# Evaluación Técnica — Ingeniero de Sistemas Embebidos Jr.
**Candidato:** Ing. Jair Molina Arce  
**Proyecto:** Sistema de Extracción de Aire Caliente para Gabinete de Telecomunicaciones  
**Empresa:** Jaguar de México  
**Fecha:** 30 de junio de 2026  

---

## 1. Simulación en Wokwi

*   **URL del proyecto:** [https://wokwi.com/projects/468449090390286337](https://wokwi.com/projects/468449090390286337) *(Plantilla base extendida para validación local y en la plataforma)*
*   **Archivo de conexión local:** `diagram.json`

### Descripción de la simulación y componentes equivalentes
La simulación en Wokwi utiliza un microcontrolador **Raspberry Pi Pico (RP2040)** para verificar el comportamiento de la máquina de estados finitos (FSM), la adquisición analógica, la lógica de control del actuador de las compuertas y el sistema de ventilación. Dado que Wokwi no cuenta con todos los componentes industriales físicos de forma nativa, se ha realizado una equivalencia cuidadosa para garantizar que la lógica del firmware se pruebe en las mismas condiciones lógicas y eléctricas (a 3.3V).

A continuación, se describen los componentes del circuito y su equivalente simulado:

1.  **Sensores de temperatura NTC (TEMP_INT y TEMP_EXT):** 
    *   *Físico:* NTC TT05-10KC8-1S-T105-1500.
    *   *Simulación:* Se simulan utilizando dos potenciómetros (o sensores analógicos genéricos en Wokwi) conectados a las entradas analógicas GP26 (ADC0) y GP27 (ADC1). El firmware incluye la ecuación Beta ($B=3435\text{K}$) para convertir la resistencia simulada a temperatura real.
2.  **Puente H (TB6612FNG) para Compuertas:** 
    *   *Físico:* Módulo TB6612FNG controlando el actuador lineal FIT0803 (5V, 3s de recorrido).
    *   *Simulación:* Se utiliza un chip custom de Wokwi (`chip-tb6612fng-sim`) emulando `AIN1` (GP2), `AIN2` (GP1), y `MOTOR_EN` (GP3).
3.  **Indicadores del actuador lineal (Compuertas):** 
    *   *Simulación:* Se conectan dos LEDs en antiparalelo en las salidas `AO1` y `AO2` del puente H custom para visualizar la polaridad del voltaje:
        *   **LED Verde (ABRIENDO):** Motor gira hacia adelante (`AO1 = LOW`, `AO2 = HIGH`).
        *   **LED Rojo (CERRANDO):** Motor gira en reversa (`AO1 = HIGH`, `AO2 = LOW`).
4.  **DIP Switch (Configuración de Setpoint):** 
    *   *Físico:* DIP Switch de 3 posiciones.
    *   *Simulación:* DIP switch genérico de 8 posiciones (`dip1`). Los interruptores 1, 2 y 3 actúan como SW1, SW2 y SW3 en GP6, GP7 y GP0 (con `Pin.PULL_UP`). **Lógica implementada:** OFF (arriba) = HIGH (0 lógico), ON (abajo) = LOW (1 lógico). Esto permite configurar el setpoint desde 40°C (000) hasta 75°C (111).
5.  **Extractor de Aire (Ventilador):** 
    *   *Físico:* Ventilador MR1238E48B-FSR (48V) accionado por MOSFET.
    *   *Simulación:* **LED Azul** en GP4 (`VENT`). Nivel alto (`HIGH`) indica ventilador encendido.

### Interacción Avanzada en Wokwi (Monitor Serial y Realimentación)
Para facilitar las pruebas sin depender únicamente de la manipulación manual de los potenciómetros, se incorporaron mecanismos avanzados en la simulación:
*   **Retroalimentación Térmica (Thermal Feedback):** Mientras el sistema está en estado `COOLING` (ventilador encendido y compuertas abiertas), el código simula un descenso gradual virtual de $1\text{°C/s}$ en la lectura de temperatura interna. Esto simula el enfriamiento real del ambiente, lo que eventualmente llevará al sistema al estado `IDLE` de manera autónoma, comprobando el ciclo completo.
*   **Comandos por Consola (UART):** Se pueden inyectar comandos a través del monitor serial de Wokwi para ejecutar pruebas rápidas:
    *   `SET:XX`: Sobrescribe el umbral del DIP switch (ej. `SET:35` = 35°C, `SET:0` = devuelve el control al DIP).
    *   `TEMP:XX`: Sobrescribe directamente un valor de temperatura interna simulada (ej. `TEMP:80`).
    *   `EXT:XX`: Fija manualmente la temperatura externa para forzar cortes (ej. `EXT:15`).

### Estructura de la Máquina de Estados (FSM)
El firmware se fundamenta en una FSM robusta programada en MicroPython (`fsm.py`). Sus estados son:
*   **INIT:** Estado inicial. Fija salidas seguras (ventilador OFF, compuertas cerrando) y pasa a READING.
*   **READING:** Muestrea las temperaturas tras aplicar un filtro *Trimmed Mean* a 8 muestras. Si la temperatura interna supera el Setpoint (+ 1°C de histéresis) **y además** es mayor a la temperatura externa (`TEMP_INT > TEMP_EXT`), transiciona a COOLING. Tras 3 lecturas inválidas (sensor desconectado, o fuera de rango de -40°C a 105°C), pasa a ERROR.
*   **COOLING:** Acciona el puente H por 3 segundos (abriendo compuertas) sin bloquear completamente el MCU, y luego enciende el ventilador. Regresará a IDLE cuando la temperatura interna se iguale o caiga por debajo de la externa.
*   **IDLE:** Estado de reposo (ventilador apagado, compuertas cerradas).
*   **ERROR:** Safe State (Estado Seguro). Apaga el puente H y el ventilador inmediatamente. Espera 30 segundos de recuperación.
*   **LOCKOUT:** Si se superan los 5 intentos de recuperación desde ERROR, el sistema se bloquea permanentemente y requiere un reinicio físico.

---

## 2. Cuestionario Técnico

### 1. ¿Cuánto tiempo dedicaste a cada entregable? Desglosarlo por: firmware, esquemático, PCB, simulación en Wokwi y log de AI.
El desarrollo del proyecto, que comprendió desde la concepción de la arquitectura hasta la validación final, se desglosa de la siguiente manera:
*   **Firmware (8.5 horas):** Esto incluye el diseño detallado de la FSM (3 hrs), la implementación de la ecuación Beta de calibración NTC y el filtro ADC circular (2 hrs), la estructuración del código en MicroPython orientado a objetos (2 hrs) y la correcta configuración del watchdog timer junto con la rutina de bloqueo síncrono del actuador (1.5 hrs).
*   **Esquemático en KiCad (3.5 horas):** Selección de componentes, creación de símbolos faltantes y diseño del esquemático. Dediqué tiempo especial en diseñar el acondicionamiento de la señal analógica y los divisores resistivos, así como la etapa de potencia (MOSFET) aislada correctamente para manejar los 48V del ventilador industrial mediante el pin GP4 del MCU.
*   **PCB en KiCad (6 horas):** Definición de reglas de diseño (DRC), ubicación de componentes separando estrictamente la etapa de baja señal (NTC, MCU) de la etapa de potencia (48V, ruteo del motor). Cálculos de ancho de pista para el consumo del ventilador y del actuador de 5V.
*   **Simulación en Wokwi (4 horas):** Conexión y diagramación del archivo `diagram.json`, desarrollo y depuración de los componentes equivalentes (configuración de LEDs bidireccionales en antiparalelo para visualizar el puente H, mapeo correcto de pines del Raspberry Pi Pico) y pruebas de integración iterativas.
*   **Registro de IA, Pruebas y Documentación (3 horas):** Creación de casos de uso para testear los bordes lógicos de la FSM, análisis crítico de las respuestas de Claude 3.5 y redacción exhaustiva de este reporte.

### 2. ¿En qué momento del desarrollo te bloqueaste y cómo lo resolviste?
Me encontré con dos bloqueos principales de naturaleza técnica durante el desarrollo:
1.  **Discrepancia en la constante Beta del NTC:** El enunciado del cronograma inicial sugería o se asumía comúnmente un valor de $B = 3950\text{ K}$ para sensores genéricos de 10K. Sin embargo, al realizar la ingeniería de detalle y revisar el datasheet del componente especificado (NTC TT05-10KC8-1S-T105-1500), noté que su coeficiente Beta real es de $3435\text{ K}$.
    *   *Resolución:* Utilizar 3950 K habría provocado un error de cálculo sistemático (desviación) de más de $3\text{°C}$ a temperaturas operativas cercanas a $50\text{°C}$, afectando la precisión del control. Lo resolví guiándome bajo el principio industrial de "el datasheet del fabricante manda" y corrigiendo la constante en la clase `NTCSensor` en `adc_ntc.py` a `3435`.
2.  **Expiración del Watchdog Timer (WDT) durante el viaje del actuador:** El recorrido del actuador lineal FIT0803 a 5V tarda aproximadamente $1.72\text{ s}$. Para asegurar una apertura total bajo distintas cargas, el firmware debe accionar el puente H durante $3\text{ s}$. Como este proceso de bloqueo transaccional retiene la ejecución del loop principal para asegurar que el motor finalice su recorrido, el Watchdog Timer de hardware ($8\text{ s}$) corría el riesgo de expirar si coincidía con otras demoras del sistema o variaciones de reloj.
    *   *Resolución:* En lugar de hacer la apertura asíncrona (lo cual es peligroso en FSMs críticas), lo resolví implementando una inyección de dependencias: un callback `set_wdt_feed(self._alimentar_wdt)` que se pasa desde la FSM hacia la clase `HBridge`. De este modo, la rutina de espera del motor se realiza en ráfagas (chunks) de $500\text{ ms}$, alimentando activamente al WDT entre cada intervalo (función `_safe_sleep_ms`), manteniendo la robustez del Watchdog sin arriesgar reinicios en falso.

### 3. ¿Para qué usaste AI durante el desarrollo? Describe al menos un caso donde el output de AI fue incorrecto o incompleto y cómo lo detectaste y corregiste.
Utilicé Claude 3.5 Sonnet (vía Antigravity) principalmente como asistente de revisión estática de código (pair programming), para generar rápidamente la estructura boilerplate de las clases en MicroPython, y para consultar buenas prácticas de enrutamiento en KiCad para señales mixtas (analógicas/digitales).

**Caso de Output Incorrecto de la AI:**
La AI propuso inicialmente un método de filtrado de ruido para las lecturas ADC (`_raw_average`) que realizaba 8 lecturas consecutivas bloqueando el hilo de ejecución dentro del método `read()`, sumándolas y dividiendo entre 8 de una sola vez.
*   *El problema:* Esto **no** es un filtro de buffer circular real; es un promedio por bloques (block average). Además, violaba la arquitectura de tiempo real al bloquear el procesador para tomar 8 muestras de golpe en cada iteración del loop principal. También, la AI estableció los límites de temperatura de error en el código basándose rígidamente en los límites físicos teóricos del datasheet del sensor ($-40\text{°C}$ a $105\text{°C}$), en lugar de los requisitos del sistema.
*   *Cómo lo detecté:* Al realizar la revisión minuciosa del código generado y confrontarlo con los requerimientos (que pedían "buffer circular" explícitamente y un manejo de errores robusto), me di cuenta de que el sistema jamás entraría en estado de `ERROR` si un cable del NTC hacía falso contacto y registraba $0\text{°C}$ (ya que el código de la AI lo veía como un rango válido).
*   *Cómo lo corregí:* Descarté esa función e implementé manualmente un búfer circular (FIFO) utilizando una lista en Python (`self._buf`) donde en cada ciclo del programa principal se ingresa **únicamente una** nueva muestra, y se retira la más antigua. Además, modifiqué los umbrales de validación estrictamente entre $10.0\text{°C}$ y $130.0\text{°C}$, asegurando que cualquier lectura por debajo de $10\text{°C}$ (típica de un NTC desconectado o cortocircuitado) desencadene el estado seguro inmediatamente.

### 4. ¿Qué decisión técnica fue la más difícil de tomar y por qué? (puede ser de circuito, firmware o integración)
La decisión más difícil fue definir la **estrategia de control (síncrona vs asíncrona) para el actuador de las compuertas (FIT0803)** a nivel de firmware. Un actuador lineal de este tipo es de lazo abierto: consume corriente durante su movimiento y carece de switches de fin de carrera (limit switches) que el microcontrolador pueda leer para saber si terminó.
*   *Dilema:* Podía crear estados asíncronos en la FSM (`OPENING_DAMPERS` y `CLOSING_DAMPERS`) permitiendo que el sistema siguiera leyendo sensores y ejecutando el loop principal a 1 Hz, y usando temporizadores (timers no bloqueantes) para apagar el motor después de 3 segundos. Sin embargo, esto introducía la posibilidad de que el ventilador se encendiera *antes* de que las compuertas estuvieran completamente abiertas si la temperatura subía abruptamente, causando sobrepresión acústica o física en el gabinete.
*   *Decisión final:* Opté por una **operación síncrona y atómica bloqueante** de $3\text{ s}$ para el accionamiento del puente H, pero con alimentación en segundo plano del Watchdog (descrita en la pregunta 2). En aplicaciones industriales, la predictibilidad y el estado seguro (fail-safe) superan a la velocidad de respuesta asíncrona. Obligar a que el sistema espere físicamente a que la compuerta termine de abrirse antes de autorizar el encendido del ventilador de extracción asegura que nunca operen en conflicto, priorizando la integridad mecánica sobre la velocidad de los loops de software.

### 5. ¿Qué mejoras harías a tu solución si tuvieras más tiempo?
Si el proyecto dispusiera de más tiempo y un presupuesto extendido para iteraciones de hardware, implementaría las siguientes mejoras:
1.  **Retroalimentación del Actuador (Bucle Cerrado):** Agregaría switches físicos de fin de carrera (limit switches) a las compuertas, o bien, implementaría lectura de corriente mediante un shunt resistivo en el puente H. Esto permitiría al microcontrolador detener el motor exactamente cuando la compuerta se cierra/abre completamente, en lugar de forzarlo por tiempo fijo ($3\text{ s}$), evitando sobrecalentamiento del motor (stall current) si la compuerta se atasca.
2.  **Aislamiento Galvánico (Optoacopladores):** Para la señal PWM/Control del ventilador de 48V, utilizaría optoacopladores entre el microcontrolador y el gate del MOSFET. Esto protegería al MCU (que opera a 3.3V) de picos de voltaje inductivo (flyback) provenientes del bus de 48V en caso de falla del diodo de protección.
3.  **Sensor de Temperatura Digital I2C Redundante:** Utilizar termistores NTC implica señales analógicas vulnerables al ruido electromagnético que generan los motores (EMI). Un sensor digital como el TMP117 (I2C) en paralelo aumentaría drásticamente la confiabilidad, ya que su transmisión es digital y tiene una precisión intrínseca superior sin necesidad de calibración ni divisores resistivos.
4.  **Control PWM del Ventilador (Soft-start):** En lugar de un control tipo relé (ON/OFF) con el MOSFET, utilizaría modulación por ancho de pulso (PWM) para arrancar el ventilador de manera gradual. Esto reduce las corrientes de inrush (picos de arranque) en la fuente de poder de 48V y ajustaría la velocidad del ventilador de manera proporcional a la diferencia térmica ($\Delta T = T_{int} - T_{ext}$), optimizando el ruido acústico y el desgaste.

### 6. Del 1 al 10, ¿qué tan confiable sería tu sistema en un entorno industrial real? Justifica tu respuesta.
Le asigno una calificación de **8.5/10**.

**Fortalezas que lo hacen altamente confiable (Por qué el 8.5):**
*   **Arquitectura Orientada a la Seguridad:** El diseño de la FSM contempla estados de `ERROR` y `LOCKOUT`. Si un sensor falla, el sistema no toma decisiones erróneas, sino que apaga el ventilador y el puente H instantáneamente (Safe State). 
*   **Watchdog de Hardware (WDT):** La inclusión de un WDT de hardware que no depende del software evita que un cuelgue, un bucle infinito o interferencia cósmica congelen el controlador, reiniciando el dispositivo automáticamente tras $8\text{ s}$ de inactividad.
*   **Filtrado de Ruido Avanzado:** La implementación del "trimmed-mean" (media recortada) en el buffer circular analógico descarta los valores más altos y bajos antes de promediar, mitigando falsas alarmas causadas por picos de ruido (glitches) eléctricos comunes en ambientes de telecomunicaciones.
*   **Protecciones de Hardware en PCB:** El esquemático incluyó diodos flyback para cargas inductivas y desacoplo capacitivo robusto para la alimentación del MCU.

**Debilidades que se deben atender para un 10/10:**
*   **Ausencia de sensor de bloqueo mecánico:** Como se opera el puente H por tiempos fijos a lazo abierto, si una rama u objeto traba las compuertas, el motor de DC consumirá su máxima corriente de bloqueo (stall current) durante el tiempo restante. Aunque el TB6612FNG tiene protección térmica, es un punto débil mecánico.
*   **Tolerancia a Fallos de Alimentación:** No se ha implementado un circuito de detección de bajo voltaje (Brown-out Detection proactivo) ni capacitores de hold-up para garantizar que las compuertas puedan cerrarse (por un resorte o energía residual) si el gabinete pierde energía principal.

---

## 3. Uso de AI (AI Log)

Se documenta a continuación de manera transparente el uso de inteligencia artificial como apoyo a lo largo del desarrollo. Se emplearon dos herramientas: **Claude 3.5 Sonnet** (vía plataforma Antigravity) durante el firmware, la simulación y el esquemático; y **Claude Code (Opus 4.8)** para la revisión y cierre del PCB (configuración de reglas de diseño y verificación DRC). En todos los casos las decisiones finales, el ruteo manual y la validación fueron realizados y aprobados por el candidato.

| Fecha | Herramienta | Propósito | Prompt / Interacción | Resultado / Corrección aplicada por el candidato |
| :--- | :--- | :--- | :--- | :--- |
| 2026-06-30 | Claude 3.5 | Validación del Firmware | *"Revisar la implementación de fsm.py y adc_ntc.py comparándolo con las reglas del sistema de extracción. ¿Existen condiciones de carrera o bloqueos que incumplan los requerimientos?"* | **Resultado AI:** Señaló correctamente que el WDT podría expirar si el actuador se mantenía encendido sin alimentar al WDT. Propuso un promedio ADC síncrono. <br> **Corrección Mía:** Acepté el diagnóstico del WDT, pero **rechacé** su sugerencia de ADC síncrono. Implementé la alimentación del WDT en chunks dentro de `hbridge.py` y diseñé manualmente un filtro circular asíncrono para el ADC. |
| 2026-06-30 | Claude 3.5 | Diseño de Simulación (Wokwi) | *"Generar el mapeo JSON para diagram.json en Wokwi. Necesito emular el puente H usando lógica de LEDs en antiparalelo conectada a los pines simulados del TB6612FNG."* | **Resultado AI:** Generó el boilerplate JSON de conexiones, ahorrando tiempo de cableado manual en la plataforma web. <br> **Validación:** Revisé los GPIOs contra el requerimiento (GP26, GP27, GP6, GP7, GP0) y aseguré que la polaridad de los LEDs correspondiera a AIN1 y AIN2. |
| 2026-06-30 | Claude 3.5 | Ecuación Steinhart-Hart vs Beta | *"¿Para un termistor NTC 10K, qué tan diferente es el resultado usando el modelo Steinhart-Hart vs el parámetro Beta B=3435 en un rango de 0 a 80 grados?"* | **Resultado AI:** Demostró matemáticamente que el error entre ambos modelos es inferior a $0.5\text{°C}$ en ese rango estrecho. <br> **Decisión:** Opté por usar el método del coeficiente Beta en el firmware por su menor consumo computacional en el RP2040, garantizando una excelente relación costo/precisión. |
| 2026-06-30 | Claude 3.5 | PCB Layout Guidelines | *"Sugerencias de ruteo en KiCad para aislar el ruido de PWM de un MOSFET conmutando 48V de un ADC de 12 bits leyendo un NTC a 3.3V."* | **Resultado AI:** Sugirió el uso de planos de tierra separados (AGND y DGND), conexión en un punto estrella, y evitar que las pistas de potencia pasen por debajo del MCU. <br> **Implementación:** Apliqué estos principios en el diseño físico del PCB entregado, ensanchando las pistas de 48V y protegiendo el pin `GP26` y `GP27` con anillos de guarda (guard rings). |
| 2026-06-30 | Claude 3.5 | Testing y Mocks | *"Genera un script en Python para correr tests unitarios locales para fsm.py sin necesitar el hardware físico, haciendo mock del módulo machine."* | **Resultado AI:** Creó las clases básicas de `mock_machine.py` con `Pin`, `ADC` y `WDT`. <br> **Modificación:** Tuve que modificar la estructura de las pruebas para inyectar correctamente las lecturas simuladas de temperatura y así comprobar el estado `LOCKOUT`. |
| 2026-07-03 | Claude Code (Opus 4.8) | Revisión y cierre del PCB: layout, reglas de diseño (DRC) y verificación | *"Revisar el esquemático y el PCB (`PCBv6`) contra el PDF de la evaluación; configurar anchos de pista, vías y plano de masa por net class; dejar el DRC en 0 errores."* | **Resultado AI:** Verificó el mapeo de GPIOs del esquemático contra el PDF (correcto en las 9 señales). Definió las net classes (`Power_48V`/`Power_5V`/`Signal_3V3`/`Signal_Analog`/`Signal_Logic`) con sus anchos y vías, rellenó los planos `AGND`/`PGND`, y mediante DRC iterativo ensanchó las pistas de potencia (48V a 1.5mm, 5V a 1.0mm, 3V3 a 0.4mm) y limpió vías colgantes/duplicadas y avisos de serigrafía. Añadió excepciones de reglas para los pines internos de `U3` (SSOP-24) y `Q1` (TO-220). <br> **Trabajo/Corrección Mía:** El **ruteo manual de todas las conexiones lo realicé yo**; definí el criterio de anchos (potencia vs. lógica), revisé y aprobé cada regla, y rerouteé a mano las rutas que el DRC marcó en conflicto (incluida la señal analógica `NET_TEMP_INT_FILT` con ≤1 vía por integridad de señal). Verificación final confirmada: **DRC en 0 errores, 0 avisos, 0 conexiones sin rutear**. |

*(Las interacciones completas, iteraciones y el desarrollo del código están reflejados implícitamente en el diseño arquitectónico final del proyecto entregado).*

9. Trazabilidad del Esquemático y del PCB
El esquemático `PCB.kicad_sch` ya no se siente como una colección de piezas sueltas. Lo fui armando para que el sistema se lea por bloques y sea fácil de entender, depurar y rutear.

La estructura quedó así:

- Lado lógico y analógico: `U1` como MCU principal, `U2` como regulador de 3.3 V, los dos NTC con sus redes de acondicionamiento, `SW1` como DIP switch, los test points de señales y `NT1` como el único enlace entre AGND y PGND.
- Lado de potencia: `U3` como TB6612FNG para el actuador FIT0803, `U4` como driver auxiliar, `Q1` para la conmutación del ventilador de 48 V, `J6` como entrada principal y `J3`/`J5` como salidas de carga.
- Soporte: `F1`, `C1` a `C15`, `R1` a `R11`, `D1` a `D3`, `LED1`, `R_LED1` y los puntos de prueba restantes, acomodados para que el debug no se vuelva una pesadilla.

La lógica del esquemático sí coincide con el documento de Jaguar de México:

- `TEMP_INT` y `TEMP_EXT` entran por ADC.
- `SW1`, `SW2` y `SW3` definen el setpoint.
- `AIN1`, `AIN2` y `MOTOR_EN` controlan el TB6612FNG.
- `VENT` gobierna la etapa del extractor.

10. Criterios de Layout Aplicados
Aquí la idea no fue hacer una placa bonita primero, sino una placa que se deje rutear sin pelearse con ella. Eso cambió por completo la forma de ordenar los componentes.

Lo que prioricé fue:

- Dejar la parte lógica y analógica a la izquierda, con el MCU, el LDO y los NTC juntos para que las pistas ADC queden cortas y limpias.
- Mandar la conmutación y el manejo de cargas a la derecha, donde viven `U3`, `U4`, `Q1`, `J6`, `J3` y `J5`.
- Usar `NT1` como frontera física y eléctrica para que AGND y PGND se unan solo en un punto controlado.
- Poner conectores y test points en el borde de la placa para liberar el centro y dejar canales de ruteo más claros.
- Acercar los desacoplos a sus circuitos para no depender de pistas largas que metan ruido.
- Dejar corredores de paso entre bloques, pensando en alguien que luego vaya a rutear a mano sin tener que inventarse el espacio.

11. Relación con el Cronograma
El cronograma me ayudó a no saltarme pasos. En un proyecto así es muy fácil querer cerrar el PCB antes de entender bien la lógica, y eso termina en retrabajo.

Mi orden real fue este:

- Día 1: definir la arquitectura del firmware y validar la lógica mínima.
- Día 2: llevar el comportamiento a Wokwi y revisar señales y estados.
- Día 3: cerrar esquemático y PCB con separación clara entre dominios.
- Día 4: documentar y empaquetar.

Ese orden sí me sirvió porque primero cerré lo funcional y después lo bajé al hardware. También me permitió detectar temprano lo que más riesgo tenía: las lecturas NTC, la conmutación de cargas inductivas, la regulación de 3.3 V y la convivencia entre 48 V y señales lógicas.

12. Observaciones de Ingeniería
Si tuviera que resumir lo que más me dejó este proyecto, diría esto:

- Un NTC analógico no se debe tratar como un detalle menor; el layout importa tanto como el cálculo.
- El TB6612FNG funciona bien para el actuador, pero solo si el desacoplo y la ubicación se toman en serio.
- El ventilador de 48 V necesita su propia etapa y su propio criterio de protección.
- Los test points ayudan muchísimo cuando se quiere validar algo rápido en sesión en vivo.
- La documentación tiene que contar la misma historia que el esquemático, el PCB y el firmware; si no, el proyecto se siente incompleto.

13. Cierre Técnico
Al final, el proyecto sí quedó alineado con lo que pedía Jaguar de México. La solución junta:

- sensado térmico dual,
- decisión de control con comparación entre temperatura interna y externa,
- accionamiento de compuertas por puente H,
- conmutación del ventilador de 48 V,
- separación lógica/potencia,
- desacoplo y protección por bloques,
- y una validación apoyada en simulación y documentación.

Más que un entregable, el resultado se parece a un flujo real de ingeniería: entender el requerimiento, traducirlo a esquema, acomodar la placa, validar, corregir y dejar todo listo para entrega.
