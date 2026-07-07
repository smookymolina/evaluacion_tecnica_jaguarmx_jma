#include <Arduino.h>
// =====================================================================
// main.cpp — Firmware de demostración con planta térmica simulada
// (Seeed XIAO RP2350)
// Sistema de extracción de aire caliente — Jaguar de México
// Candidato: Ing. Jair Molina Arce
//
// Variante de demostración del firmware de prueba física: la FSM, el
// puente H TB6612FNG (actuador FIT0803), el ventilador (MOSFET) y el
// DIP switch operan sobre los GPIOs REALES de la placa, pero las
// temperaturas provienen de un modelo térmico interno en lugar de los
// NTC. Permite demostrar el ciclo completo (COOLING / IDLE / ERROR /
// LOCKOUT) en un ambiente controlado, sin calentar físicamente el
// gabinete ni depender de los sensores.
//
//   FSM: INIT → READING → COOLING / IDLE / ERROR (+ LOCKOUT)
//   - COOLING si TEMP_INT > (SETPOINT + 1°C)  Y  TEMP_INT > TEMP_EXT
//   - IDLE    si TEMP_INT <= TEMP_EXT
//   - ERROR   tras 3 lecturas inválidas consecutivas → safe state
//             (ventilador OFF, motor detenido) → recovery a los 30 s
//
// Modelo térmico (paso de 1 s, sincronizado con la FSM a 1 Hz):
//   - Ventilador OFF o compuertas cerradas: la temperatura interna
//     sube heat_rate °C/s hasta un tope de SIM_TEMP_TOPE (equipo de
//     telecom disipando dentro del gabinete cerrado).
//   - Ventilador ON y compuertas abiertas: baja cool_rate °C/s, sin
//     caer por debajo de la temperatura exterior (límite físico de un
//     sistema de extracción de aire).
//   - FALLA:INT / FALLA:EXT / FALLA:AMBOS simulan NTC desconectado
//     (lectura inválida) para demostrar ERROR → recovery → LOCKOUT.
//
// Comandos por Serial (115200 baudios, terminados en Enter):
//   SET:<C>      Setpoint manual (SET:0 regresa al DIP switch)
//   TEMP:<C>     Fija la temperatura interna del modelo
//   EXT:<C>      Fija la temperatura exterior del modelo
//   RATE:<C/s>   Tasa de calentamiento (default 0.5 °C/s)
//   COOL:<C/s>   Tasa de enfriamiento (default 1.5 °C/s)
//   FALLA:INT | FALLA:EXT | FALLA:AMBOS | FALLA:OFF
// =====================================================================

#include <math.h>

#ifdef ARDUINO_ARCH_RP2040
#include "hardware/watchdog.h"   // WDT hardware del RP2350 (pico-sdk)
#else
// Mocks para poder compilar fuera del target (el WDT solo existe ahí)
void watchdog_enable(uint32_t delay_ms, bool pause_on_debug) {}
void watchdog_update() {}
#endif

// ---------------------------------------------------------------------
// Mapa de GPIOs (documento oficial Jaguar — NO cambiar sin justificación)
// Los NTC (GPIO26/27) no se leen en esta variante: la temperatura viene
// del modelo simulado. Las salidas y el DIP sí son físicas.
// ---------------------------------------------------------------------
constexpr int PIN_SW1      = 6;   // DIP bit 0 (LSB), pull-up interno
constexpr int PIN_SW2      = 7;   // DIP bit 1,       pull-up interno
constexpr int PIN_SW3      = 0;   // DIP bit 2 (MSB), pull-up interno
constexpr int PIN_AIN1     = 2;   // TB6612FNG AIN1 (dirección 1)
constexpr int PIN_AIN2     = 1;   // TB6612FNG AIN2 (dirección 2)
constexpr int PIN_MOTOR_EN = 3;   // TB6612FNG PWMA (habilitación canal A)
constexpr int PIN_VENT     = 4;   // MOSFET NMOS — ventilador 48V

// ---------------------------------------------------------------------
// Rango físico válido del NTC TT05 (se conserva la misma validación que
// el firmware físico: una falla simulada entrega TEMP_INVALID, fuera de
// rango, y dispara el mismo camino de ERROR).
// ---------------------------------------------------------------------
constexpr float TEMP_MIN_C   = -40.0;
constexpr float TEMP_MAX_C   = 105.0;
constexpr float TEMP_INVALID = -999.0;  // Marcador de lectura inválida

