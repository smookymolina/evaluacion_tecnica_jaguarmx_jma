// =====================================================================
// sketch.ino — Simulación Wokwi (Arduino, Raspberry Pi Pico RP2040)
// Sistema de extracción de aire caliente — Jaguar de México
// Candidato: Ing. Jair Molina Arce
//
// Este sketch replica en C++/Arduino la lógica del firmware MicroPython
// de referencia (main.py / fsm.py / adc_ntc.py / dip_switch.py /
// hbridge.py / fan.py):
//
//   FSM: INIT → READING → COOLING / IDLE / ERROR (+ LOCKOUT)
//   - COOLING si TEMP_INT > (SETPOINT + 1°C)  Y  TEMP_INT > TEMP_EXT
//   - IDLE    si TEMP_INT <= (SETPOINT - 1°C) O  TEMP_INT <= TEMP_EXT
//   - ERROR   tras 3 lecturas inválidas consecutivas → safe state
//             (ventilador OFF, motor detenido) → recovery a los 30 s
//
//   Integración del setpoint (coherente con fsm.py):
//   El DIP switch de 3 bits selecciona el setpoint (40..75°C). El
//   setpoint actúa como condición ADICIONAL de habilitación del
//   enfriamiento: no basta con TEMP_INT > TEMP_EXT, además TEMP_INT
//   debe superar el umbral alto (setpoint + histéresis). La histéresis
//   de ±1°C evita chattering del actuador FIT0803 alrededor del umbral.
//
//   Filtrado ADC: buffer circular de 8 muestras, promedio descartando
//   máximo y mínimo (trimmed mean), igual que adc_ntc.py.
//
//   Actuador FIT0803 (compuertas) via TB6612FNG canal A:
//     Abrir : AIN1=LOW,  AIN2=HIGH, MOTOR_EN(PWMA)=HIGH  → AO2=HIGH (LED "abre")
//     Cerrar: AIN1=HIGH, AIN2=LOW,  MOTOR_EN(PWMA)=HIGH  → AO1=HIGH (LED "cierra")
//     Fin de travel (~3 s): AIN1=AIN2=LOW, MOTOR_EN=LOW (motor detenido,
//     estado seguro — igual que hbridge.py). El travel se temporiza de
//     forma NO bloqueante con millis(), por lo que el loop sigue
//     ejecutándose a 1 Hz durante los 3 s de recorrido.
//
//   Ventilador MR1238E48B-FSR (48V) via MOSFET NMOS en GP4:
//     Se enciende al completar la apertura de compuertas (misma
//     secuencia que fsm.py: abrir → fan ON) y se apaga al entrar a IDLE.
// =====================================================================

#include <math.h>

#ifdef ARDUINO_ARCH_RP2040
#include "hardware/watchdog.h"   // WDT hardware del RP2040 (pico-sdk)
#else
// Mocks para poder compilar fuera del RP2040 (el WDT solo existe en el target)
void watchdog_enable(uint32_t delay_ms, bool pause_on_debug) {}
void watchdog_update() {}
#endif

// ---------------------------------------------------------------------
// Mapa de GPIOs (documento oficial Jaguar — NO cambiar sin justificación)
// ---------------------------------------------------------------------
constexpr int PIN_TEMP_INT = 26;  // ADC0 — NTC temperatura interna
constexpr int PIN_TEMP_EXT = 27;  // ADC1 — NTC temperatura externa
constexpr int PIN_SW1      = 6;   // DIP bit 0 (LSB), pull-up interno
constexpr int PIN_SW2      = 7;   // DIP bit 1,       pull-up interno
constexpr int PIN_SW3      = 0;   // DIP bit 2 (MSB), pull-up interno
constexpr int PIN_AIN1     = 2;   // TB6612FNG AIN1 (dirección 1)
constexpr int PIN_AIN2     = 1;   // TB6612FNG AIN2 (dirección 2)
constexpr int PIN_MOTOR_EN = 3;   // TB6612FNG PWMA (habilitación canal A)
constexpr int PIN_VENT     = 4;   // MOSFET NMOS — ventilador 48V

