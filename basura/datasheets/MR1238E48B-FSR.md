# MR1238E48B-FSR — Ventilador DC 48V (MinebeaMitsumi / NMB)

**Función en el sistema:** Extracción de aire caliente del gabinete de telecomunicaciones

---

## Decodificación del part number

| Segmento | Significado |
|---|---|
| MR | MinebeaMitsumi (NMB-Minebea) |
| 1238 | 120 mm × 120 mm × 38 mm (dimensiones) |
| E | Ball bearing (dual ball bearing) |
| 48B | 48V DC, versión B |
| FSR | Fan Speed Regulation — con señal de control de velocidad (FG/PWM) |

---

## Parámetros técnicos estimados (serie MR1238)

> **Nota:** El datasheet completo del MR1238E48B-FSR específico no está disponible en fuentes públicas abiertas.
> Los valores siguientes se basan en el catálogo de la serie MR1238 de MinebeaMitsumi.
> **Verificar con el datasheet oficial antes de la sesión en vivo.**

| Parámetro | Valor (serie MR1238 @ 48V) | Nota |
|---|---|---|
| Dimensiones | 120 × 120 × 38 mm | |
| Tensión de operación | **48V DC** | **No conectar al RP2040 directo** |
| Rango de tensión | 38.4V – 57.6V | ±20% sobre nominal |
| Corriente nominal | ~0.27–0.35 A | @ 48V, plena velocidad |
| Potencia de entrada | ~13–17 W | |
| Velocidad nominal | ~3000–3500 RPM | Varía por variante |
| Flujo de aire | ~130–180 CFM | |
| Presión estática | ~5–9 mm H₂O | |
| Nivel de ruido | ~48–55 dBA | |
| Bearing | Dual ball bearing | Alta vida útil (>70,000 h) |
| MTBF | >70,000 horas | @ 40°C |
| Temperatura de operación | -10°C a +70°C | |
| Señal FSR | FG (tachometro) o PWM | Para supervisión de velocidad |

---

## Integración en el sistema

```
48V DC ──(+)──[ventilador MR1238E48B-FSR]──(−)──[ Drain IRL520N ]──[ Source ]── GND

[1N4007 flyback: ánodo en Drain, cátodo en 48V]

GPIO4 → (gate IRL520N) → switch ON/OFF del ventilador
```

**El GPIO4 nunca se conecta al ventilador directamente.** La diferencia de tensión (3.3V vs 48V) requiere la etapa MOSFET.

---

## Precauciones

1. **Aislamiento 48V:** El rail de 48V debe estar completamente aislado de los circuitos de 3.3V del MCU.
2. **Diodo flyback obligatorio:** Al apagar el ventilador, la inductancia del motor genera un pico de decenas de voltios. El 1N4007 lo absorbe.
3. **Capacitor de decoupling:** 100µF / 63V electrolítico en el rail 48V cerca del drenador del MOSFET.
4. **Señal FSR:** La línea FG (tachometro) puede conectarse a un GPIO del RP2350 para supervisión de velocidad (no implementado en esta versión).

---

## Links de descarga del datasheet

| Documento / Fuente | URL | Estado | Archivo Local | Tamaño | Páginas |
|---|---|---|---|---|---|
| **MR1238 Series** | https://www.mechatronics.com/pdf/MR1238.pdf | Success | `MR1238_Series.pdf` | 304.9 KB | 1 |
| **NMB Fan Catalog 2024** | https://cdn.nmbtc.com/uploads/2025/04/202407-fan-motor-catalog-pdf.pdf | Success | `NMB_Fan_Catalog_2024.pdf` | 9366.6 KB | 160 |
| **MR1238 Mechatronics MD1238** | https://www.mechatronics.com/pdf/MD1238.pdf | Success | `MR1238_Mechatronics_MD1238.pdf` | 306.3 KB | 1 |