// ---------------------------------------------------------------------
// Planta térmica simulada
// ---------------------------------------------------------------------
constexpr float SIM_TEMP_TOPE = 85.0;  // Tope de calentamiento del gabinete
float sim_temp_int = 30.0;             // Temperatura interna inicial
float sim_temp_ext = 25.0;             // Temperatura exterior inicial
float heat_rate    = 0.5;              // °C/s con ventilador OFF
float cool_rate    = 1.5;              // °C/s con ventilador ON + compuerta abierta
bool  falla_int    = false;            // Simula NTC interno desconectado
bool  falla_ext    = false;            // Simula NTC externo desconectado

// ---------------------------------------------------------------------
// FSM — estados y parámetros (idéntico al firmware físico)
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
int error_counter = 0;                // Lecturas inválidas consecutivas
unsigned long ticks_error = 0;        // millis() al entrar a ERROR/LOCKOUT
int recoveries_count = 0;             // Intentos de recovery realizados
unsigned long ticks_cooling_start = 0;// millis() al iniciar enfriamiento
int lockout_setpoint = -1;            // Setpoint capturado al entrar a LOCKOUT

int override_setpoint = -1;           // SET:<C> ignora el DIP (-1 = DIP)

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
// DIP switch — setpoint (idéntico al firmware físico)
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
  if (override_setpoint != -1) {
    return override_setpoint;
  }
  int code = readDIPCode();
  // Mapeo estricto a la tabla de valores estandarizados del PDF
  const int setpoints[8] = {40, 45, 50, 55, 60, 65, 70, 75};
  return setpoints[code];
}

void getDIPStatusStr(char* out, size_t len) {
  int code = readDIPCode();
  if (override_setpoint != -1) {
    snprintf(out, len, "DIP=0b%d%d%d SP=%dC(OVR) +/-%.0fC",
             (code >> 2) & 1, (code >> 1) & 1, code & 1,
             readSetpoint(), HYSTERESIS_C);
  } else {
    snprintf(out, len, "DIP=0b%d%d%d SP=%dC +/-%.0fC",
             (code >> 2) & 1, (code >> 1) & 1, code & 1,
             readSetpoint(), HYSTERESIS_C);
  }
}

// ---------------------------------------------------------------------
// Planta térmica simulada — avanza 1 paso (1 s) por ciclo de la FSM.
// Sustituye a la lectura de los NTC del firmware físico; el resto del
// pipeline (validación de rango, contador de errores, FSM) es idéntico.
// ---------------------------------------------------------------------
void stepThermalModel() {
  if (fan_on && damper_abierta) {
    // Extracción activa: enfría hacia la temperatura exterior
    sim_temp_int -= cool_rate;
    if (sim_temp_int < sim_temp_ext) {
      sim_temp_int = sim_temp_ext;  // No enfría por debajo del exterior
    }
  } else {
    // Gabinete cerrado: el equipo de telecom calienta el aire interno
    sim_temp_int += heat_rate;
    if (sim_temp_int > SIM_TEMP_TOPE) {
      sim_temp_int = SIM_TEMP_TOPE;
    }
  }
}

float readTemperatureInt() {
  return falla_int ? TEMP_INVALID : sim_temp_int;
}

float readTemperatureExt() {
  return falla_ext ? TEMP_INVALID : sim_temp_ext;
}

// ---------------------------------------------------------------------
// Salidas: ventilador y puente H (idéntico al firmware físico)
// ---------------------------------------------------------------------
void setFan(bool on) {
  digitalWrite(PIN_VENT, on ? HIGH : LOW);  // GP4 → gate MOSFET NMOS
  fan_on = on;
}