// ---------------------------------------------------------------------
// Conversión NTC (ecuación Beta) — divisor: Vcc--R_REF--Vout--NTC--GND
//   R_NTC = R_REF * raw / (ADC_MAX - raw)
//   T(K)  = 1 / [ (1/T0) + (1/BETA) * ln(R_NTC/R0) ]
//
// NOTA SOBRE EL MODELO DE WOKWI (verificado en
// docs.wokwi.com/parts/wokwi-ntc-temperature-sensor):
//   La parte "wokwi-ntc-temperature-sensor" NO entrega un voltaje lineal:
//   modela internamente un NTC de 10k en serie con una resistencia de 10k
//   y calcula OUT con la ecuación Beta (atributo "beta", default 3950).
//   Por eso aquí usamos la MISMA conversión Beta del firmware real, pero
//   con BETA = 3950 para que la temperatura calculada coincida con el
//   slider de la simulación.
//   En el HARDWARE REAL (NTC TEWA TT05-10KC8-1S-T105-1500) el datasheet
//   indica Beta = 3435 K → cambiar BETA a BETA_HW (la diferencia entre
//   ambas Betas produce un error de ~4°C a 50°C si no se corrige).
// ---------------------------------------------------------------------
constexpr float BETA_WOKWI = 3950.0;  // Beta del NTC genérico de Wokwi
constexpr float BETA_HW    = 3435.0;  // Beta del TEWA TT05 (hardware real)
constexpr float BETA       = BETA_WOKWI;  // ← usar BETA_HW en el hardware
constexpr float T0_K       = 298.15;      // 25°C en Kelvin
constexpr float R0         = 10000.0;     // Resistencia NTC @ 25°C (Ohm)
constexpr float R_REF      = 10000.0;     // Resistencia de referencia (Ohm)
constexpr float ADC_MAX    = 4095.0;      // 12 bits (analogReadResolution)

// Rango físico válido del NTC TT05 (T105 = Tmax 105°C según part number).
// Fuera de este rango (o ADC saturado en 0/4095) la lectura se considera
// inválida: NTC desconectado o en cortocircuito.
// (El firmware MicroPython usa 10..130°C como plausibilidad de gabinete;
// aquí usamos el rango físico del sensor para que todo el recorrido del
// slider de Wokwi (-24..80°C) sea válido y el estado ERROR se demuestre
// desconectando el cable OUT del NTC.)
constexpr float TEMP_MIN_C   = -40.0;
constexpr float TEMP_MAX_C   = 105.0;
constexpr float TEMP_INVALID = -999.0;  // Marcador de lectura inválida

// ---------------------------------------------------------------------
// Filtro: buffer circular de 8 muestras + trimmed mean (descarta max/min)
// ---------------------------------------------------------------------
constexpr int N_SAMPLES = 8;
int buf_int[N_SAMPLES] = {0};
int buf_ext[N_SAMPLES] = {0};
int buf_int_count = 0, buf_int_index = 0;
int buf_ext_count = 0, buf_ext_index = 0;

// ---------------------------------------------------------------------
// FSM — estados y parámetros (coherente con fsm.py)
// ---------------------------------------------------------------------
enum State {
  STATE_INIT,
  STATE_READING,
  STATE_COOLING,
  STATE_IDLE,
  STATE_ERROR,
  STATE_LOCKOUT
};

const char* STATE_NAMES[] = {
  "INIT", "READING", "COOLING", "IDLE", "ERROR", "LOCKOUT"
};

State currentState = STATE_INIT;
float temp_int = 0.0;                 // Última temperatura interna (°C)
float temp_ext = 0.0;                 // Última temperatura externa (°C)
float simulated_heat_offset = 0.0;    // Offset térmico simulado
bool startup_heat_initialized = false;// Bandera para inicio en 30°C
int error_counter = 0;                // Lecturas inválidas consecutivas
unsigned long ticks_error = 0;        // millis() al entrar a ERROR/LOCKOUT
int recoveries_count = 0;             // Intentos de recovery realizados
unsigned long ticks_cooling_start = 0;// millis() al iniciar enfriamiento
int lockout_setpoint = -1;            // Setpoint capturado al entrar a LOCKOUT

