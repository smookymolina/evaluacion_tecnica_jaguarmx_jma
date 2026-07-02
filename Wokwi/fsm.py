"""
fsm.py - Maquina de estados finita (FSM) del sistema de extraccion
===================================================================
Sistema de extraccion de aire caliente - Jaguar de Mexico
Candidato: Ing. Jair Molina Arce

Estados y transiciones:
  INIT    -> READING  (siempre, tras aplicar safe state)
  READING -> COOLING  (TEMP_INT > TH_HI  Y  TEMP_INT > TEMP_EXT)
  READING -> IDLE     (condicion inversa o zona de histeresis)
  READING -> ERROR    (N errores ADC consecutivos)
  COOLING -> IDLE     (TEMP_INT <= TH_LO  O  TEMP_INT <= TEMP_EXT)
  COOLING -> ERROR    (N errores ADC consecutivos)
  IDLE    -> COOLING  (TEMP_INT > TH_HI  Y  TEMP_INT > TEMP_EXT)
  IDLE    -> ERROR    (N errores ADC consecutivos)
  ERROR   -> READING  (tras RECOVERY_MS ms de safe state, max MAX_RECOVERIES)
  ERROR   -> LOCKOUT  (si se excede MAX_RECOVERIES)
  LOCKOUT -> (requiere reset de hardware o cambio de DIP)

Filtrado de temperatura:
  El promedio movil N=8 con trimmed-mean se realiza en adc_ntc.py
  (NTCSensor._buf). La FSM recibe temperaturas ya filtradas y las
  almacena directamente en SystemState. Sin segundo buffer.

Watchdog:
  Timeout = 8000 ms. Se alimenta al inicio de cada step() y cada
  500 ms durante el travel del actuador via callback en hbridge.
"""

import time
from machine import WDT
from micropython import const

from adc_ntc import read_temperatures, reset_sensors
from dip_switch import dip
from hbridge import hbridge
from fan import fan

# Constantes de la FSM
_WDT_TIMEOUT_MS     = const(8000)   # Watchdog 8 s
_MAX_ERRORES_CONSEC = const(3)      # Errores consecutivos antes de ERROR
_RECOVERY_MS        = const(30000)  # Tiempo de safe state antes de recovery (30 s)
_MAX_RECOVERIES     = const(5)      # Max recoveries antes de LOCKOUT
_MAX_TEMP_DELTA     = const(80)     # Diferencia INT/EXT fisicamente imposible

# Identificadores de estado (enteros para eficiencia en MicroPython)
_STATE_INIT    = const(0)
_STATE_READING = const(1)
_STATE_COOLING = const(2)
_STATE_IDLE    = const(3)
_STATE_ERROR   = const(4)
_STATE_LOCKOUT = const(5)

# Nombres de estado para logging
_STATE_NAMES = ("INIT", "READING", "COOLING", "IDLE", "ERROR", "LOCKOUT")


class SystemState:
    """
    Estructura de datos equivalente a un struct C.
    Agrupa todas las variables de estado del sistema.
    __slots__ optimiza el consumo de memoria en MicroPython.
    """
    __slots__ = (
        'estado',              # Estado actual de la FSM (int)
        'temp_int',            # Ultima temperatura interna validada (float, grados C)
        'temp_ext',            # Ultima temperatura externa validada (float, grados C)
        'errores_consec',      # Contador de lecturas invalidas consecutivas (int)
        'ticks_error',         # ticks_ms al entrar a ERROR o LOCKOUT
        'recoveries_count',    # Numero de intentos de recovery realizados
        'ciclos_count',        # Contador de transiciones de estado (telemetria)
        'ticks_cooling_start', # ticks_ms al encender el sistema de extraccion
    )

    def __init__(self):
        self.estado              = _STATE_INIT
        self.temp_int            = 0.0
        self.temp_ext            = 0.0
        self.errores_consec      = 0
        self.ticks_error         = 0
        self.recoveries_count    = 0
        self.ciclos_count        = 0
        self.ticks_cooling_start = 0


