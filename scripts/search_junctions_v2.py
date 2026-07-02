import re

sch_path = r"C:\Users\GIRTEC\Claude\Projects\Jaguar MX\kicad\PCB\PCB.kicad_sch"

with open(sch_path, 'r', encoding='utf-8') as f:
    content = f.read()

junctions = re.findall(r'\(junction\s+\(at\s+([\d.-]+)\s+([\d.-]+)\)', content)

print("Junctions in schematic:")
for idx, j in enumerate(junctions):
    print(f"Junction {idx+1}: at ({j[0]}, {j[1]})")
