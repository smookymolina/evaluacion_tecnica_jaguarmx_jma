# PROMPT OPTIMIZADO PARA REVISIÓN DE ESQUEMÁTICO Y MEJORA DE LAYOUT
## Proyecto Jaguar MX — Extractor de Aire Caliente
## Candidato: Ing. Jair Molina Arce | Herramienta: Fable 5
---

## INSTRUCCIONES DE USO

Este prompt está dividido en **2 fases secuenciales** para optimizar tokens en Fable 5:

1. **FASE A (este prompt):** Revisión del esquemático + búsqueda de referencias
2. **FASE B (próximo prompt):** Implementación del layout mejorado

**Ejecutar en Fable 5 con parámetro: `--model=fable-5`**

---

## FASE A: REVISIÓN DE ESQUEMÁTICO + INVESTIGACIÓN DE REFERENCIAS

### PARTE 1: REVISAR ESQUEMÁTICO ACTUAL

Analiza el esquemático en: `C:\Users\GIRTEC\Claude\Projects\Jaguar MX\kicad\jaguar_extractor.kicad_sch`

**Verificación contra requisitos (PDF evaluación):**

1. **Etapa de sensores NTC:**
   - ¿Hay divisor de voltaje 10kΩ + 10kΩ en ambos canales (INT y EXT)?
   - ¿Están las resistencias de pull-up del DIP switch correctas (GP6, GP7, GP0)?
   - ¿Existe filtrado RC (1kΩ + capacitor) en las entradas analógicas?
   - ¿Los diodos de protección (BAT54S) están presentes?

2. **Etapa de potencia TB6612FNG:**
   - ¿Están los pines de entrada AIN1, AIN2, MOTOR_EN conectados a los GPIOs correctos (GP2, GP1, GP3)?
   - ¿Está el pin STBY conectado a HIGH (habilitación)?
   - ¿Hay desacoplamiento (100nF + 47µF) en VM y VCC?
   - ¿Hay protección TVS en las líneas de entrada?

3. **Etapa de ventilador (MOSFET):**
   - ¿Es el MOSFET un NMOS accionable por 3.3V (ej. IRL520N)?
   - ¿Hay resistencia pull-down (10kΩ) en el gate?
   - ¿Hay resistencia serie en el gate (100Ω)?
   - ¿Está el diodo flyback (1N4007) entre drain y +48V?
   - ¿Hay desacoplamiento 100µF + 100nF en el rail +48V?

4. **Fuente de alimentación:**
   - ¿Hay LDO AP2112 o similar para generar +3.3V?
   - ¿Hay fusible PPTC (F1) en la salida del LDO?
   - ¿Hay desacoplamiento en entrada y salida del LDO (≤3mm)?

5. **Conexiones de tierra:**
   - ¿Hay Net-Tie (NT1) entre AGND y PGND?
   - ¿Las tierras están separadas en zonas (analógica vs. potencia)?

**Salida esperada:**
- Lista de CUMPLE/NO CUMPLE para cada ítem
- Si hay deficiencias: enumerar qué falta o está incorrecto
- Recomendaciones puntuales para corregir

---

### PARTE 2: INVESTIGACIÓN DE REFERENCIAS — LAYOUT DE PCB SIMILAR

**Objetivo:** Buscar 3-5 proyectos de referencia de circuitos similares para estudiar su estrategia de layout.

**Criterios de búsqueda:**

Busca proyectos que cumplan TODOS estos requisitos:
- 2 capas (FR4 1.6mm, Cu 1oz) — **NO búsqueda de multicapa**
- Mezcla de potencia (48V) + lógica (3.3V) + analógica (sensores)
- MOSFET o circuito de conmutación con protecciones (flyback, TVS)
- Sensor analógico con filtrado (NTC, termopar, etc.)
- Microcontrolador (RP2040/RP2350 o similar ARM de baja potencia)

**Fuentes a revisar:**
1. Proyectos de GitHub con PCB abierto (OpenPCB, OSHWA) — filtrar por "mixed-signal PCB layout"
2. Documentación de referencia: AN-95 (Analog Devices "PCB Layout for Mixed-Signal Systems")
3. KiCad official library ejemplos
4. Digikey / TI aplicativos notes sobre TB6612 / gate drivers

