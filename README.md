# Sistema de Extracción de Aire Caliente para Gabinete de Telecomunicaciones
## Jaguar de México — Evaluación Técnica
**Candidato:** Ing. Jair Molina Arce  
**Fecha:** 30 de junio de 2026

---

## Descripción del Proyecto
Este proyecto consiste en el diseño físico y lógico (hardware y firmware) de un sistema de control automático para la extracción de aire caliente en un gabinete de telecomunicaciones. El sistema compara la temperatura interna (`TEMP_INT`) con la temperatura externa (`TEMP_EXT`) y gestiona de forma dinámica:
1. **Compuertas mecánicas:** Operadas por un actuador lineal DFRobot FIT0803 a través de un puente H Toshiba TB6612FNG.
2. **Extractor/Ventilador:** Ventilador industrial Mechatronics MR1238E48B-FSR (48V DC) controlado por modulación low-side con un MOSFET de potencia IRL520N.

El núcleo de control está basado en el microcontrolador **Seeed Studio XIAO RP2350**, programado en MicroPython con una arquitectura de Máquina de Estados Finitos (FSM) y supervisado por un watchdog timer por hardware (WDT).

---

## Estructura del Repositorio

- `firmware/`: Código fuente de control en MicroPython.
  - `main.py`: Punto de entrada, inicialización y gestión de fallos.
  - `fsm.py`: Implementación de la FSM (INIT, READING, COOLING, IDLE, ERROR).
  - `adc_ntc.py`: Adquisición analógica con promedio móvil (trimmed mean, N=8) y conversión Beta.
  - `dip_switch.py`: Configuración de setpoint de histéresis mediante DIP switch.
  - `hbridge.py`: Control de dirección y habilitación del actuador con alimentación segura al WDT.
  - `fan.py`: Módulo de conmutación del MOSFET del ventilador.
- `kicad/`: Archivos del diseño de hardware en KiCad v8/v9.
  - `PCB/PCB.kicad_pro`: Archivo de proyecto de KiCad.
  - `PCB/PCB.kicad_sch`: Esquemático del circuito (Componentes colocados, especificaciones y BOM al 100%).
  - `PCB/PCB.kicad_pcb`: Diseño físico del PCB.
  - `PCB/sym-lib-table`: Tabla de mapeo de librerías de símbolos.
- `datasheets/`: Especificaciones técnicas en markdown y PDFs de los componentes clave.
- `FASE2.1_Netlist_Corregido_JaguarMX.md`: Netlist blindado de interconexiones (verdad de referencia).
- `FASE3_Guia_Esquematico_KiCad_JaguarMX.md`: Guía de diseño del esquemático.
- `FASE4_Layout_PCB_KiCad_JaguarMX.md`: Guía para el trazado de PCB y distribución de componentes.
- `ETISEJr_JairMolina.md`: Respuestas de evaluación y bitácora de uso de IA.
- `EvaluacionTecnica_SistemasEmbebidosJr_JaguarDeMexico.pdf`: Documento de requerimientos oficiales.
- `Cronograma_EvaluacionTecnica_JairMolina.docx`: Planificación de las fases del examen.
- `parse_sch.py`: Script para extraer la BOM directamente del esquemático KiCad.
- `test_firmware.py` / `micropython.py` / `mock_*.py`: Entorno local de pruebas unitarias y mocks de hardware.
- `package_project.ps1`: Script automatizado para el empaquetado del entregable final.

---

## Modificaciones de Hardware Incorporadas (Fase 2.1)
- **[MOD-1] Remapeo de SW2:** Movido de GP7 (back pad inaccesible) a GP8 (castellación lateral del Seeed XIAO RP2350).
- **[MOD-2] Clamping de ADC:** Reemplazo de diodos TVS SMBJ3.3A por diodos Schottky duales BAT54S en configuración de clamp activo post-filtro.
- **[MOD-3] Inmunidad EMI en DIP Switch:** Pull-ups externas de 10kΩ y condensadores de bypass de 100nF en cada canal.
- **[MOD-4] Selector J9:** Reemplazo del puente de soldadura por un header de 3 pines para seleccionar control del Gate directo o con driver TC4420.
- **[MOD-5] Star Ground:** Unión única AGND-PGND mediante Net-Tie de cobre directo (0Ω), eliminando la ferrita.
- **[Desacoplo de U4 (Nuevo)] Capacitor C15:** Adición del capacitor de desacoplo `C15` (100nF, DNP por defecto) para alimentar adecuadamente al driver TC4420 si se decide poblar en Configuración Activa-B.
- **[Conexión GND U4 (Nuevo)] Corrección de Plano:** Enrutamiento de la tierra de U4 (GND, pines 1, 2, 4) al plano de potencia `PGND` (en lugar del plano analógico `AGND`) para evitar la inyección de ruidos transitorios de 6A pico en el plano sensible de lectura.
- **[Consolidación (Nuevo)] Remoción de Excesos:** Eliminación de la resistencia fantasma redundante `R8` del diseño del circuito.

