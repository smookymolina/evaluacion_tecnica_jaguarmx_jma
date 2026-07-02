import re

sch_path = r"C:\Users\GIRTEC\Claude\Projects\Jaguar MX\kicad\PCB\PCB.kicad_sch"

with open(sch_path, 'r', encoding='utf-8') as f:
    content = f.read()

wires = re.findall(r'\(wire\s*\(pts\s*\(xy\s+([\d.-]+)\s+([\d.-]+)\)\s*\(xy\s+([\d.-]+)\s+([\d.-]+)\)\s*\)', content)

print("All wires in schematic:")
for idx, w in enumerate(wires):
    print(f"Wire {idx+1}: ({w[0]}, {w[1]}) -> ({w[2]}, {w[3]})")