**Para CADA proyecto encontrado, documentar:**
- Nombre del proyecto y link
- Dimensiones del PCB y número de capas
- Topología de planos de tierra (star ground, planos separados, etc.)
- Estrategia de ruteado analógico (separación física, vías, capas)
- Ruteado de potencia (ancho de pista, via array, disipación térmica)
- Clearance y DRC utilizado (si está documentado)
- Observación sobre qué funcionó bien y qué se podría mejorar

**Salida esperada:**
- Tabla resumen de 3-5 referencias con observaciones clave
- Recomendaciones concretas que se pueden aplicar al proyecto Jaguar

---

## NORMAS DE DISEÑO A APLICAR (resumen de FASE4_Layout_PCB_KiCad_JaguarMX.md)

**Debe cumplir ESTRICTAMENTE:**

| Parámetro | Valor |
|-----------|-------|
| Dimensiones PCB | 80 × 55 mm |
| Capas | F.Cu + B.Cu (2 capas) |
| Stackup | FR4 1.6mm, 1oz Cu |
| Ancho pista Power_48V | 1.5 mm |
| Ancho pista Power_5V | 1.0–1.5 mm |
| Ancho pista Signal | 0.2 mm |
| Clearance Power_48V | 0.6 mm |
| Clearance Signal | 0.15 mm |
| Vías Power | 0.8 mm drill / 1.4 mm pad |
| Vías Signal | 0.3 mm drill / 0.7 mm pad |
| **Hemisferio Lógico** | X: 0–40 mm (AGND) |
| **Hemisferio Potencia** | X: 40–80 mm (PGND) |
| **NT1 (Net-Tie)** | X≈40 mm, Y≈15 mm — único cruce AGND↔PGND |
| **Lazo freewheeling** | D3 a ≤5mm de J5, área <100mm² |
| **Rutas analógicas** | ≤10mm, F.Cu solo, no vías, separación ≥0.5mm de conmutación |

---

## ENTREGA ESPERADA (FASE A)

Proporcionar un informe conciso en formato markdown con:

1. **Sección 1: Verificación de Esquemático**
   - Tabla CUMPLE/NO CUMPLE (5 bloques: sensores, TB6612, MOSFET, PSU, tierra)
   - Si hay deficiencias: acción recomendada

2. **Sección 2: Referencias de Layout**
   - Tabla de 3-5 proyectos encontrados
   - Para cada uno: link, topología de tierra, ruteado analógico, ruteado potencia
   - Recomendaciones extraídas

3. **Sección 3: Plan para FASE B**
   - Checklist de 10 elementos clave a implementar en el layout
   - Prioridad (CRÍTICO / IMPORTANTE / ÓPTIMO)
   - Estimado de tiempo en KiCad para layout completo

---

## NOTAS IMPORTANTES

- **NO diseñar layout aún** — solo investigar y verificar base actual
- **Optimizar para Fable 5:** respuestas concisas, sin redundancia, enfocadas en hechos técnicos
- **Si el esquemático tiene errores críticos:** PAUSAR y reportar antes de continuar a FASE B
- **Usar enlaces de GitHub raw (raw.githubusercontent.com)** para consultar archivos de proyectos públicos sin descargar ZIP
- **Documentar fuentes:** todo claim sobre "mejor práctica" debe tener referencia a AN, datasheet o proyecto OSH

---

## PRÓXIMO PASO (FASE B)

Una vez completada FASE A, usar el siguiente prompt para implementar el layout mejorado:

```
FASE B: IMPLEMENTACIÓN DE LAYOUT EN KICAD SIGUIENDO NORMAS FASE4

[Se proporcionará después de FASE A con referencias específicas de FASE A]
```

---

**Autor:** Claude Code (Fable 5)  
**Fecha:** 2026-07-02  
**Proyecto:** Evaluación Técnica Jaguar de México — Ingeniero de Sistemas Embebidos Jr.