// Variables para la inyección de temperatura por cambio de DIP
int last_dip_setpoint = -1;
int dip_change_stage = 0; 
int dip_delay_counter = 0;

constexpr int MAX_ERRORES_CONSEC = 3;         // Errores antes de ERROR
constexpr unsigned long RECOVERY_MS = 30000;  // Safe state 30 s antes de recovery
constexpr int MAX_RECOVERIES = 5;             // Máx recoveries antes de LOCKOUT
constexpr float MAX_TEMP_DELTA = 80.0;        // Delta INT/EXT físicamente imposible
constexpr float HYSTERESIS_C = 1.0;           // Histéresis ±1°C (anti-chattering)

// ---------------------------------------------------------------------
// Actuador FIT0803 — travel NO bloqueante temporizado con millis()
// FIT0803 @ 5V: ~5.8 mm/s → travel ~1.72 s; 3000 ms da margen ×1.75
// ---------------------------------------------------------------------
constexpr unsigned long ACTUATOR_TRAVEL_MS = 3000;

enum MotorPhase { MOTOR_STOPPED, MOTOR_OPENING, MOTOR_CLOSING };
MotorPhase motorPhase = MOTOR_STOPPED;
unsigned long motor_start_ms = 0;
bool damper_abierta = false;   // Posición estimada de las compuertas
bool fan_pendiente  = false;   // Encender ventilador al terminar apertura
bool fan_on         = false;   // Estado actual del ventilador

// Prototipos (los tipos State/MotorPhase ya están declarados arriba)
void logFSM(const char* msg);
void transitionTo(State newState);
void logTelemetry();

// ---------------------------------------------------------------------
// Logging con timestamp y estado FSM
// ---------------------------------------------------------------------
void logFSM(const char* msg) {
  char buf[40];
  snprintf(buf, sizeof(buf), "[%010lu] FSM[%s] ", millis(), STATE_NAMES[currentState]);
  Serial.print(buf);
  Serial.println(msg);
}

// ---------------------------------------------------------------------
// DIP switch — setpoint (coherente con dip_switch.py)
// Pull-up interno + switch a GND → lógica invertida: pin LOW = bit 1
//
//   SW3 SW2 SW1 | Setpoint        SW1=GP6 (bit 0, LSB)
//    0   0   0  |  40°C           SW2=GP7 (bit 1)
//    0   0   1  |  45°C           SW3=GP0 (bit 2, MSB)
//    0   1   0  |  50°C
//    0   1   1  |  55°C
//    1   0   0  |  60°C
//    1   0   1  |  65°C
//    1   1   0  |  70°C
//    1   1   1  |  75°C
// ---------------------------------------------------------------------
int readDIPCode() {
  int b0 = (digitalRead(PIN_SW1) == LOW) ? 1 : 0;  // SW1 → bit 0 (LSB)
  int b1 = (digitalRead(PIN_SW2) == LOW) ? 1 : 0;  // SW2 → bit 1
  int b2 = (digitalRead(PIN_SW3) == LOW) ? 1 : 0;  // SW3 → bit 2 (MSB)
  return (b2 << 2) | (b1 << 1) | b0;
}

int readSetpoint() {
  int code = readDIPCode();
  // Mapeo estricto a la tabla de valores estandarizados del PDF
  const int setpoints[8] = {40, 45, 50, 55, 60, 65, 70, 75};
  return setpoints[code];
}

void getDIPStatusStr(char* out, size_t len) {
  int code = readDIPCode();
  snprintf(out, len, "DIP=0b%d%d%d SP=%dC +/-%.0fC",
           (code >> 2) & 1, (code >> 1) & 1, code & 1,
           readSetpoint(), HYSTERESIS_C);
}

// ---------------------------------------------------------------------
// Lectura ADC con filtro trimmed-mean (igual que adc_ntc.py)
// ---------------------------------------------------------------------

