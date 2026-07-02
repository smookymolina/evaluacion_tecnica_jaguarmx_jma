import re

sch_path = r"C:\Users\GIRTEC\Claude\Projects\Jaguar MX\kicad\PCB\PCB.kicad_sch"

with open(sch_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Let's print all wires in the schematic and check their coordinates
wires = re.findall(r'\(wire\s*\(pts\s*\(xy\s+([\d.-]+)\s+([\d.-]+)\)\s*\(xy\s+([\d.-]+)\s+([\d.-]+)\)\s*\)', content)

print("Wires close to U1 Pin 13 (161.29, 124.46):")
for w in wires:
    p1 = (float(w[0]), float(w[1]))
    p2 = (float(w[2]), float(w[3]))
    if abs(p1[0] - 161.29) < 5 and abs(p1[1] - 124.46) < 5:
        print(f"Wire: {p1} -> {p2}")
    elif abs(p2[0] - 161.29) < 5 and abs(p2[1] - 124.46) < 5:
        print(f"Wire: {p1} -> {p2}")

print("\nWires close to U1 Pin 24 (147.32, 83.82):")
for w in wires:
    p1 = (float(w[0]), float(w[1]))
    p2 = (float(w[2]), float(w[3]))
    if abs(p1[0] - 147.32) < 5 and abs(p1[1] - 83.82) < 5:
        print(f"Wire: {p1} -> {p2}")
    elif abs(p2[0] - 147.32) < 5 and abs(p2[1] - 83.82) < 5:
        print(f"Wire: {p1} -> {p2}")
