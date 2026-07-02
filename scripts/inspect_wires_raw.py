import re

sch_path = r"C:\Users\GIRTEC\Claude\Projects\Jaguar MX\kicad\PCB\PCB.kicad_sch"

with open(sch_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Find all wire S-expressions
wires = re.findall(r'\(wire\s*\(pts\s*\(xy\s+([\d.-]+)\s+([\d.-]+)\)\s*\(xy\s+([\d.-]+)\s+([\d.-]+)\)\s*\)', content)

print("Wires with X in [120, 150] or Y in [20, 65]:")
for w in wires:
    x1, y1, x2, y2 = float(w[0]), float(w[1]), float(w[2]), float(w[3])
    if (120 <= x1 <= 150 or 120 <= x2 <= 150) or (20 <= y1 <= 65 or 20 <= y2 <= 65):
        print(f"Wire: ({x1}, {y1}) -> ({x2}, {y2})")