// Precarga el buffer con lecturas frescas (evita deriva al arrancar)
void fillBuffer(int pin, int* buffer, int& count, int& index) {
  for (int i = 0; i < N_SAMPLES; i++) {
    buffer[i] = analogRead(pin);
  }
  count = N_SAMPLES;
  index = 0;
}

void resetSensors() {
  fillBuffer(PIN_TEMP_INT, buf_int, buf_int_count, buf_int_index);
  fillBuffer(PIN_TEMP_EXT, buf_ext, buf_ext_count, buf_ext_index);
}

// Agrega 1 muestra al buffer circular y retorna el promedio de las
// muestras restantes tras descartar el máximo y el mínimo — O(N)
int getTrimmedMean(int pin, int* buffer, int& count, int& index) {
  int raw = analogRead(pin);
  if (count < N_SAMPLES) {
    buffer[count++] = raw;
  } else {
    buffer[index] = raw;
    index = (index + 1) % N_SAMPLES;
  }

  // Con pocas muestras no tiene sentido recortar extremos
  if (count < 4) {
    long sum = 0;
    for (int i = 0; i < count; i++) sum += buffer[i];
    return sum / count;
  }

  int min_val = buffer[0];
  int max_val = buffer[0];
  long sum = buffer[0];
  for (int i = 1; i < count; i++) {
    int val = buffer[i];
    sum += val;
    if (val < min_val) min_val = val;
    if (val > max_val) max_val = val;
  }
  // Promedio excluyendo máximo y mínimo (elimina picos de ruido/EMI)
  return (sum - min_val - max_val) / (count - 2);
}

// Convierte la lectura filtrada a °C con la ecuación Beta.
// Retorna TEMP_INVALID si el ADC está saturado (NTC desconectado o corto).
float readTemperature(int pin, int* buffer, int& count, int& index) {
  int raw = getTrimmedMean(pin, buffer, count, index);
  if (raw <= 0 || (float)raw >= ADC_MAX) return TEMP_INVALID;

  float r_ntc = R_REF * (float)raw / (ADC_MAX - (float)raw);
  float inv_t = (1.0 / T0_K) + (1.0 / BETA) * log(r_ntc / R0);
  return (1.0 / inv_t) - 273.15;
}

// ---------------------------------------------------------------------
// Salidas: ventilador y puente H (coherente con fan.py / hbridge.py)
// ---------------------------------------------------------------------
void setFan(bool on) {
  digitalWrite(PIN_VENT, on ? HIGH : LOW);  // GP4 → gate MOSFET NMOS
  fan_on = on;
}

// Inicia el travel del actuador (no bloqueante). La detención la hace
// updateMotorTravel() cuando transcurren ACTUATOR_TRAVEL_MS.
void startMotorTravel(bool abrir) {
  digitalWrite(PIN_MOTOR_EN, LOW);             // Deshabilitar antes de cambiar dirección
  digitalWrite(PIN_AIN1, abrir ? LOW : HIGH);  // Abrir:  AIN1=0, AIN2=1 → AO2=1
  digitalWrite(PIN_AIN2, abrir ? HIGH : LOW);  // Cerrar: AIN1=1, AIN2=0 → AO1=1
  digitalWrite(PIN_MOTOR_EN, HIGH);            // PWMA=1 habilita el canal A
  motorPhase = abrir ? MOTOR_OPENING : MOTOR_CLOSING;
  motor_start_ms = millis();
}

