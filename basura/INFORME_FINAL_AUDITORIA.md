# Informe Final de Auditoría del Proyecto

## 1. Revisión de Objetivos (PDF vs Implementación)

### Objetivo General
* **Requerimiento:** Diseñar el circuito, PCB y firmware de un sistema de extracción de aire caliente para un gabinete de telecomunicaciones comparando `TEMP_INT` vs `TEMP_EXT`.
* **Estado:** ✅ CUMPLIDO. Se desarrollaron las 3 fases (Firmware en MicroPython/C++, Hardware en KiCad y Simulación en Wokwi).

### Objetivos Específicos y Lógica
1. **Lectura Periódica de Temperatura:** ✅ Implementada a 1 Hz con filtro de promedio recortado (Trimmed Mean) de 8 muestras para eliminar ruido electromagnético.
2. **Activación de Enfriamiento (`TEMP_INT` > `TEMP_EXT` y `> Setpoint`):** ✅ Implementado. La FSM abre las compuertas (via TB6612FNG, travel no bloqueante de 3s) y luego enciende el ventilador.
3. **Detención de Enfriamiento (`TEMP_INT` <= `TEMP_EXT`):** ✅ Implementado. Físicamente no se puede enfriar más allá de la temperatura exterior. El sistema pasa a IDLE, apaga el ventilador y cierra compuertas.
4. **Estado Seguro ante Errores:** ✅ Implementado. Si el NTC reporta temperatura fuera de rango (-40 a 105°C) o se desconecta (saturación de ADC) por 3 lecturas consecutivas, se entra a `STATE_ERROR` (apaga motor y ventilador), con reintentos a los 30s. Al fallar 5 veces, entra a `STATE_LOCKOUT` permanente.
5. **DIP Switch (40°C - 75°C):** ✅ Implementado rigurosamente siguiendo la tabla de verdad (SW3, SW2, SW1).
6. **Mapa de GPIOs:** ✅ Cumplido estrictamente según el PDF (ej. VENT en GPIO4, TEMP_INT en GPIO26, etc.).

## 2. Mejoras Añadidas a la Simulación (Wokwi)
Para asegurar una defensa brillante en la sesión en vivo (Fase 2), implementamos características por encima de los requerimientos:
* **FSM 100% No Bloqueante:** Uso de `millis()` en C++ para que el travel del actuador (~3s) no detenga el escaneo térmico de 1 Hz.
* **Parpadeo Dinámico:** El LED del ventilador parpadea velozmente (150ms) al superar los 60°C simulando su máxima capacidad.
* **Comandos Seriales (SET:, TEMP:, EXT:):** Permiten inyectar temperaturas y manipular los límites térmicos en tiempo real sin requerir interacción mecánica con los potenciómetros/DIP durante la presentación.

## 3. Estado de los Entregables Finales
Comparado contra el **Cronograma_EvaluacionTecnica_JairMolina.docx**, el progreso es del 100%:
* 📁 `/firmware/` -> Completo.
* 📁 `/kicad/` -> Esquemático y PCB terminados y sin errores de DRC/ERC.
* 📁 `/Wokwi/` -> Simulación completa y validada con enlace público.
* 📄 `ETISEJr_JairMolina.md` -> Documento de entrega listo con URL, Cuestionario y Logs de IA.

## 4. Limpieza del Repositorio
Se realizó la limpieza del repositorio eliminando scripts temporales, archivos basura de word (`~$...`) y carpetas scratch, dejando un proyecto impecable y profesional listo para la evaluación técnica.
