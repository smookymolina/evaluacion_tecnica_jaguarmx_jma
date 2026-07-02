# test_firmware.py
"""
Pruebas unitarias para validar la lógica del firmware localmente.
"""
import sys
import unittest

# Parchear los módulos de hardware machine y time antes de importar el firmware
import mock_machine
import mock_time
sys.modules['machine'] = mock_machine
sys.modules['time'] = mock_time

# Añadir la carpeta de firmware al path de importaciones
sys.path.insert(0, './firmware')

import adc_ntc
import dip_switch
import hbridge
import fan
import fsm

class TestFirmware(unittest.TestCase):
    def setUp(self):
        # Reset de tiempo simulado y buffers de sensores
        mock_time._current_time_ms = 1000
        adc_ntc.reset_sensors()
        hbridge.hbridge.stop()
        fan.fan.off()
        # Reset de pines DIP
        dip_switch.dip._sw1.value(1)
        dip_switch.dip._sw2.value(1)
        dip_switch.dip._sw3.value(1)

    def test_dip_switch_setpoints(self):
        # Estado por defecto (todos HIGH = no presionados = 0b000)
        self.assertEqual(dip_switch.dip.read_setpoint(), 40)
        self.assertEqual(dip_switch.dip.threshold_high(), 41.0)
        self.assertEqual(dip_switch.dip.threshold_low(), 39.0)

        # Simular DIP switch en 0b101 (SW3 y SW1 en LOW/presionado, SW2 en HIGH/suelto)
        dip_switch.dip._sw3.value(0)  # MSB = 1
        dip_switch.dip._sw2.value(1)  # Bit 1 = 0
        dip_switch.dip._sw1.value(0)  # LSB = 1
        self.assertEqual(dip_switch.dip.read_setpoint(), 65)
        self.assertEqual(dip_switch.dip.threshold_high(), 66.0)
        self.assertEqual(dip_switch.dip.threshold_low(), 64.0)

    def test_adc_ntc_conversion(self):
        # 32768 es la mitad de 65535, por divisor de tensión R_NTC = R_REF = 10kOhm.
        # R_NTC = 10kOhm corresponde exactamente a T0 = 25 °C (298.15 K).
        adc_ntc.sensor_int._adc.set_mock_value(32768)
        ok, temp = adc_ntc.sensor_int.read()
        self.assertTrue(ok)
        self.assertAlmostEqual(temp, 25.0, places=1)

    def test_hbridge_control(self):
        hbridge.hbridge.open_dampers()
        # Al finalizar el travel, el motor debe detenerse automáticamente
        self.assertEqual(hbridge.hbridge.state, hbridge.HBridge.STATE_STOPPED)
        self.assertEqual(hbridge.hbridge._motor_en.value(), 0)

    def test_fsm_transitions(self):
        # Instanciar FSM en modo test (sin watchdog físico de hardware)
        thermal_fsm = fsm.ThermalFSM(enable_watchdog=False, verbose=False)
        self.assertEqual(thermal_fsm._state.estado, fsm._STATE_INIT)

        # Paso 1: INIT -> READING
        thermal_fsm.step()
        self.assertEqual(thermal_fsm._state.estado, fsm._STATE_READING)

        # Configurar lecturas de sensores:
        # TEMP_INT = 45 °C (R_NTC ≈ 4381 Ohm, ADC raw ≈ 19964)
        adc_ntc.sensor_int._adc.set_mock_value(19964)
        # TEMP_EXT = 30 °C (R_NTC ≈ 8113 Ohm, ADC raw ≈ 29354)
        adc_ntc.sensor_ext._adc.set_mock_value(29354)
        adc_ntc.reset_sensors()

        # Paso 2: Evaluar. Como 45 > Umbral Alto (41) y 45 > 30, debe ir a COOLING
        thermal_fsm.step()
        self.assertEqual(thermal_fsm._state.estado, fsm._STATE_COOLING)
        self.assertTrue(fan.fan.is_on())

        # Cambiar TEMP_INT a 35 °C (R_NTC ≈ 6672 Ohm, ADC raw ≈ 26226)
        # Como 35 <= Umbral Bajo (39), debe ir a IDLE
        adc_ntc.sensor_int._adc.set_mock_value(26226)
        adc_ntc.reset_sensors()
        thermal_fsm.step()
        self.assertEqual(thermal_fsm._state.estado, fsm._STATE_IDLE)
        self.assertFalse(fan.fan.is_on())

    def test_fsm_sensor_error_recovery(self):
        thermal_fsm = fsm.ThermalFSM(enable_watchdog=False, verbose=False)
        thermal_fsm.step()  # INIT -> READING

        # Simular lectura inválida (sensor desconectado, ADC raw = 65535)
        adc_ntc.sensor_int._adc.set_mock_value(65535)

        # Se requieren 3 errores consecutivos para pasar a ERROR
        thermal_fsm.step()  # Errores = 1
        self.assertEqual(thermal_fsm._state.estado, fsm._STATE_READING)
        thermal_fsm.step()  # Errores = 2
        self.assertEqual(thermal_fsm._state.estado, fsm._STATE_READING)
        thermal_fsm.step()  # Errores = 3 -> TRANSICION A ERROR
        self.assertEqual(thermal_fsm._state.estado, fsm._STATE_ERROR)
        self.assertFalse(fan.fan.is_on())

        # Avanzar el tiempo simulado en 30 segundos para cumplir tiempo de recovery
        mock_time._current_time_ms += 30000
        thermal_fsm.step()  # Intento de recovery -> transiciona a READING
        self.assertEqual(thermal_fsm._state.estado, fsm._STATE_READING)

if __name__ == '__main__':
    unittest.main()
