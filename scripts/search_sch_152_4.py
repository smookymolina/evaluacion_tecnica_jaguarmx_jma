import re

sch_path = r"C:\Users\GIRTEC\Claude\Projects\Jaguar MX\kicad\PCB\PCB.kicad_sch"

with open(sch_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Let's search for "152.4" in wires
wires_152_4 = re.findall(r'\(wire\s*\(pts\s*\(xy\s+[\d.-]+\s+152\.4\)\s*\(xy\s+[\d.-]+\s+[\d.-]+\)\s*\)', content)
wires_152_4_end = re.findall(r'\(wire\s*\(pts\s*\(xy\s+[\d.-]+\s+[\d.-]+\)\s*\(xy\s+[\d.-]+\s+152\.4\)\s*\)', content)

print("Wires with Y=152.4:")
for w in wires_152_4:
    print(w)
for w in wires_152_4_end:
    print(w)

print("\nAll wires in schematic:")
all_wires = re.findall(r'\(wire\s*\(pts\s*\(xy\s+([\d.-]+)\s+([\d.-]+)\)\s*\(xy\s+([\d.-]+)\s+([\d.-]+)\)\s*\)', content)
for w in all_wires:
    p1 = (float(w[0]), float(w[1]))
    p2 = (float(w[2]), float(w[3]))
    if 150 <= p1[1] <= 155 or 150 <= p2[1] <= 155:
        print(f"Wire near Y=152.4: {p1} -> {p2}")
