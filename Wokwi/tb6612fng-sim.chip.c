// tb6612fng-sim.chip.c — Modelo simplificado del TB6612FNG para Wokwi
// Sistema de extraccion de aire caliente — Jaguar de Mexico
// Candidato: Ing. Jair Molina Arce
//
// Modelo a nivel logico unicamente: NO simula corriente, caida de
// tension, apagado termico, par de frenado ni comportamiento inductivo.
//
// Tabla de verdad implementada (por canal, segun datasheet Toshiba):
//   STBY  PWM  IN1  IN2 | OUT1  OUT2 | Modo
//    L     x    x    x  |  L     L   | Standby (puente deshabilitado)
//    H     L    x    x  |  L     L   | Short brake (motor detenido)
//    H     H    L    H  |  L     H   | CCW  -> abre compuertas (canal A)
//    H     H    H    L  |  H     L   | CW   -> cierra compuertas (canal A)
//    H     H    H    H  |  L     L   | Short brake (ambas salidas a GND)
//    H     H    L    L  |  L     L   | Stop / coast
//
// En la simulacion los LEDs conectados a AO1/AO2 indican:
//   AO2=HIGH -> LED "MOTOR A ABRE"   (AIN1=0, AIN2=1, PWMA=1, STBY=1)
//   AO1=HIGH -> LED "MOTOR A CIERRA" (AIN1=1, AIN2=0, PWMA=1, STBY=1)
//   PWMA=0 o STBY=0 -> AO1=AO2=LOW (ambos LEDs apagados)

#include "wokwi-api.h"
#include <stdbool.h>
#include <stdint.h>
#include <stdlib.h>

typedef struct {
  pin_t stby;

  // Canal A (usado por el firmware para el actuador FIT0803)
  pin_t pwma;
  pin_t ain1;
  pin_t ain2;
  pin_t ao1;
  pin_t ao2;

  // Canal B (no usado; entradas fijadas a GND en diagram.json)
  pin_t pwmb;
  pin_t bin1;
  pin_t bin2;
  pin_t bo1;
  pin_t bo2;
} chip_state_t;

// Aplica la tabla de verdad de un canal del puente H
static void drive_channel(pin_t pwm, pin_t in1, pin_t in2,
                          pin_t out1, pin_t out2, bool standby_enabled) {
  bool enabled = standby_enabled && pin_read(pwm);

  if (!enabled) {
    // Standby (STBY=L) o PWM=L: salidas en bajo (motor detenido)
    pin_write(out1, LOW);
    pin_write(out2, LOW);
    return;
  }

  bool a = pin_read(in1);
  bool b = pin_read(in2);

  if (a && !b) {
    // CW: OUT1=H, OUT2=L (canal A: cierra compuertas)
    pin_write(out1, HIGH);
    pin_write(out2, LOW);
  } else if (!a && b) {
    // CCW: OUT1=L, OUT2=H (canal A: abre compuertas)
    pin_write(out1, LOW);
    pin_write(out2, HIGH);
  } else {
    // IN1=IN2=H -> short brake (datasheet: OUT1=OUT2=L, ambas a GND)
    // IN1=IN2=L -> stop/coast   (OUT1=OUT2=L a nivel logico)
    pin_write(out1, LOW);
    pin_write(out2, LOW);
  }
}

// Recalcula ambos canales a partir del estado actual de las entradas
static void update_outputs(chip_state_t *chip) {
  bool standby_enabled = pin_read(chip->stby);

  drive_channel(chip->pwma, chip->ain1, chip->ain2, chip->ao1, chip->ao2, standby_enabled);
  drive_channel(chip->pwmb, chip->bin1, chip->bin2, chip->bo1, chip->bo2, standby_enabled);
}

// Callback de cambio de pin: cualquier flanco re-evalua las salidas
static void pin_changed(void *user_data, pin_t pin, uint32_t value) {
  (void)pin;
  (void)value;
  update_outputs((chip_state_t *)user_data);
}

// Registra observacion de ambos flancos (BOTH) sobre un pin de entrada
static void watch_pin(pin_t pin, chip_state_t *chip) {
  const pin_watch_config_t config = {
    .edge = BOTH,
    .pin_change = pin_changed,
    .user_data = chip,
  };
  pin_watch(pin, &config);
}

void chip_init(void) {
  chip_state_t *chip = malloc(sizeof(chip_state_t));
  if (!chip) return;

  // Pull-up interno en STBY: el chip queda activo por defecto si el pin
  // se deja sin cablear (igual que las placas breakout comerciales).
  // En diagram.json STBY va cableado a 3V3 (CRITICO en hardware real).
  chip->stby = pin_init("STBY", INPUT_PULLUP);

  // Canal A: entradas de control y salidas de motor
  chip->pwma = pin_init("PWMA", INPUT);
  chip->ain1 = pin_init("AIN1", INPUT);
  chip->ain2 = pin_init("AIN2", INPUT);
  chip->ao1  = pin_init("AO1", OUTPUT_LOW);   // Arranque en estado seguro
  chip->ao2  = pin_init("AO2", OUTPUT_LOW);

  // Canal B: entradas de control y salidas de motor
  chip->pwmb = pin_init("PWMB", INPUT);
  chip->bin1 = pin_init("BIN1", INPUT);
  chip->bin2 = pin_init("BIN2", INPUT);
  chip->bo1  = pin_init("BO1", OUTPUT_LOW);
  chip->bo2  = pin_init("BO2", OUTPUT_LOW);

  // Nota: VM, VCC y GND estan declarados en el .chip.json como puntos de
  // conexion (alimentacion); no requieren logica en este modelo.

  // Observar todas las entradas que afectan las salidas
  watch_pin(chip->stby, chip);
  watch_pin(chip->pwma, chip);
  watch_pin(chip->ain1, chip);
  watch_pin(chip->ain2, chip);
  watch_pin(chip->pwmb, chip);
  watch_pin(chip->bin1, chip);
  watch_pin(chip->bin2, chip);

  // Estado inicial coherente con las entradas presentes al arrancar
  update_outputs(chip);
}
