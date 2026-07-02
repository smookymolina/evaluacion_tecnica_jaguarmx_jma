# Datasheets — Sistema de Extracción de Aire Caliente
**Jaguar de México — Evaluación Técnica — Ing. Jair Molina Arce**

> Los archivos de esta carpeta son referencias técnicas para cada componente del sistema.
> Se incluyen dos fuentes por componente donde fue posible.
> **Los PDFs deben descargarse manualmente desde los links oficiales listados en cada archivo.**

---

## Índice de componentes

| Componente | Archivo | Función en el sistema |
|---|---|---|
| TB6612FNG | [TB6612FNG.md](TB6612FNG.md) | Puente H — control actuador FIT0803 |
| NTC TT05-10KC8-1S-T105-1500 | [NTC_TT05.md](NTC_TT05.md) | Sensor de temperatura ×2 |
| FIT0803 | [FIT0803.md](FIT0803.md) | Actuador lineal — compuertas |
| MR1238E48B-FSR | [MR1238E48B-FSR.md](MR1238E48B-FSR.md) | Ventilador 48V |
| IRL520N | [IRL520N.md](IRL520N.md) | MOSFET NMOS — etapa potencia ventilador |
| Seeed XIAO RP2350 | [XIAO_RP2350.md](XIAO_RP2350.md) | MCU (sesión en vivo) |
| RP2040 / Raspberry Pi Pico | [RP2040_Pico.md](RP2040_Pico.md) | MCU (simulación Wokwi) |
| AP2112K-3.3 | [AP2112K.md](AP2112K.md) | LDO 3.3V — regulador de tensión |
| 1N4007 | [1N4007.md](1N4007.md) | Diodo flyback — protección ventilador |
| SMBJ3.3A | [SMBJ3.3A.md](SMBJ3.3A.md) | TVS — protección entradas analógicas |

---

## Links de descarga directa (PDFs oficiales)

| Componente | Fuente 1 (oficial) | Fuente 2 (alternativa) |
|---|---|---|
| TB6612FNG | [Toshiba official](https://toshiba.semicon-storage.com/info/TB6612FNG_datasheet_en_20141001.pdf) | [SparkFun mirror](https://cdn.sparkfun.com/datasheets/Robotics/TB6612FNG.pdf) |
| NTC TT05 | [TME/TEWA official](https://www.tme.com/Document/878564d75c52f90722a06147eac94b00/TT05-10KC8-1S-T105-1500.pdf) | [DigiKey product page](https://www.digikey.com/en/products/detail/tewa-sensors-llc/TT05-10KC8-1S-T105-1500/10264792) |
| FIT0803 | [DFRobot (FIT080x series)](https://www.logosfoundation.org/instrum_gwr/sper/datasheets/DFRobot-FIT080x.pdf) | [DFRobot product page](https://www.dfrobot.com/product-2367.html) |
| MR1238E48B-FSR | [MinebeaMitsumi MR1238 series](https://www.mechatronics.com/pdf/MR1238.pdf) | [MinebeaMitsumi catalog](https://cdn.nmbtc.com/uploads/2025/04/202407-fan-motor-catalog-pdf.pdf) |
| IRL520N | [Infineon oficial](https://www.infineon.com/dgdl/Infineon-IRL520N-DataSheet-v01_01-EN.pdf?fileId=5546d462533600a40153565f9b62255b) | [Infineon assets](https://www.infineon.com/assets/row/public/documents/24/49/infineon-irl520n-datasheet-en.pdf) |
| XIAO RP2350 | [Seeed Studio Wiki](https://wiki.seeedstudio.com/getting-started-xiao-rp2350/) | [GitHub OSHW](https://github.com/Seeed-Studio/OSHW-XIAO-Series) |
| RP2040 | [RPi official](https://datasheets.raspberrypi.com/rp2040/rp2040-datasheet.pdf) | [Pico datasheet](https://datasheets.raspberrypi.com/pico/pico-datasheet.pdf) |
| AP2112K-3.3 | [Diodes Inc. official](https://www.diodes.com/assets/Datasheets/AP2112.pdf) | [Adafruit CDN](https://cdn-shop.adafruit.com/product-files/2471/AP2112.pdf) |
| 1N4007 | [Diodes Inc.](https://www.diodes.com/assets/Datasheets/ds28002.pdf) | [Mouser/Vishay](https://www.mouser.com/datasheet/2/149/1N4007-888322.pdf) |
| SMBJ3.3A | [Vishay SMBJ3V3](https://www.vishay.com/docs/88940/smbj3v3.pdf) | [Vishay SMBJ series](https://www.vishay.com/docs/88392/smbj.pdf) |
