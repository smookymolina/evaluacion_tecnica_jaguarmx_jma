import re

sch_path = r"C:\Users\GIRTEC\Claude\Projects\Jaguar MX\kicad\PCB\PCB.kicad_sch"

with open(sch_path, 'r', encoding='utf-8') as f:
    content = f.read()

wires = re.findall(r'\(wire\s*\(pts\s*\(xy\s+([\d.-]+)\s+([\d.-]+)\)\s*\(xy\s+([\d.-]+)\s+([\d.-]+)\)\s*\)', content)

print("Wires close to SW1, C12, C13, C14:")
for w in wires:
    x1, y1, x2, y2 = float(w[0]), float(w[1]), float(w[2]), float(w[3])
    # SW1 is at (135.89, 73.66)
    # C12 is at (25.4, 71.12)
    # C13 is at (25.4, 80.01)
    # C14 is at (25.4, 88.9)
    if (abs(x1 - 25.4) < 10 or abs(x2 - 25.4) < 10) or (abs(x1 - 135.89) < 10 or abs(x2 - 135.89) < 10):
        print(f"Wire: ({x1}, {y1}) -> ({x2}, {y2})")
