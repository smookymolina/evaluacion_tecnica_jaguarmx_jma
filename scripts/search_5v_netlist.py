import re

netlist_path = r"C:\Users\GIRTEC\Claude\Projects\Jaguar MX\FASE2.1_Netlist_Corregido_JaguarMX.md"

with open(netlist_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Let's search for lines containing "+5V" or "VM" or "V_MOTOR"
print("Lines with +5V or VM:")
for line in content.split('\n'):
    if "+5V" in line or "VM" in line or "V_MOTOR" in line or "VCC" in line:
        print(line.encode('ascii', errors='replace').decode('ascii'))
