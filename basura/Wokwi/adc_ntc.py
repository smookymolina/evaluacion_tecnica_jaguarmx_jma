"""
adc_ntc.py - Lectura y conversion de sensores NTC
==================================================
Sistema de extraccion de aire caliente - Jaguar de Mexico
Candidato: Ing. Jair Molina Arce

Sensor: NTC TT05-10KC8-1S-T105-1500 (TEWA Temperature Sensors)
  R0   = 10,000 Ohm @ T0 = 25 C (298.15 K)
  Beta = 3435 K  (datasheet TEWA/TME -- correccion; cronograma usaba 3950K)
  Rango: -40 C a 105 C (T105 en el part number = Tmax 105 C)

Circuito: divisor de voltaje
  Vcc (3.3V) -- R_REF (10kOhm) -- Vout -- NTC -- GND
  Vout -> ADC GPIO26 (TEMP_INT) y GPIO27 (TEMP_EXT)

Filtrado: buffer circular de N_SAMPLES=8 lecturas + trimmed mean
  (descarta max y min para eliminar picos de ruido EMI)

Rango valido:  10.0 C <= T <= 130.0 C
  < 10 C  -> sensor desconectado / circuito abierto
  > 130 C -> cortocircuito o fuera del rango fisico del NTC
"""

import math
from machine import ADC, Pin

# Configuracion del sensor
R_REF      = 10_000    # Resistencia de referencia del divisor (Ohm)
R0         = 10_000    # Resistencia nominal del NTC @ T0 = 25 C
T0_K       = 298.15    # Temperatura de referencia (Kelvin)
BETA       = 3435      # Constante Beta del NTC (K) -- datasheet TEWA
ADC_MAX    = 65535     # Valor maximo ADC MicroPython (12-bit mapeado a 16-bit)

# Filtro
N_SAMPLES  = 8         # Tamano del buffer circular

# Rangos de validacion
TEMP_MIN_C = 10.0      # < 10 C = invalido (sensor desconectado)
TEMP_MAX_C = 130.0     # > 130 C = invalido (cortocircuito)

# Pines ADC
PIN_TEMP_INT = 26      # GPIO26 / ADC0 -> temperatura interna
PIN_TEMP_EXT = 27      # GPIO27 / ADC1 -> temperatura externa


class NTCSensor:
    """
    Lee un sensor NTC via divisor de voltaje + ADC.
    Buffer circular N=8 con trimmed mean (descarta max y min).
    """

    def __init__(self, pin, name="NTC"):
        self._adc  = ADC(Pin(pin))
        self._pin  = pin
        self._name = name
        self._buf  = []

    def reset(self):
        """Limpia el buffer para forzar una precarga de muestras frescas."""
        self._buf = []

    def _adc_to_resistance(self, raw):
        """
        Convierte valor ADC a resistencia NTC (Ohm).
        Circuito: Vcc--R_REF--Vout--NTC--GND
        R_NTC = R_REF * raw / (ADC_MAX - raw)
        Retorna None si el sensor esta desconectado o en cortocircuito.
        """
        if raw <= 0 or raw >= ADC_MAX:
            return None
        return R_REF * raw / (ADC_MAX - raw)

    def _resistance_to_celsius(self, r_ntc):
        """
        Ecuacion Beta: T(K) = 1 / [(1/T0) + (1/Beta)*ln(R/R0)]
        Retorna None si el resultado esta fuera del rango valido.
        """
        try:
            inv_t  = (1.0 / T0_K) + (1.0 / BETA) * math.log(r_ntc / R0)
            temp_c = (1.0 / inv_t) - 273.15
        except (ValueError, ZeroDivisionError):
            return None
        if temp_c < TEMP_MIN_C or temp_c > TEMP_MAX_C:
            return None
        return temp_c

    def read(self):
        """
        Lee el sensor y retorna (ok: bool, temp_c: float).
        Primera llamada: precarga el buffer con N_SAMPLES lecturas.
        Llamadas siguientes: agrega 1 muestra, descarta la mas antigua.
        """
        if not self._buf:
            for _ in range(N_SAMPLES):
                self._buf.append(self._adc.read_u16())
        else:
            self._buf.append(self._adc.read_u16())
            self._buf.pop(0)

        # Trimmed mean: copia para no alterar el buffer
        samples = list(self._buf)
        if len(samples) >= 4:
            samples.remove(max(samples))
            samples.remove(min(samples))
        raw = int(sum(samples) / len(samples))

        r_ntc = self._adc_to_resistance(raw)
        if r_ntc is None:
            return False, 0.0

        temp_c = self._resistance_to_celsius(r_ntc)
        if temp_c is None:
            return False, 0.0

        return True, round(temp_c, 2)

    def __repr__(self):
        return "<NTCSensor name={} pin=GP{}>".format(self._name, self._pin)


# Instancias globales del modulo
sensor_int = NTCSensor(PIN_TEMP_INT, name="TEMP_INT")
sensor_ext = NTCSensor(PIN_TEMP_EXT, name="TEMP_EXT")


def read_temperatures():
    """
    Lee ambos sensores NTC.
    Retorna: (ok_int, temp_int_c, ok_ext, temp_ext_c)
    """
    ok_int, t_int = sensor_int.read()
    ok_ext, t_ext = sensor_ext.read()
    return ok_int, t_int, ok_ext, t_ext


def reset_sensors():
    """Limpia los buffers de ambos sensores para forzar precarga."""
    sensor_int.reset()
    sensor_ext.reset()
