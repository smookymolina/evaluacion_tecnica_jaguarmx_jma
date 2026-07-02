import re
import math

sch_path = r"C:\Users\GIRTEC\Claude\Projects\Jaguar MX\kicad\PCB\PCB.kicad_sch"

with open(sch_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Let's find U3 instance block
u3_match = re.search(r'\(symbol\s*\(lib_id\s*"Driver_Motor:TB6612FNG".*?property\s*"Reference"\s*"U3".*?\)', content, re.DOTALL)
if u3_match:
    print("Found U3:")
    print(u3_match.group(0))
else:
    # let's look for U3 reference in a wider block
    matches = re.finditer(r'\(symbol\s*\(lib_id\s*"[^"]+"', content)
    for m in matches:
        start_idx = m.start()
        p_count = 0
        end_idx = start_idx
        for i in range(start_idx, len(content)):
            if content[i] == '(':
                p_count += 1
            elif content[i] == ')':
                p_count -= 1
                if p_count == 0:
                    end_idx = i + 1
                    break
        block = content[start_idx:end_idx]
        if 'property "Reference" "U3"' in block:
            print("Found U3 block:")
            print(block)
            break

print("\n" + "="*40 + "\n")

# Let's find all labels and wires within X: [30, 90], Y: [100, 160]
print("Wires and labels near U3:")
wires = re.findall(r'\(wire\s*\(pts\s*\(xy\s+([\d.-]+)\s+([\d.-]+)\)\s*\(xy\s+([\d.-]+)\s+([\d.-]+)\)\s*\)', content)
for pt1_x, pt1_y, pt2_x, pt2_y in wires:
    p1x, p1y, p2x, p2y = float(pt1_x), float(pt1_y), float(pt2_x), float(pt2_y)
    if (30 <= p1x <= 90 and 100 <= p1y <= 160) or (30 <= p2x <= 90 and 100 <= p2y <= 160):
        print(f"Wire: ({p1x}, {p1y}) -> ({p2x}, {p2y})")

labels = re.findall(r'\((label|global_label|hierarchical_label)\s+"([^"]+)"\s*\(at\s+([\d.-]+)\s+([\d.-]+)\s*([\d.-]*)\)', content)
for ltype, name, lx, ly, lrot in labels:
    lx, ly = float(lx), float(ly)
    if 30 <= lx <= 90 and 100 <= ly <= 160:
        print(f"Label: {name} ({ltype}) at ({lx}, {ly})")
