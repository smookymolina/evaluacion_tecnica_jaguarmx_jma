import re

sch_path = r"C:\Users\GIRTEC\Claude\Projects\Jaguar MX\kicad\PCB\PCB.kicad_sch"

with open(sch_path, 'r', encoding='utf-8') as f:
    content = f.read()

wires = re.findall(r'\(wire\s*\(pts\s*\(xy\s+([\d.-]+)\s+([\d.-]+)\)\s*\(xy\s+([\d.-]+)\s+([\d.-]+)\)\s*\)', content)

print("Wires with 45.72:")
for w in wires:
    if "45.72" in w[0] or "45.72" in w[2]:
        print(f"Wire: ({w[0]}, {w[1]}) -> ({w[2]}, {w[3]})")