class ThermalFSM:
    """
    Maquina de estados finita para el control termico del gabinete.
    Interfaz publica: step() y run_forever().
    """

    def __init__(self, enable_watchdog=True, verbose=True):
        self._state    = SystemState()
        self._verbose  = verbose
        self._usar_wdt = False
        self._wdt      = None

        # Watchdog timer
        if enable_watchdog:
            self._wdt      = WDT(timeout=_WDT_TIMEOUT_MS)
            self._usar_wdt = True
            hbridge.set_wdt_feed(self._alimentar_wdt)

        self._log("FSM inicializada - WDT={}".format(
            "habilitado ({} ms)".format(_WDT_TIMEOUT_MS) if enable_watchdog
            else "deshabilitado"
        ))

    # -- Interfaz publica -------------------------------------------------

    def step(self):
        """Ejecuta un ciclo de la FSM. Llamar a 1 Hz desde el loop principal."""
        self._alimentar_wdt()

        try:
            e = self._state.estado
            if   e == _STATE_INIT:    self._paso_init()
            elif e == _STATE_READING: self._paso_reading()
            elif e == _STATE_COOLING: self._paso_cooling()
            elif e == _STATE_IDLE:    self._paso_idle()
            elif e == _STATE_ERROR:   self._paso_error()
            elif e == _STATE_LOCKOUT: self._paso_lockout()
            else:
                self._log("Estado desconocido {} - reset a INIT".format(e))
                self._transicion(_STATE_INIT)

        except MemoryError:
            try:
                print("[{}] FSM[{}] MemoryError - transicion a ERROR".format(
                    time.ticks_ms(), self._estado_str()))
            except Exception:
                pass
            self._transicion(_STATE_ERROR)

        except Exception as exc:
            self._log("Excepcion [{}]: {} - transicion a ERROR".format(
                type(exc).__name__, exc))
            self._transicion(_STATE_ERROR)

    def run_forever(self):
        """
        Loop bloqueante a 1 Hz con compensacion de tiempo sin deriva (drift).
        Cada ciclo toma exactamente 1000 ms medidos desde el inicio del ciclo anterior.
        """
        self._log("Loop principal iniciado (1 Hz, compensacion de tiempo libre de deriva)")
        t_base = time.ticks_ms()

        while True:
            self.step()

            t_sig  = time.ticks_add(t_base, 1000)
            espera = time.ticks_diff(t_sig, time.ticks_ms())

            if espera > 0:
                time.sleep_ms(espera)
                t_base = t_sig
            else:
                # Ciclo extendido (ej: travel actuador ~3 s): no dormimos
                dur = time.ticks_diff(time.ticks_ms(), t_base)
                self._log("Ciclo extendido ({} ms) - reajustando base de tiempo".format(dur))
                t_base = time.ticks_ms()

    @property
    def estado(self):
        """Nombre del estado actual (str, solo lectura)."""
        return self._estado_str()

    # -- Pasos de cada estado ---------------------------------------------

    def _paso_init(self):
        """INIT: aplica safe state y transiciona a READING."""
        hbridge.stop()
        fan.off()
        self._state.errores_consec   = 0
        self._state.recoveries_count = 0
        self._log("Safe state inicial aplicado - {}".format(dip.status_str()))
        self._transicion(_STATE_READING)

    def _paso_reading(self):
        """READING: primera evaluacion post-arranque o post-recovery."""
        self._aplicar_resultado(self._evaluar())

    def _paso_cooling(self):
        """COOLING: re-evalua condiciones en cada ciclo de 1 Hz."""
        self._aplicar_resultado(self._evaluar())

    def _paso_idle(self):
        """IDLE: re-evalua condiciones en cada ciclo de 1 Hz."""
        self._aplicar_resultado(self._evaluar())

    def _paso_error(self):
        """ERROR: safe state activo. Tras RECOVERY_MS intenta recovery."""
        transcurrido = time.ticks_diff(time.ticks_ms(), self._state.ticks_error)
        restante_s   = max(0, (_RECOVERY_MS - transcurrido) // 1000)

        # Log periodico (cada ~5 s) para no saturar la consola
        if (transcurrido // 1000) % 5 == 0:
            self._log("Safe state activo - recovery #{} en {} s".format(
                self._state.recoveries_count + 1, restante_s))

        if transcurrido >= _RECOVERY_MS:
            self._state.recoveries_count += 1
            if self._state.recoveries_count > _MAX_RECOVERIES:
                self._log("Limite de recoveries ({}) alcanzado - LOCKOUT".format(
                    _MAX_RECOVERIES))
                self._transicion(_STATE_LOCKOUT)
            else:
                self._log("Recovery #{} - reintentando lectura".format(
                    self._state.recoveries_count))
                self._state.errores_consec = 0
                self._transicion(_STATE_READING)

    def _paso_lockout(self):
        """LOCKOUT: fallo permanente. Requiere reset de hardware o cambio de DIP."""
        if hasattr(self, '_lockout_setpoint') and dip.read_setpoint() != self._lockout_setpoint:
            self._log("Cambio de DIP detectado en LOCKOUT - reiniciando FSM")
            self._transicion(_STATE_INIT)
            return

        transcurrido = time.ticks_diff(time.ticks_ms(), self._state.ticks_error)
        if (transcurrido // 1000) % 10 == 0:
            self._log("LOCKOUT ACTIVO - Requiere intervencion de mantenimiento")
        fan.off()
        hbridge.stop()

    # -- Evaluacion de temperatura con histeresis -------------------------

    def _evaluar(self):
        """
        Lee sensores NTC (ya promediados en adc_ntc.py) y determina el
        estado destino aplicando histeresis. Detecta:
          - Sensor desconectado / fuera de rango (ok=False de adc_ntc.py)
          - Timeout de ADC (lectura que tarda > 100 ms)
          - Delta termica fisicamente imposible (|INT-EXT| > 80 C)

        Retorna: int (estado destino) o None (mantener estado actual)
        """
        t0 = time.ticks_ms()
        ok_int, t_int, ok_ext, t_ext = read_temperatures()
        dt = time.ticks_diff(time.ticks_ms(), t0)

        # Timeout de ADC
        adc_timeout = dt > 100
        if adc_timeout:
            self._log("WARN: timeout ADC ({} ms)".format(dt))

        # Delta termica invalida
        delta_invalida = False
        if ok_int and ok_ext:
            if abs(t_int - t_ext) > _MAX_TEMP_DELTA:
                delta_invalida = True
                self._log("WARN: delta INT/EXT {:.1f} C > {} C (imposible)".format(
                    abs(t_int - t_ext), _MAX_TEMP_DELTA))

        # Comprobacion de errores
        if not ok_int or not ok_ext or delta_invalida or adc_timeout:
            self._state.errores_consec += 1
            self._log("Lectura invalida #{}/{} - INT:{} {:.1f}C  EXT:{} {:.1f}C".format(
                self._state.errores_consec, _MAX_ERRORES_CONSEC,
                "OK" if ok_int else "FALLA", t_int,
                "OK" if ok_ext else "FALLA", t_ext,
            ))
            if self._state.errores_consec >= _MAX_ERRORES_CONSEC:
                return _STATE_ERROR
            return None   # Mantener estado actual mientras no supere el limite

        # Lectura valida: actualizar SystemState
        self._state.errores_consec   = 0
        self._state.temp_int         = t_int
        self._state.temp_ext         = t_ext
        self._state.recoveries_count = 0

        th_hi = dip.threshold_high()
        th_lo = dip.threshold_low()

        self._log("INT={:.1f}C  EXT={:.1f}C  TH_LO={:.0f}  TH_HI={:.0f}  {}".format(
            t_int, t_ext, th_lo, th_hi, dip.status_str()))

        # Logica de histeresis
        if self._state.estado == _STATE_COOLING:
            # Desactivacion: basta que UNA condicion se cumpla (conservador)
            if t_int <= th_lo or t_int <= t_ext:
                return _STATE_IDLE
            return _STATE_COOLING
        else:
            # Activacion (IDLE o READING): AMBAS condiciones deben cumplirse
            if t_int > th_hi and t_int > t_ext:
                return _STATE_COOLING
            return _STATE_IDLE

    def _aplicar_resultado(self, resultado):
        """Despacha el resultado de _evaluar() a la transicion de estado."""
        if resultado is not None:
            self._transicion(resultado)

    # -- Transiciones de estado -------------------------------------------

    def _transicion(self, nuevo_estado):
        """Ejecuta una transicion de estado de forma segura."""
        if nuevo_estado == self._state.estado:
            return

        de_estado = self._state.estado
        self._log("TRANSICION: {} -> {}".format(
            self._estado_str(), _STATE_NAMES[nuevo_estado]))

        self._state.estado = nuevo_estado

        try:
            self._accion_entrada(nuevo_estado, de_estado)
            self._state.ciclos_count += 1
        except Exception as exc:
            self._log("Error en accion de entrada: {} - forzando ERROR".format(exc))
            if nuevo_estado in (_STATE_ERROR, _STATE_LOCKOUT):
                raise exc
            self._state.estado = de_estado
            self._transicion(_STATE_ERROR)

    def _accion_entrada(self, estado, de_estado):
        """Ejecuta las acciones de hardware al entrar a un nuevo estado."""
        if estado == _STATE_COOLING:
            self._state.ticks_cooling_start = time.ticks_ms()
            self._log("Abriendo compuertas (FIT0803 via TB6612FNG, ~3 s)...")
            hbridge.open_dampers()    # Bloqueante ~3 s; WDT alimentado cada 500 ms
            self._log("Ventilador ON (MR1238E48B-FSR via MOSFET NMOS)")
            fan.on()

        elif estado == _STATE_IDLE:
            if de_estado == _STATE_COOLING and self._state.ticks_cooling_start > 0:
                dur = time.ticks_diff(time.ticks_ms(),
                                      self._state.ticks_cooling_start) / 1000.0
                self._log("ENFRIAMIENTO OK - duracion ciclo: {:.1f} s".format(dur))
                self._state.ticks_cooling_start = 0
            self._log("Ventilador OFF")
            fan.off()
            self._log("Cerrando compuertas (FIT0803 via TB6612FNG, ~3 s)...")
            hbridge.close_dampers()   # Bloqueante ~3 s; WDT alimentado cada 500 ms

        elif estado == _STATE_ERROR:
            self._log("SAFE STATE: ventilador OFF + MOTOR_EN=0")
            fan.off()
            hbridge.stop()
            self._state.errores_consec = 0   # Limpiar para el proximo ciclo de recovery
            self._state.ticks_error = time.ticks_ms()

        elif estado == _STATE_LOCKOUT:
            self._log("LOCKOUT: ventilador OFF + MOTOR_EN=0 (permanente)")
            fan.off()
            hbridge.stop()
            self._state.ticks_error = time.ticks_ms()
            self._lockout_setpoint = dip.read_setpoint()

        elif estado == _STATE_READING:
            self._state.errores_consec = 0
            reset_sensors()
            self._log("Evaluando sensores NTC...")

    # -- Watchdog y logging -----------------------------------------------

    def _alimentar_wdt(self):
        if self._usar_wdt and self._wdt:
            self._wdt.feed()

    def _estado_str(self):
        e = self._state.estado
        if 0 <= e < len(_STATE_NAMES):
            return _STATE_NAMES[e]
        return "UNKNOWN"

    def _log(self, msg):
        if self._verbose:
            print("[{:010d}] FSM[{}] {}".format(
                time.ticks_ms(), self._estado_str(), msg))