// Llamada en cada pasada de loop(): detiene el motor al completar el
// travel (~3 s) sin bloquear. Sustituye el delay() bloqueante del
// firmware MicroPython (que por eso necesita alimentar el WDT cada
// 500 ms durante el travel; aquí el loop nunca se bloquea).
void updateMotorTravel() {
  if (motorPhase == MOTOR_STOPPED) return;
  if (millis() - motor_start_ms < ACTUATOR_TRAVEL_MS) return;

  bool abriendo = (motorPhase == MOTOR_OPENING);

  // Fin de recorrido → estado seguro del puente H (igual que hbridge.stop())
  digitalWrite(PIN_MOTOR_EN, LOW);
  digitalWrite(PIN_AIN1, LOW);
  digitalWrite(PIN_AIN2, LOW);
  motorPhase = MOTOR_STOPPED;
  damper_abierta = abriendo;
  logFSM(abriendo ? "Compuertas ABIERTAS - fin de travel, motor detenido"
                  : "Compuertas CERRADAS - fin de travel, motor detenido");

  // Secuencia COOLING (igual que fsm.py): abrir compuertas → ventilador ON
  if (abriendo && fan_pendiente && currentState == STATE_COOLING) {
    setFan(true);
    logFSM("Ventilador ON (MR1238E48B-FSR via MOSFET NMOS)");
  }
  fan_pendiente = false;
}

// Safe state completo: ventilador OFF + motor detenido + travel cancelado
void stopMotorAndFan() {
  setFan(false);
  fan_pendiente = false;
  digitalWrite(PIN_MOTOR_EN, LOW);
  digitalWrite(PIN_AIN1, LOW);
  digitalWrite(PIN_AIN2, LOW);
  motorPhase = MOTOR_STOPPED;
}

// ---------------------------------------------------------------------
// Transiciones de estado con acciones de entrada (coherente con fsm.py)
// ---------------------------------------------------------------------
void transitionTo(State newState) {
  if (currentState == newState) return;

  char transBuf[48];
  snprintf(transBuf, sizeof(transBuf), "TRANSICION: %s -> %s",
           STATE_NAMES[currentState], STATE_NAMES[newState]);
  logFSM(transBuf);

  currentState = newState;

  switch (newState) {
    case STATE_INIT:
      // Acciones de INIT ejecutadas en run_fsm_step() (como _paso_init de fsm.py)
      break;

    case STATE_READING:
      error_counter = 0;
      resetSensors();  // Precarga buffers con muestras frescas
      logFSM("Evaluando sensores NTC...");
      break;

    case STATE_COOLING:
      ticks_cooling_start = millis();
      logFSM("Abriendo compuertas (FIT0803 via TB6612FNG, ~3 s)...");
      startMotorTravel(true);   // AIN1=0, AIN2=1, MOTOR_EN=1 → LED "MOTOR A ABRE"
      fan_pendiente = true;     // Ventilador ON al completar la apertura
      break;

    case STATE_IDLE:
      if (ticks_cooling_start > 0) {
        char durBuf[64];
        snprintf(durBuf, sizeof(durBuf), "ENFRIAMIENTO OK - duracion ciclo: %.1f s",
                 (millis() - ticks_cooling_start) / 1000.0);
        logFSM(durBuf);
        ticks_cooling_start = 0;
      }
      logFSM("Ventilador OFF");
      setFan(false);
      fan_pendiente = false;
      logFSM("Cerrando compuertas (FIT0803 via TB6612FNG, ~3 s)...");
      startMotorTravel(false);  // AIN1=1, AIN2=0, MOTOR_EN=1 → LED "MOTOR A CIERRA"
      break;

    case STATE_ERROR:
      logFSM("SAFE STATE: ventilador OFF + motor detenido");
      stopMotorAndFan();
      error_counter = 0;
      ticks_error = millis();
      break;

    case STATE_LOCKOUT:
      logFSM("LOCKOUT: ventilador OFF + motor detenido (permanente)");
      stopMotorAndFan();
      ticks_error = millis();
      lockout_setpoint = readSetpoint();  // Un cambio de DIP reinicia la FSM
      break;
  }
}

