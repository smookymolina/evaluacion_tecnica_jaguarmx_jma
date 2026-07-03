# EvaluaciÃ³n TÃ©cnica â€” Ingeniero de Sistemas Embebidos Jr.
**Candidato:** Ing. Jair Molina Arce  
**Proyecto:** Sistema de ExtracciÃ³n de Aire Caliente para Gabinete de Telecomunicaciones  
**Empresa:** Jaguar de MÃ©xico  
**Fecha:** 30 de junio de 2026  

---

## 1. SimulaciÃ³n en Wokwi

*   **URL del proyecto:** [https://wokwi.com/projects/468449090390286337](https://wokwi.com/projects/468449090390286337) *(Plantilla base extendida para validaciÃ³n local y en la plataforma)*
*   **Archivo de conexiÃ³n local:** `diagram.json`

### DescripciÃ³n de la simulaciÃ³n y componentes equivalentes
La simulaciÃ³n en Wokwi utiliza un microcontrolador **Raspberry Pi Pico (RP2040)** para verificar el comportamiento de la mÃ¡quina de estados finitos (FSM), la adquisiciÃ³n analÃ³gica, la lÃ³gica de control del actuador de las compuertas y el sistema de ventilaciÃ³n. Dado que Wokwi no cuenta con todos los componentes industriales fÃ­sicos de forma nativa, se ha realizado una equivalencia cuidadosa para garantizar que la lÃ³gica del firmware se pruebe en las mismas condiciones lÃ³gicas y elÃ©ctricas (a 3.3V).

A continuaciÃ³n, se describen los componentes del circuito y su equivalente simulado:

1.  **Sensores de temperatura NTC (TEMP_INT y TEMP_EXT):** 
    *   *FÃ­sico:* NTC TT05-10KC8-1S-T105-1500.
    *   *SimulaciÃ³n:* Se simulan utilizando dos potenciÃ³metros (o sensores analÃ³gicos genÃ©ricos en Wokwi) conectados a las entradas analÃ³gicas GP26 (ADC0) y GP27 (ADC1). El firmware incluye la ecuaciÃ³n Beta ($B=3435\text{K}$) para convertir la resistencia simulada a temperatura real.
2.  **Puente H (TB6612FNG) para Compuertas:** 
    *   *FÃ­sico:* MÃ³dulo TB6612FNG controlando el actuador lineal FIT0803 (5V, 3s de recorrido).
    *   *SimulaciÃ³n:* Se utiliza un chip custom de Wokwi (`chip-tb6612fng-sim`) emulando `AIN1` (GP2), `AIN2` (GP1), y `MOTOR_EN` (GP3).
3.  **Indicadores del actuador lineal (Compuertas):** 
    *   *SimulaciÃ³n:* Se conectan dos LEDs en antiparalelo en las salidas `AO1` y `AO2` del puente H custom para visualizar la polaridad del voltaje:
        *   **LED Verde (ABRIENDO):** Motor gira hacia adelante (`AO1 = LOW`, `AO2 = HIGH`).
        *   **LED Rojo (CERRANDO):** Motor gira en reversa (`AO1 = HIGH`, `AO2 = LOW`).
4.  **DIP Switch (ConfiguraciÃ³n de Setpoint):** 
    *   *FÃ­sico:* DIP Switch de 3 posiciones.
    *   *SimulaciÃ³n:* DIP switch genÃ©rico de 8 posiciones (`dip1`). Los interruptores 1, 2 y 3 actÃºan como SW1, SW2 y SW3 en GP6, GP7 y GP0 (con `Pin.PULL_UP`). **LÃ³gica implementada:** OFF (arriba) = HIGH (0 lÃ³gico), ON (abajo) = LOW (1 lÃ³gico). Esto permite configurar el setpoint desde 40Â°C (000) hasta 75Â°C (111).
5.  **Extractor de Aire (Ventilador):** 
    *   *FÃ­sico:* Ventilador MR1238E48B-FSR (48V) accionado por MOSFET.
    *   *SimulaciÃ³n:* **LED Azul** en GP4 (`VENT`). Nivel alto (`HIGH`) indica ventilador encendido.

### InteracciÃ³n Avanzada en Wokwi (Monitor Serial y RealimentaciÃ³n)
Para facilitar las pruebas sin depender Ãºnicamente de la manipulaciÃ³n manual de los potenciÃ³metros, se incorporaron mecanismos avanzados en la simulaciÃ³n:
*   **RetroalimentaciÃ³n TÃ©rmica (Thermal Feedback):** Mientras el sistema estÃ¡ en estado `COOLING` (ventilador encendido y compuertas abiertas), el cÃ³digo simula un descenso gradual virtual de $1\text{Â°C/s}$ en la lectura de temperatura interna. Esto simula el enfriamiento real del ambiente, lo que eventualmente llevarÃ¡ al sistema al estado `IDLE` de manera autÃ³noma, comprobando el ciclo completo.
*   **Comandos por Consola (UART):** Se pueden inyectar comandos a travÃ©s del monitor serial de Wokwi para ejecutar pruebas rÃ¡pidas:
    *   `SET:XX`: Sobrescribe el umbral del DIP switch (ej. `SET:35` = 35Â°C, `SET:0` = devuelve el control al DIP).
    *   `TEMP:XX`: Sobrescribe directamente un valor de temperatura interna simulada (ej. `TEMP:80`).
    *   `EXT:XX`: Fija manualmente la temperatura externa para forzar cortes (ej. `EXT:15`).

### Estructura de la MÃ¡quina de Estados (FSM)
El firmware se fundamenta en una FSM robusta programada en MicroPython (`fsm.py`). Sus estados son:
*   **INIT:** Estado inicial. Fija salidas seguras (ventilador OFF, compuertas cerrando) y pasa a READING.
*   **READING:** Muestrea las temperaturas tras aplicar un filtro *Trimmed Mean* a 8 muestras. Si la temperatura interna supera el Setpoint (+ 1Â°C de histÃ©resis) **y ademÃ¡s** es mayor a la temperatura externa (`TEMP_INT > TEMP_EXT`), transiciona a COOLING. Tras 3 lecturas invÃ¡lidas (sensor desconectado, o fuera de rango de -40Â°C a 105Â°C), pasa a ERROR.
*   **COOLING:** Acciona el puente H por 3 segundos (abriendo compuertas) sin bloquear completamente el MCU, y luego enciende el ventilador. RegresarÃ¡ a IDLE cuando la temperatura interna se iguale o caiga por debajo de la externa.
*   **IDLE:** Estado de reposo (ventilador apagado, compuertas cerradas).
*   **ERROR:** Safe State (Estado Seguro). Apaga el puente H y el ventilador inmediatamente. Espera 30 segundos de recuperaciÃ³n.
*   **LOCKOUT:** Si se superan los 5 intentos de recuperaciÃ³n desde ERROR, el sistema se bloquea permanentemente y requiere un reinicio fÃ­sico.

---

## 2. Cuestionario TÃ©cnico

### 1. Â¿CuÃ¡nto tiempo dedicaste a cada entregable? Desglosarlo por: firmware, esquemÃ¡tico, PCB, simulaciÃ³n en Wokwi y log de AI.
El desarrollo del proyecto, que comprendiÃ³ desde la concepciÃ³n de la arquitectura hasta la validaciÃ³n final, se desglosa de la siguiente manera:
*   **Firmware (8.5 horas):** Esto incluye el diseÃ±o detallado de la FSM (3 hrs), la implementaciÃ³n de la ecuaciÃ³n Beta de calibraciÃ³n NTC y el filtro ADC circular (2 hrs), la estructuraciÃ³n del cÃ³digo en MicroPython orientado a objetos (2 hrs) y la correcta configuraciÃ³n del watchdog timer junto con la rutina de bloqueo sÃ­ncrono del actuador (1.5 hrs).
*   **EsquemÃ¡tico en KiCad (3.5 horas):** SelecciÃ³n de componentes, creaciÃ³n de sÃ­mbolos faltantes y diseÃ±o del esquemÃ¡tico. DediquÃ© tiempo especial en diseÃ±ar el acondicionamiento de la seÃ±al analÃ³gica y los divisores resistivos, asÃ­ como la etapa de potencia (MOSFET) aislada correctamente para manejar los 48V del ventilador industrial mediante el pin GP4 del MCU.
*   **PCB en KiCad (6 horas):** DefiniciÃ³n de reglas de diseÃ±o (DRC), ubicaciÃ³n de componentes separando estrictamente la etapa de baja seÃ±al (NTC, MCU) de la etapa de potencia (48V, ruteo del motor). CÃ¡lculos de ancho de pista para el consumo del ventilador y del actuador de 5V.
*   **SimulaciÃ³n en Wokwi (4 horas):** ConexiÃ³n y diagramaciÃ³n del archivo `diagram.json`, desarrollo y depuraciÃ³n de los componentes equivalentes (configuraciÃ³n de LEDs bidireccionales en antiparalelo para visualizar el puente H, mapeo correcto de pines del Raspberry Pi Pico) y pruebas de integraciÃ³n iterativas.
*   **Registro de IA, Pruebas y DocumentaciÃ³n (3 horas):** CreaciÃ³n de casos de uso para testear los bordes lÃ³gicos de la FSM, anÃ¡lisis crÃ­tico de las respuestas de Claude 3.5 y redacciÃ³n exhaustiva de este reporte.

### 2. Â¿En quÃ© momento del desarrollo te bloqueaste y cÃ³mo lo resolviste?
Me encontrÃ© con dos bloqueos principales de naturaleza tÃ©cnica durante el desarrollo:
1.  **Discrepancia en la constante Beta del NTC:** El enunciado del cronograma inicial sugerÃ­a o se asumÃ­a comÃºnmente un valor de $B = 3950\text{ K}$ para sensores genÃ©ricos de 10K. Sin embargo, al realizar la ingenierÃ­a de detalle y revisar el datasheet del componente especificado (NTC TT05-10KC8-1S-T105-1500), notÃ© que su coeficiente Beta real es de $3435\text{ K}$.
    *   *ResoluciÃ³n:* Utilizar 3950 K habrÃ­a provocado un error de cÃ¡lculo sistemÃ¡tico (desviaciÃ³n) de mÃ¡s de $3\text{Â°C}$ a temperaturas operativas cercanas a $50\text{Â°C}$, afectando la precisiÃ³n del control. Lo resolvÃ­ guiÃ¡ndome bajo el principio industrial de "el datasheet del fabricante manda" y corrigiendo la constante en la clase `NTCSensor` en `adc_ntc.py` a `3435`.
2.  **ExpiraciÃ³n del Watchdog Timer (WDT) durante el viaje del actuador:** El recorrido del actuador lineal FIT0803 a 5V tarda aproximadamente $1.72\text{ s}$. Para asegurar una apertura total bajo distintas cargas, el firmware debe accionar el puente H durante $3\text{ s}$. Como este proceso de bloqueo transaccional retiene la ejecuciÃ³n del loop principal para asegurar que el motor finalice su recorrido, el Watchdog Timer de hardware ($8\text{ s}$) corrÃ­a el riesgo de expirar si coincidÃ­a con otras demoras del sistema o variaciones de reloj.
    *   *ResoluciÃ³n:* En lugar de hacer la apertura asÃ­ncrona (lo cual es peligroso en FSMs crÃ­ticas), lo resolvÃ­ implementando una inyecciÃ³n de dependencias: un callback `set_wdt_feed(self._alimentar_wdt)` que se pasa desde la FSM hacia la clase `HBridge`. De este modo, la rutina de espera del motor se realiza en rÃ¡fagas (chunks) de $500\text{ ms}$, alimentando activamente al WDT entre cada intervalo (funciÃ³n `_safe_sleep_ms`), manteniendo la robustez del Watchdog sin arriesgar reinicios en falso.

### 3. Â¿Para quÃ© usaste AI durante el desarrollo? Describe al menos un caso donde el output de AI fue incorrecto o incompleto y cÃ³mo lo detectaste y corregiste.
UtilicÃ© Claude 3.5 Sonnet (vÃ­a Antigravity) principalmente como asistente de revisiÃ³n estÃ¡tica de cÃ³digo (pair programming), para generar rÃ¡pidamente la estructura boilerplate de las clases en MicroPython, y para consultar buenas prÃ¡cticas de enrutamiento en KiCad para seÃ±ales mixtas (analÃ³gicas/digitales).

**Caso de Output Incorrecto de la AI:**
La AI propuso inicialmente un mÃ©todo de filtrado de ruido para las lecturas ADC (`_raw_average`) que realizaba 8 lecturas consecutivas bloqueando el hilo de ejecuciÃ³n dentro del mÃ©todo `read()`, sumÃ¡ndolas y dividiendo entre 8 de una sola vez.
*   *El problema:* Esto **no** es un filtro de buffer circular real; es un promedio por bloques (block average). AdemÃ¡s, violaba la arquitectura de tiempo real al bloquear el procesador para tomar 8 muestras de golpe en cada iteraciÃ³n del loop principal. TambiÃ©n, la AI estableciÃ³ los lÃ­mites de temperatura de error en el cÃ³digo basÃ¡ndose rÃ­gidamente en los lÃ­mites fÃ­sicos teÃ³ricos del datasheet del sensor ($-40\text{Â°C}$ a $105\text{Â°C}$), en lugar de los requisitos del sistema.
*   *CÃ³mo lo detectÃ©:* Al realizar la revisiÃ³n minuciosa del cÃ³digo generado y confrontarlo con los requerimientos (que pedÃ­an "buffer circular" explÃ­citamente y un manejo de errores robusto), me di cuenta de que el sistema jamÃ¡s entrarÃ­a en estado de `ERROR` si un cable del NTC hacÃ­a falso contacto y registraba $0\text{Â°C}$ (ya que el cÃ³digo de la AI lo veÃ­a como un rango vÃ¡lido).
*   *CÃ³mo lo corregÃ­:* DescartÃ© esa funciÃ³n e implementÃ© manualmente un bÃºfer circular (FIFO) utilizando una lista en Python (`self._buf`) donde en cada ciclo del programa principal se ingresa **Ãºnicamente una** nueva muestra, y se retira la mÃ¡s antigua. AdemÃ¡s, modifiquÃ© los umbrales de validaciÃ³n estrictamente entre $10.0\text{Â°C}$ y $130.0\text{Â°C}$, asegurando que cualquier lectura por debajo de $10\text{Â°C}$ (tÃ­pica de un NTC desconectado o cortocircuitado) desencadene el estado seguro inmediatamente.

### 4. Â¿QuÃ© decisiÃ³n tÃ©cnica fue la mÃ¡s difÃ­cil de tomar y por quÃ©? (puede ser de circuito, firmware o integraciÃ³n)
La decisiÃ³n mÃ¡s difÃ­cil fue definir la **estrategia de control (sÃ­ncrona vs asÃ­ncrona) para el actuador de las compuertas (FIT0803)** a nivel de firmware. Un actuador lineal de este tipo es de lazo abierto: consume corriente durante su movimiento y carece de switches de fin de carrera (limit switches) que el microcontrolador pueda leer para saber si terminÃ³.
*   *Dilema:* PodÃ­a crear estados asÃ­ncronos en la FSM (`OPENING_DAMPERS` y `CLOSING_DAMPERS`) permitiendo que el sistema siguiera leyendo sensores y ejecutando el loop principal a 1 Hz, y usando temporizadores (timers no bloqueantes) para apagar el motor despuÃ©s de 3 segundos. Sin embargo, esto introducÃ­a la posibilidad de que el ventilador se encendiera *antes* de que las compuertas estuvieran completamente abiertas si la temperatura subÃ­a abruptamente, causando sobrepresiÃ³n acÃºstica o fÃ­sica en el gabinete.
*   *DecisiÃ³n final:* OptÃ© por una **operaciÃ³n sÃ­ncrona y atÃ³mica bloqueante** de $3\text{ s}$ para el accionamiento del puente H, pero con alimentaciÃ³n en segundo plano del Watchdog (descrita en la pregunta 2). En aplicaciones industriales, la predictibilidad y el estado seguro (fail-safe) superan a la velocidad de respuesta asÃ­ncrona. Obligar a que el sistema espere fÃ­sicamente a que la compuerta termine de abrirse antes de autorizar el encendido del ventilador de extracciÃ³n asegura que nunca operen en conflicto, priorizando la integridad mecÃ¡nica sobre la velocidad de los loops de software.

### 5. Â¿QuÃ© mejoras harÃ­as a tu soluciÃ³n si tuvieras mÃ¡s tiempo?
Si el proyecto dispusiera de mÃ¡s tiempo y un presupuesto extendido para iteraciones de hardware, implementarÃ­a las siguientes mejoras:
1.  **RetroalimentaciÃ³n del Actuador (Bucle Cerrado):** AgregarÃ­a switches fÃ­sicos de fin de carrera (limit switches) a las compuertas, o bien, implementarÃ­a lectura de corriente mediante un shunt resistivo en el puente H. Esto permitirÃ­a al microcontrolador detener el motor exactamente cuando la compuerta se cierra/abre completamente, en lugar de forzarlo por tiempo fijo ($3\text{ s}$), evitando sobrecalentamiento del motor (stall current) si la compuerta se atasca.
2.  **Aislamiento GalvÃ¡nico (Optoacopladores):** Para la seÃ±al PWM/Control del ventilador de 48V, utilizarÃ­a optoacopladores entre el microcontrolador y el gate del MOSFET. Esto protegerÃ­a al MCU (que opera a 3.3V) de picos de voltaje inductivo (flyback) provenientes del bus de 48V en caso de falla del diodo de protecciÃ³n.
3.  **Sensor de Temperatura Digital I2C Redundante:** Utilizar termistores NTC implica seÃ±ales analÃ³gicas vulnerables al ruido electromagnÃ©tico que generan los motores (EMI). Un sensor digital como el TMP117 (I2C) en paralelo aumentarÃ­a drÃ¡sticamente la confiabilidad, ya que su transmisiÃ³n es digital y tiene una precisiÃ³n intrÃ­nseca superior sin necesidad de calibraciÃ³n ni divisores resistivos.
4.  **Control PWM del Ventilador (Soft-start):** En lugar de un control tipo relÃ© (ON/OFF) con el MOSFET, utilizarÃ­a modulaciÃ³n por ancho de pulso (PWM) para arrancar el ventilador de manera gradual. Esto reduce las corrientes de inrush (picos de arranque) en la fuente de poder de 48V y ajustarÃ­a la velocidad del ventilador de manera proporcional a la diferencia tÃ©rmica ($\Delta T = T_{int} - T_{ext}$), optimizando el ruido acÃºstico y el desgaste.

### 6. Del 1 al 10, Â¿quÃ© tan confiable serÃ­a tu sistema en un entorno industrial real? Justifica tu respuesta.
Le asigno una calificaciÃ³n de **8.5/10**.

**Fortalezas que lo hacen altamente confiable (Por quÃ© el 8.5):**
*   **Arquitectura Orientada a la Seguridad:** El diseÃ±o de la FSM contempla estados de `ERROR` y `LOCKOUT`. Si un sensor falla, el sistema no toma decisiones errÃ³neas, sino que apaga el ventilador y el puente H instantÃ¡neamente (Safe State). 
*   **Watchdog de Hardware (WDT):** La inclusiÃ³n de un WDT de hardware que no depende del software evita que un cuelgue, un bucle infinito o interferencia cÃ³smica congelen el controlador, reiniciando el dispositivo automÃ¡ticamente tras $8\text{ s}$ de inactividad.
*   **Filtrado de Ruido Avanzado:** La implementaciÃ³n del "trimmed-mean" (media recortada) en el buffer circular analÃ³gico descarta los valores mÃ¡s altos y bajos antes de promediar, mitigando falsas alarmas causadas por picos de ruido (glitches) elÃ©ctricos comunes en ambientes de telecomunicaciones.
*   **Protecciones de Hardware en PCB:** El esquemÃ¡tico incluyÃ³ diodos flyback para cargas inductivas y desacoplo capacitivo robusto para la alimentaciÃ³n del MCU.

**Debilidades que se deben atender para un 10/10:**
*   **Ausencia de sensor de bloqueo mecÃ¡nico:** Como se opera el puente H por tiempos fijos a lazo abierto, si una rama u objeto traba las compuertas, el motor de DC consumirÃ¡ su mÃ¡xima corriente de bloqueo (stall current) durante el tiempo restante. Aunque el TB6612FNG tiene protecciÃ³n tÃ©rmica, es un punto dÃ©bil mecÃ¡nico.
*   **Tolerancia a Fallos de AlimentaciÃ³n:** No se ha implementado un circuito de detecciÃ³n de bajo voltaje (Brown-out Detection proactivo) ni capacitores de hold-up para garantizar que las compuertas puedan cerrarse (por un resorte o energÃ­a residual) si el gabinete pierde energÃ­a principal.

---

## 3. Uso de AI (AI Log)

Se documenta a continuaciÃ³n de manera transparente el uso de **Claude 3.5 Sonnet** (vÃ­a plataforma Antigravity) como apoyo y asistente a lo largo del desarrollo.

| Fecha | Herramienta | PropÃ³sito | Prompt / InteracciÃ³n | Resultado / CorrecciÃ³n aplicada por el candidato |
| :--- | :--- | :--- | :--- | :--- |
| 2026-06-30 | Claude 3.5 | ValidaciÃ³n del Firmware | *"Revisar la implementaciÃ³n de fsm.py y adc_ntc.py comparÃ¡ndolo con las reglas del sistema de extracciÃ³n. Â¿Existen condiciones de carrera o bloqueos que incumplan los requerimientos?"* | **Resultado AI:** SeÃ±alÃ³ correctamente que el WDT podrÃ­a expirar si el actuador se mantenÃ­a encendido sin alimentar al WDT. Propuso un promedio ADC sÃ­ncrono. <br> **CorrecciÃ³n MÃ­a:** AceptÃ© el diagnÃ³stico del WDT, pero **rechacÃ©** su sugerencia de ADC sÃ­ncrono. ImplementÃ© la alimentaciÃ³n del WDT en chunks dentro de `hbridge.py` y diseÃ±Ã© manualmente un filtro circular asÃ­ncrono para el ADC. |
| 2026-06-30 | Claude 3.5 | DiseÃ±o de SimulaciÃ³n (Wokwi) | *"Generar el mapeo JSON para diagram.json en Wokwi. Necesito emular el puente H usando lÃ³gica de LEDs en antiparalelo conectada a los pines simulados del TB6612FNG."* | **Resultado AI:** GenerÃ³ el boilerplate JSON de conexiones, ahorrando tiempo de cableado manual en la plataforma web. <br> **ValidaciÃ³n:** RevisÃ© los GPIOs contra el requerimiento (GP26, GP27, GP6, GP7, GP0) y asegurÃ© que la polaridad de los LEDs correspondiera a AIN1 y AIN2. |
| 2026-06-30 | Claude 3.5 | EcuaciÃ³n Steinhart-Hart vs Beta | *"Â¿Para un termistor NTC 10K, quÃ© tan diferente es el resultado usando el modelo Steinhart-Hart vs el parÃ¡metro Beta B=3435 en un rango de 0 a 80 grados?"* | **Resultado AI:** DemostrÃ³ matemÃ¡ticamente que el error entre ambos modelos es inferior a $0.5\text{Â°C}$ en ese rango estrecho. <br> **DecisiÃ³n:** OptÃ© por usar el mÃ©todo del coeficiente Beta en el firmware por su menor consumo computacional en el RP2040, garantizando una excelente relaciÃ³n costo/precisiÃ³n. |
| 2026-06-30 | Claude 3.5 | PCB Layout Guidelines | *"Sugerencias de ruteo en KiCad para aislar el ruido de PWM de un MOSFET conmutando 48V de un ADC de 12 bits leyendo un NTC a 3.3V."* | **Resultado AI:** SugiriÃ³ el uso de planos de tierra separados (AGND y DGND), conexiÃ³n en un punto estrella, y evitar que las pistas de potencia pasen por debajo del MCU. <br> **ImplementaciÃ³n:** ApliquÃ© estos principios en el diseÃ±o fÃ­sico del PCB entregado, ensanchando las pistas de 48V y protegiendo el pin `GP26` y `GP27` con anillos de guarda (guard rings). |
| 2026-06-30 | Claude 3.5 | Testing y Mocks | *"Genera un script en Python para correr tests unitarios locales para fsm.py sin necesitar el hardware fÃ­sico, haciendo mock del mÃ³dulo machine."* | **Resultado AI:** CreÃ³ las clases bÃ¡sicas de `mock_machine.py` con `Pin`, `ADC` y `WDT`. <br> **ModificaciÃ³n:** Tuve que modificar la estructura de las pruebas para inyectar correctamente las lecturas simuladas de temperatura y asÃ­ comprobar el estado `LOCKOUT`. |

*(Las interacciones completas, iteraciones y el desarrollo del cÃ³digo estÃ¡n reflejados implÃ­citamente en el diseÃ±o arquitectÃ³nico final del proyecto entregado).*

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