// Inicia el travel del actuador (no bloqueante). La detención la hace
// updateMotorTravel() cuando transcurren ACTUATOR_TRAVEL_MS.
void startMotorTravel(bool abrir) {
  digitalWrite(PIN_MOTOR_EN, LOW);             // Deshabilitar antes de cambiar dirección
  digitalWrite(PIN_AIN1, abrir ? LOW : HIGH);  // Abrir:  AIN1=0, AIN2=1 (extiende)
  digitalWrite(PIN_AIN2, abrir ? HIGH : LOW);  // Cerrar: AIN1=1, AIN2=0 (retrae)
  digitalWrite(PIN_MOTOR_EN, HIGH);            // PWMA=1 habilita el canal A
  motorPhase = abrir ? MOTOR_OPENING : MOTOR_CLOSING;
  motor_start_ms = millis();
}

// Llamada en cada pasada de loop(): detiene el motor al completar el
// travel (~3 s) sin bloquear.
void updateMotorTravel() {
  if (motorPhase == MOTOR_STOPPED) return;
  if (millis() - motor_start_ms < ACTUATOR_TRAVEL_MS) return;

  bool abriendo = (motorPhase == MOTOR_OPENING);

  // Fin de recorrido → estado seguro del puente H
  digitalWrite(PIN_MOTOR_EN, LOW);
  digitalWrite(PIN_AIN1, LOW);
  digitalWrite(PIN_AIN2, LOW);
  motorPhase = MOTOR_STOPPED;
  damper_abierta = abriendo;
  logFSM(abriendo ? "Compuertas ABIERTAS - fin de travel, motor detenido"
                  : "Compuertas CERRADAS - fin de travel, motor detenido");

  // Secuencia COOLING: abrir compuertas → ventilador ON
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
// Transiciones de estado con acciones de entrada (idéntico al físico)
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
      // Acciones de INIT ejecutadas en run_fsm_step()
      break;

    case STATE_READING:
      error_counter = 0;
      logFSM("Evaluando sensores (planta simulada)...");
      break;

    case STATE_COOLING:
      ticks_cooling_start = millis();
      logFSM("Abriendo compuertas (FIT0803 via TB6612FNG, ~3 s)...");
      startMotorTravel(true);   // AIN1=0, AIN2=1, MOTOR_EN=1 → extiende
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
      startMotorTravel(false);  // AIN1=1, AIN2=0, MOTOR_EN=1 → retrae
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

  // -- INIT: aplicar safe state y pasar a READING ----------------------
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

  // -- READING / COOLING / IDLE: modelo térmico y evaluación a 1 Hz ----
  stepThermalModel();
  temp_int = readTemperatureInt();
  temp_ext = readTemperatureExt();

  // Validación de rango físico (mismo criterio que el firmware físico)
  bool ok_int = (temp_int >= TEMP_MIN_C && temp_int <= TEMP_MAX_C);
  bool ok_ext = (temp_ext >= TEMP_MIN_C && temp_ext <= TEMP_MAX_C);

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

// ---------------------------------------------------------------------
// Telemetría por Serial — 1 línea por ciclo: estado FSM, temperaturas
// (marcadas SIM), setpoint y salidas físicas (VENT, compuerta, GPIOs)
// ---------------------------------------------------------------------
const char* motorStatusStr() {
  switch (motorPhase) {
    case MOTOR_OPENING: return "ABRIENDO";
    case MOTOR_CLOSING: return "CERRANDO";
    default:            return damper_abierta ? "ABIERTA" : "CERRADA";
  }
}

void logTelemetry() {
  char buf[176];
  snprintf(buf, sizeof(buf),
           "[%010lu] TLM(SIM) EST=%s INT=%.1fC%s EXT=%.1fC%s SP=%dC VENT=%s COMPUERTA=%s "
           "AIN1=%d AIN2=%d EN=%d",
           millis(), STATE_NAMES[currentState],
           temp_int, falla_int ? "(FALLA)" : "",
           temp_ext, falla_ext ? "(FALLA)" : "",
           readSetpoint(),
           fan_on ? "ON" : "OFF", motorStatusStr(),
           digitalRead(PIN_AIN1), digitalRead(PIN_AIN2), digitalRead(PIN_MOTOR_EN));
  Serial.println(buf);
}

// ---------------------------------------------------------------------
// Comandos Serial del simulador
// ---------------------------------------------------------------------
void processSerialCommand(String cmd) {
  cmd.trim();
  if (cmd.startsWith("SET:")) {
    int val = cmd.substring(4).toInt();
    if (val <= 0) {
      override_setpoint = -1;
      Serial.println("Comando recibido: Setpoint manual desactivado (regresa al DIP switch)");
    } else {
      override_setpoint = val;
      Serial.print("Comando recibido: Setpoint manual fijado a ");
      Serial.println(val);
    }
  } else if (cmd.startsWith("TEMP:")) {
    sim_temp_int = cmd.substring(5).toFloat();
    Serial.print("Comando recibido: Temp interna del modelo fijada a ");
    Serial.println(sim_temp_int);
  } else if (cmd.startsWith("EXT:")) {
    sim_temp_ext = cmd.substring(4).toFloat();
    Serial.print("Comando recibido: Temp exterior del modelo fijada a ");
    Serial.println(sim_temp_ext);
  } else if (cmd.startsWith("RATE:")) {
    float val = cmd.substring(5).toFloat();
    if (val >= 0.0) {
      heat_rate = val;
      Serial.print("Comando recibido: Tasa de calentamiento fijada a ");
      Serial.print(heat_rate);
      Serial.println(" C/s");
    }
  } else if (cmd.startsWith("COOL:")) {
    float val = cmd.substring(5).toFloat();
    if (val >= 0.0) {
      cool_rate = val;
      Serial.print("Comando recibido: Tasa de enfriamiento fijada a ");
      Serial.print(cool_rate);
      Serial.println(" C/s");
    }
  } else if (cmd.startsWith("FALLA:")) {
    String arg = cmd.substring(6);
    if (arg.equalsIgnoreCase("INT")) {
      falla_int = true;
      Serial.println("Comando recibido: FALLA en NTC interno (lectura invalida)");
    } else if (arg.equalsIgnoreCase("EXT")) {
      falla_ext = true;
      Serial.println("Comando recibido: FALLA en NTC externo (lectura invalida)");
    } else if (arg.equalsIgnoreCase("AMBOS")) {
      falla_int = true;
      falla_ext = true;
      Serial.println("Comando recibido: FALLA en ambos NTC (lectura invalida)");
    } else if (arg.equalsIgnoreCase("OFF")) {
      falla_int = false;
      falla_ext = false;
      Serial.println("Comando recibido: Fallas de NTC desactivadas");
    } else {
      Serial.println("Uso: FALLA:INT | FALLA:EXT | FALLA:AMBOS | FALLA:OFF");
    }
  } else if (cmd.length() > 0) {
    Serial.println("Comandos: SET:<C> TEMP:<C> EXT:<C> RATE:<C/s> COOL:<C/s> FALLA:INT|EXT|AMBOS|OFF");
  }
}

// ---------------------------------------------------------------------
// setup / loop
// ---------------------------------------------------------------------
void setup() {
  Serial.begin(115200);

  pinMode(PIN_SW1, INPUT_PULLUP);  // DIP a GND → LOW = bit 1
  pinMode(PIN_SW2, INPUT_PULLUP);
  pinMode(PIN_SW3, INPUT_PULLUP);
  pinMode(PIN_AIN1, OUTPUT);
  pinMode(PIN_AIN2, OUTPUT);
  pinMode(PIN_MOTOR_EN, OUTPUT);
  pinMode(PIN_VENT, OUTPUT);

  // Safe state inmediato al arrancar (fail-safe)
  stopMotorAndFan();

  // Watchdog hardware: 8 s (se alimenta en cada step de la FSM)
  watchdog_enable(8000, true);

  Serial.println("=====================================================");
  Serial.println(" Sistema de extraccion de aire caliente - Jaguar MX");
  Serial.println(" DEMO planta termica SIMULADA - Ing. Jair Molina Arce");
  Serial.println(" Comandos: SET:<C> TEMP:<C> EXT:<C> RATE:<C/s>");
  Serial.println("           COOL:<C/s> FALLA:INT|EXT|AMBOS|OFF");
  Serial.println("=====================================================");
  // currentState arranca en STATE_INIT; el primer step ejecuta el
  // auto-diagnostico/safe state y transiciona a READING.
}

unsigned long last_step_time = 0;
constexpr unsigned long STEP_INTERVAL = 1000;  // Loop de control a 1 Hz

void loop() {
  // --- Procesamiento de comandos Serial ---
  if (Serial.available() > 0) {
    processSerialCommand(Serial.readStringUntil('\n'));
  }

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
}