// ---------------------------------------------------------------------
// Paso de la FSM — ejecutado a 1 Hz desde loop()
// ---------------------------------------------------------------------
void run_fsm_step() {
  watchdog_update();  // Alimentar WDT (timeout 8 s) al inicio de cada step

  // --- INICIO DE LÓGICA DE INYECCIÓN DE TEMPERATURA ---
  bool fsm_eval_blocked = false;
  bool inject_temperature = false;
  int current_setpoint = readSetpoint();
  
  if (last_dip_setpoint == -1) {
    last_dip_setpoint = current_setpoint;
  } else if (current_setpoint != last_dip_setpoint && dip_change_stage == 0) {
    dip_change_stage = 1;
    dip_delay_counter = 0;
    last_dip_setpoint = current_setpoint;
    logFSM("Cambio de DIP detectado. Iniciando retardo 1 (2 muestras)...");
  }

  if (dip_change_stage == 1) {
    fsm_eval_blocked = true;
    dip_delay_counter++;
    if (dip_delay_counter >= 2) {
      dip_change_stage = 2;
      dip_delay_counter = 0;
      logFSM("Retardo 1 completado. Inyectando temperatura...");
    }
  } else if (dip_change_stage == 2) {
    inject_temperature = true;
    fsm_eval_blocked = true;
    dip_delay_counter++;
    if (dip_delay_counter >= 2) {
      dip_change_stage = 3;
      dip_delay_counter = 0;
      logFSM("Retardo 2 completado. Evaluando accion de control...");
    }
  } else if (dip_change_stage == 3) {
    inject_temperature = true;
    dip_change_stage = 0; // Termina la secuencia, permitiendo la evaluación FSM
  }
  // --- FIN DE LÓGICA DE INYECCIÓN ---

  // -- INIT: aplicar safe state y pasar a READING (como _paso_init) ----
  if (currentState == STATE_INIT) {
    stopMotorAndFan();
    error_counter = 0;
    recoveries_count = 0;
    char initBuf[96];
    char dipBuf[48];
    getDIPStatusStr(dipBuf, sizeof(dipBuf));
    snprintf(initBuf, sizeof(initBuf), "Safe state inicial aplicado - %s", dipBuf);
    logFSM(initBuf);
    transitionTo(STATE_READING);
    return;
  }

  // -- ERROR: safe state activo; recovery tras RECOVERY_MS -------------
  if (currentState == STATE_ERROR) {
    unsigned long transcurrido = millis() - ticks_error;
    unsigned long restante_s = (transcurrido >= RECOVERY_MS)
                               ? 0 : (RECOVERY_MS - transcurrido) / 1000;

    static unsigned long last_error_log = 0;
    if (millis() - last_error_log >= 5000) {  // Log cada 5 s (no saturar consola)
      char errorBuf[64];
      snprintf(errorBuf, sizeof(errorBuf), "Safe state activo - recovery #%d en %lu s",
               recoveries_count + 1, restante_s);
      logFSM(errorBuf);
      last_error_log = millis();
    }

    if (transcurrido >= RECOVERY_MS) {
      recoveries_count++;
      if (recoveries_count > MAX_RECOVERIES) {
        char lockBuf[64];
        snprintf(lockBuf, sizeof(lockBuf),
                 "Limite de recoveries (%d) alcanzado - LOCKOUT", MAX_RECOVERIES);
        logFSM(lockBuf);
        transitionTo(STATE_LOCKOUT);
      } else {
        char recBuf[64];
        snprintf(recBuf, sizeof(recBuf), "Recovery #%d - reintentando lectura",
                 recoveries_count);
        logFSM(recBuf);
        transitionTo(STATE_READING);
      }
    }
    return;
  }

  // -- LOCKOUT: fallo permanente; solo un cambio de DIP reinicia -------
  if (currentState == STATE_LOCKOUT) {
    if (readSetpoint() != lockout_setpoint) {
      logFSM("Cambio de DIP detectado en LOCKOUT - reiniciando FSM");
      transitionTo(STATE_INIT);
      return;
    }
    static unsigned long last_lockout_log = 0;
    if (millis() - last_lockout_log >= 10000) {
      logFSM("LOCKOUT ACTIVO - Requiere intervencion de mantenimiento");
      last_lockout_log = millis();
    }
    return;
  }

  // -- READING / COOLING / IDLE: adquisición y evaluación a 1 Hz -------
  temp_int = readTemperature(PIN_TEMP_INT, buf_int, buf_int_count, buf_int_index);
  temp_ext = readTemperature(PIN_TEMP_EXT, buf_ext, buf_ext_count, buf_ext_index);

  // Validación de rango físico del NTC usando valor crudo
  bool ok_int = (temp_int >= TEMP_MIN_C && temp_int <= TEMP_MAX_C);
  bool ok_ext = (temp_ext >= TEMP_MIN_C && temp_ext <= TEMP_MAX_C);
  
  if (ok_int) {
    if (!startup_heat_initialized) {
      simulated_heat_offset = 30.0 - temp_int; // Forzar inicio en 30°C
      startup_heat_initialized = true;
    }

    if (fan_on && damper_abierta) {
      // Enfriamiento activo
      if (temp_int + simulated_heat_offset >= 60.0) {
        simulated_heat_offset -= 3.0; // Desciende más rápido (3°C/s)
      } else {
        simulated_heat_offset -= 1.0; // Regresa a la normalidad (1°C/s)
      }
      
      // No enfriar por debajo de la temperatura externa
      if (temp_int + simulated_heat_offset < temp_ext) {
        simulated_heat_offset = temp_ext - temp_int;
      }
    } else {
      // Calentamiento natural lento
      simulated_heat_offset += 0.5; // Sube 0.5°C por segundo
      // Tope de calentamiento a 85°C
      if (temp_int + simulated_heat_offset > 85.0) {
        simulated_heat_offset = 85.0 - temp_int;
      }
    }
    
    // Inyección de temperatura para la prueba (sobrescribe la lectura)
    if (inject_temperature) {
      float target_temp = (float)current_setpoint + 2.0;
      simulated_heat_offset = target_temp - temp_int; 
    }

    temp_int += simulated_heat_offset; // Aplicar simulacion
  }

  // Delta térmica físicamente imposible entre interior y exterior
  bool delta_invalida = false;
  if (ok_int && ok_ext && fabs(temp_int - temp_ext) > MAX_TEMP_DELTA) {
    delta_invalida = true;
    char deltaBuf[80];
    snprintf(deltaBuf, sizeof(deltaBuf), "WARN: delta INT/EXT %.1f C > %.0f C (imposible)",
             fabs(temp_int - temp_ext), MAX_TEMP_DELTA);
    logFSM(deltaBuf);
  }

  if (!(ok_int && ok_ext && !delta_invalida)) {
    error_counter++;
    char warnBuf[112];
    snprintf(warnBuf, sizeof(warnBuf), "Lectura invalida #%d/%d - INT:%s %.1fC  EXT:%s %.1fC",
             error_counter, MAX_ERRORES_CONSEC,
             ok_int ? "OK" : "FALLA", temp_int,
             ok_ext ? "OK" : "FALLA", temp_ext);
    logFSM(warnBuf);

    if (error_counter >= MAX_ERRORES_CONSEC) {
      transitionTo(STATE_ERROR);  // Safe state: fan OFF + motor detenido
    }
    return;  // Mantener estado actual mientras no supere el límite
  }

  // Lectura válida: limpiar contadores y evaluar umbrales
  error_counter = 0;
  recoveries_count = 0;

  int setpoint = readSetpoint();
  float th_hi = (float)setpoint + HYSTERESIS_C;  // Umbral de activación
  float th_lo = (float)setpoint - HYSTERESIS_C;  // Umbral de desactivación

  char dipBuf[48];
  getDIPStatusStr(dipBuf, sizeof(dipBuf));
  char logBuf[128];
  snprintf(logBuf, sizeof(logBuf), "INT=%.1fC  EXT=%.1fC  TH_LO=%.0f  TH_HI=%.0f  %s",
           temp_int, temp_ext, th_lo, th_hi, dipBuf);
  logFSM(logBuf);

  // Lógica de control:
  //  - Activar COOLING: TEMP_INT supera el setpoint (th_hi) Y TEMP_INT > TEMP_EXT
  //  - Desactivar COOLING: TEMP_INT baja hasta igualar o ser menor a TEMP_EXT
  if (!fsm_eval_blocked) {
    if (currentState == STATE_COOLING) {
      if (temp_int <= temp_ext) {
        transitionTo(STATE_IDLE);
      }
    } else {  // STATE_READING o STATE_IDLE
      if (temp_int > th_hi && temp_int > temp_ext) {
        transitionTo(STATE_COOLING);
      } else if (currentState == STATE_READING) {
        transitionTo(STATE_IDLE);
      }
    }
  }
}

