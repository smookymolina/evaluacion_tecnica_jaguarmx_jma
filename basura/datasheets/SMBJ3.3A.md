# SMBJ3.3A — Diodo TVS Unidireccional 3.3V (Vishay)

**Función en el sistema:** Protección contra ESD y transitorios en las entradas analógicas GP26 y GP27

---

## ⚠️ Nota sobre el part number

> El CLAUDE.md menciona `SMBJ3.3A`. La nomenclatura Vishay para TVS de 3.3V es:
> - **SMBJ3V3A** — 3.3V standoff, unidireccional
>
> Verificar el part number exacto al pedir componentes.
> Las dos denominaciones refieren al mismo componente en diferentes catálogos.

---

## Parámetros eléctricos clave (SMBJ3V3A — Vishay)

| Parámetro | Símbolo | Valor | Nota |
|---|---|---|---|
| Standoff voltage (trabajo) | VRWM | **3.3 V** | Tensión máx sin conducción |
| Breakdown voltage mín | VBR | 3.67 V | @ IT = 10 mA |
| Breakdown voltage máx | VBR | 4.06 V | |
| Clamping voltage | VC | **6.0 V** | @ IPP = 100 A (pico 8/20µs) |
| Peak pulse power | PPP | **600 W** | 1 ms, 8/20 µs waveform |
| Peak pulse current | IPP | 100 A | |
| Corriente de fuga | IR | < 1 µA | @ VRWM = 3.3V |
| Temperatura de operación | TJ | -55°C a +150°C | |
| Encapsulado | SMB (DO-214AA) | — | SMD 2-pin |

---

## ¿Cómo protege las entradas ADC?

```
Divisor NTC → Vout (hasta 3.3V normal) → GPIO26 o GPIO27

Si hay un pico ESD o transitorio > 3.67V:
  → TVS conduce → clampea la tensión a ≤ 6.0V
  → GPIO protegido (Vmax GPIO RP2040 = 3.3V + tolerancia)
```

En condiciones normales (0–3.3V en las entradas analógicas), el TVS no conduce.
Solo se activa con transitorios.

---

## Conexión en PCB

```
Vout divisor NTC ──┬── GPIO (ADC)
                   │
                [SMBJ3V3A]  (Cátodo arriba, Ánodo a GND)
                   │
                  GND
```

- **Un TVS por entrada analógica:** GP26 y GP27 → 2× SMBJ3V3A
- Colocar lo más cerca posible al conector de la sonda NTC
- En la misma zona analógica del PCB, alejada de zonas de potencia

---

## Consideración de diseño

La resistencia del divisor (R_REF = 10 kΩ) limita naturalmente la corriente en caso de
sobretensión moderada. El TVS proporciona protección ante picos rápidos (ESD, rayo en línea).
Juntos forman una protección robusta para entradas analógicas en entorno industrial.

---

## Links de descarga del datasheet

| Documento / Fuente | URL | Estado | Archivo Local | Tamaño | Páginas |
|---|---|---|---|---|---|
| **SMBJ3V3A Vishay** | https://www.vishay.com/docs/88940/smbj3v3.pdf | Success | `SMBJ3V3A_Vishay.pdf` | 112.5 KB | 5 |
| **SMBJ Series Vishay** | https://www.vishay.com/docs/88392/smbj.pdf | Success | `SMBJ_Series_Vishay.pdf` | 126.6 KB | 6 |
| **SMBJ Series Github** | https://github.com/Edragon/Datasheet/raw/master/%E7%9E%AC%E6%80%81%E6%8A%91%E5%88%B6%E4%BA%8C%E6%9E%81%E7%AE%A1SMBJ.pdf | Success | `SMBJ_Series_Github.pdf` | 214.5 KB | 4 |
