# =====================================================================
#  CAPA 2 - Alcanzabilidad del broker MQTT (PowerShell / Windows)
# ---------------------------------------------------------------------
#  Prueba TCP pura al broker: no publica nada, solo comprueba que el
#  puerto 1883 escucha y que la red/firewall lo dejan pasar.
#
#  Uso:
#    powershell -ExecutionPolicy Bypass -File capa2_check_broker.ps1
#    (o simplemente:  .\capa2_check_broker.ps1  desde una terminal PS)
# =====================================================================

$BrokerHost = "10.146.0.87"   # <-- debe coincidir con serial_mqtt_bridge.py
$BrokerPort = 1883

Write-Host ("=" * 60)
Write-Host " CAPA 2 - Broker MQTT alcanzable"
Write-Host ("=" * 60)
Write-Host " Probando  $BrokerHost : $BrokerPort ..."

$r = Test-NetConnection $BrokerHost -Port $BrokerPort -WarningAction SilentlyContinue

Write-Host ("=" * 60)
if ($r.TcpTestSucceeded) {
    Write-Host " OK - broker alcanzable (origen $($r.SourceAddress))" -ForegroundColor Green
    exit 0
} else {
    Write-Host " FALLO - no se pudo conectar a $BrokerHost : $BrokerPort" -ForegroundColor Red
    Write-Host "   Revisa: Mosquitto corriendo en el servidor, IP correcta,"
    Write-Host "   misma red, y firewall permitiendo el puerto 1883."
    exit 1
}