// ---------------------------------------------------------------------
// Telemetría por Serial — 1 línea por ciclo (defensa en sesión en vivo):
// estado FSM, temperaturas, setpoint y salidas (VENT, compuerta, GPIOs)
// ---------------------------------------------------------------------
const char* motorStatusStr() {
  switch (motorPhase) {
    case MOTOR_OPENING: return "ABRIENDO";
    case MOTOR_CLOSING: return "CERRANDO";
    default:            return damper_abierta ? "ABIERTA" : "CERRADA";
  }
}

void logTelemetry() {
  char buf[160];
  snprintf(buf, sizeof(buf),
           "[%010lu] TLM EST=%s INT=%.1fC EXT=%.1fC SP=%dC VENT=%s COMPUERTA=%s "
           "AIN1=%d AIN2=%d EN=%d",
           millis(), STATE_NAMES[currentState], temp_int, temp_ext, readSetpoint(),
           fan_on ? "ON" : "OFF", motorStatusStr(),
           digitalRead(PIN_AIN1), digitalRead(PIN_AIN2), digitalRead(PIN_MOTOR_EN));
  Serial.println(buf);
}

// ---------------------------------------------------------------------
// setup / loop
// ---------------------------------------------------------------------
void setup() {
  Serial.begin(115200);
  analogReadResolution(12);  // ADC del RP2040 a 12 bits (0..4095)

  pinMode(PIN_SW1, INPUT_PULLUP);  // DIP a GND → LOW = bit 1
  pinMode(PIN_SW2, INPUT_PULLUP);
  pinMode(PIN_SW3, INPUT_PULLUP);
  pinMode(PIN_AIN1, OUTPUT);
  pinMode(PIN_AIN2, OUTPUT);
  pinMode(PIN_MOTOR_EN, OUTPUT);
  pinMode(PIN_VENT, OUTPUT);

  // Safe state inmediato al arrancar (fail-safe)
  stopMotorAndFan();

  // Watchdog hardware del RP2040: 8 s (se alimenta en cada step de la FSM)
  watchdog_enable(8000, true);

  Serial.println("=====================================================");
  Serial.println(" Sistema de extraccion de aire caliente - Jaguar MX");
  Serial.println(" Simulacion Wokwi (RP2040) - Ing. Jair Molina Arce");
  Serial.println("=====================================================");
  // currentState arranca en STATE_INIT; el primer step ejecuta el
  // auto-diagnostico/safe state y transiciona a READING.
}

unsigned long last_step_time = 0;
constexpr unsigned long STEP_INTERVAL = 1000;  // Loop de control a 1 Hz

void loop() {
  // Temporización NO bloqueante del travel del actuador (~3 s)
  updateMotorTravel();

  // Paso de la FSM a 1 Hz con compensación de deriva (sin delay())
  unsigned long now = millis();
  if (now - last_step_time >= STEP_INTERVAL) {
    run_fsm_step();
    logTelemetry();

    unsigned long duration = millis() - now;
    if (duration >= STEP_INTERVAL) {
      last_step_time = millis();          // Ciclo extendido: realinear base
    } else {
      last_step_time += STEP_INTERVAL;    // Ciclo normal: sin deriva acumulada
    }
  }

  // Efecto visual: ventilador a capacidad máxima (parpadeo) en alta temperatura (>= 60°C)
  if (fan_on) {
    if (temp_int >= 60.0) {
      // Reducimos la frecuencia de parpadeo (150ms) para que sea claramente visible en Wokwi
      digitalWrite(PIN_VENT, ((millis() / 150) % 2 == 0) ? HIGH : LOW);
    } else {
      digitalWrite(PIN_VENT, HIGH);
    }
  }
}
