import re

sch_path = r"C:\Users\GIRTEC\Claude\Projects\Jaguar MX\kicad\PCB\PCB.kicad_sch"

with open(sch_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Let's search for any wires, junctions, and labels that touch any U3 pin coordinates
# Let's get U3 pins coords first
pins = {
    "1": (73.66, 137.16),
    "2": (73.66, 137.16),
    "3": (60.96, 101.6),
    "4": (60.96, 101.6),
    "5": (73.66, 132.08),
    "6": (73.66, 132.08),
    "7": (73.66, 119.38),
    "8": (73.66, 119.38),
    "9": (66.04, 101.6),
    "10": (66.04, 101.6),
    "11": (73.66, 124.46),
    "12": (73.66, 124.46),
    "13": (63.5, 152.4),
    "14": (66.04, 152.4),
    "15": (43.18, 129.54),
    "16": (43.18, 116.84),
    "17": (43.18, 119.38),
    "18": (50.8, 101.6),
    "19": (43.18, 137.16),
    "20": (50.8, 152.4),
    "21": (43.18, 124.46),
    "22": (43.18, 121.92),
    "23": (43.18, 132.08),
    "24": (60.96, 152.4)
}

wires = re.findall(r'\(wire\s*\(pts\s*\(xy\s+([\d.-]+)\s+([\d.-]+)\)\s*\(xy\s+([\d.-]+)\s+([\d.-]+)\)\s*\)', content)

# Check junctions
junctions = re.findall(r'\(junction\s*\(at\s+([\d.-]+)\s+([\d.-]+)\)', content)

# Check labels
labels = re.findall(r'\((label|global_label|hierarchical_label)\s+"([^"]+)"\s*\(at\s+([\d.-]+)\s+([\d.-]+)\s*([\d.-]*)\)', content)

print("Check connections for each pin of U3:")
for pnum, (px, py) in sorted(pins.items(), key=lambda x: int(x[0])):
    connected_wires = []
    for pt1_x, pt1_y, pt2_x, pt2_y in wires:
        p1 = (round(float(pt1_x), 2), round(float(pt1_y), 2))
        p2 = (round(float(pt2_x), 2), round(float(pt2_y), 2))
        if p1 == (px, py) or p2 == (px, py):
            connected_wires.append(f"Wire {p1} -> {p2}")
            
    connected_labels = []
    for ltype, name, lx, ly, lrot in labels:
        lcoord = (round(float(lx), 2), round(float(ly), 2))
        if lcoord == (px, py):
            connected_labels.append(f"Label {name} at {lcoord}")
            
    connected_junctions = []
    for jx, jy in junctions:
        jcoord = (round(float(jx), 2), round(float(jy), 2))
        if jcoord == (px, py):
            connected_junctions.append(f"Junction at {jcoord}")
            
    if connected_wires or connected_labels or connected_junctions:
        print(f"Pin {pnum} (coord {px}, {py}):")
        for cw in connected_wires:
            print(f"  {cw}")
        for cl in connected_labels:
            print(f"  {cl}")
        for cj in connected_junctions:
            print(f"  {cj}")
    else:
        print(f"Pin {pnum} (coord {px}, {py}): Disconnected")
