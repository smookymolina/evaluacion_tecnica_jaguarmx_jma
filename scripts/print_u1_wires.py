import re

sch_path = r"C:\Users\GIRTEC\Claude\Projects\Jaguar MX\kicad\PCB\PCB.kicad_sch"

with open(sch_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Wires
wires = re.findall(r'\(wire\s*\(pts\s*\(xy\s+([\d.-]+)\s+([\d.-]+)\)\s*\(xy\s+([\d.-]+)\s+([\d.-]+)\)\s*\)', content)

print("Wires in schematic:")
for w in wires:
    p1 = (float(w[0]), float(w[1]))
    p2 = (float(w[2]), float(w[3]))
    # check if within U1 range
    # U1 is at (152.4, 105.41)
    if (120 <= p1[0] <= 180 and 50 <= p1[1] <= 150) or (120 <= p2[0] <= 180 and 50 <= p2[1] <= 150):
        print(f"Wire: {p1} -> {p2}")

print("\nLabels in schematic:")
labels = re.findall(r'\((label|global_label|hierarchical_label)\s+"([^"]+)"\s*\(at\s+([\d.-]+)\s+([\d.-]+)\s*([\d.-]*)\)', content)
for ltype, name, lx, ly, lrot in labels:
    print(f"Label: {name} ({ltype}) at ({lx}, {ly})")
