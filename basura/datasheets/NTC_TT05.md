# NTC TT05-10KC8-1S-T105-1500 — Termistor NTC (TEWA Temperature Sensors)

**Función en el sistema:** Medir TEMP_INT (GPIO26/ADC0) y TEMP_EXT (GPIO27/ADC1)

---

## ⚠️ CORRECCIÓN CRÍTICA: Valor Beta

> **El cronograma/evaluación indicaba Beta = 3950 K — INCORRECTO.**
> El datasheet oficial de TEWA/TME para este part number específico indica:
>
> **Material constant B = 3435 K**
>
> Usar 3950 K en lugar de 3435 K introduce un error de **~3.5°C a 50°C** y **~6°C a 70°C**.
> El firmware ha sido corregido a `BETA = 3435` en `adc_ntc.py`.

---

## Parámetros eléctricos / térmicos clave

| Parámetro | Valor | Nota |
|---|---|---|
| Resistencia nominal R₀ | 10,000 Ω (10 kΩ) | @ T₀ = 25°C |
| Temperatura nominal T₀ | 25°C (298.15 K) | |
| **Material constant B** | **3435 K** | Fuente: TME / datasheet TEWA |
| Tolerancia de resistencia | ±1% (clase B) | Sobre R₀ @ 25°C |
| Rango de temperatura | **-40°C a +105°C** | T105 en el part number = Tmax 105°C |
| Tensión de operación máx | — | Sensor pasivo (resistencia) |
| Encapsulado | Cabeza de perno, leads 1500mm | TT05 = M5 thread, IP68 |
| Protección IP | IP68 | Inmersión continua |
| Cable | 1500 mm de longitud | |

---

## Circuito divisor de voltaje

```
Vcc (3.3V)
    │
   R_REF = 10 kΩ   (misma magnitud que R₀ → máxima sensibilidad en rango de operación)
    │
    ├──── Vout ──→ ADC GPIO26 o GPIO27
    │
   R_NTC (TT05)
    │
   GND
```

**Ecuación de conversión:**
```
R_NTC = R_REF × ADC_raw / (ADC_max - ADC_raw)

T(K) = 1 / [(1/T₀) + (1/B) × ln(R_NTC / R₀)]
T(°C) = T(K) - 273.15
```

---

## Tabla de resistencia vs temperatura (referencia)

| Temperatura (°C) | R_NTC aprox (B=3435) |
|---|---|
| -40 | ~197 kΩ |
| 0   | ~31.2 kΩ |
| 25  | 10.00 kΩ (nominal) |
| 50  | ~3.88 kΩ |
| 70  | ~1.96 kΩ |
| 85  | ~1.22 kΩ |
| 105 | ~0.66 kΩ |

---

## Protección en PCB

- TVS SMBJ3.3A en las líneas ADC (GP26, GP27) para proteger contra ESD
- No conectar más de 3.3V a las entradas ADC del RP2040/RP2350

---

## Links de descarga del datasheet

| Documento / Fuente | URL | Estado | Archivo Local | Tamaño | Páginas |
|---|---|---|---|---|---|
| **TEWA** | https://www.tme.com/Document/878564d75c52f90722a06147eac94b00/TT05-10KC8-1S-T105-1500.pdf | Success | `NTC_TT05_TEWA.pdf` | 75.5 KB | 1 |
| **Vishay** | http://www.vishay.com/docs/29049/ntcle100.pdf | Success | `NTC_TT05_Vishay.pdf` | 237.6 KB | 17 |
| **Adafruit** | https://cdn-shop.adafruit.com/datasheets/103_3950_lookuptable.pdf | Success | `NTC_TT05_Adafruit.pdf` | 246.5 KB | 1 |
