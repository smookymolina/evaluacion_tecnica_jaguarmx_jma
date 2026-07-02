import re
from collections import defaultdict

sch_path = r"C:\Users\GIRTEC\Claude\Projects\Jaguar MX\kicad\PCB\PCB.kicad_sch"

with open(sch_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Find U1 coordinates and rotation
sym_match = re.search(r'\(symbol\s*\(lib_id\s*"Seeed_Studio_XIAO_Series:XIAO-RP2350-DIP".*?property\s*"Reference"\s*"U1".*?\)', content, re.DOTALL)
if not sym_match:
    # Try broader search
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
        if 'property "Reference" "U1"' in block:
            sym_match = m
            sym_block = block
            break
else:
    sym_block = sym_match.group(0)

at_m = re.search(r'\(at\s+([\d.-]+)\s+([\d.-]+)\s*([\d.-]*)', sym_block)
x = float(at_m.group(1))
y = float(at_m.group(2))
rot = float(at_m.group(3)) if at_m.group(3) else 0.0

# Print U1 position
print(f"U1 is at ({x}, {y}) rot={rot}")

# Parse wires
wires = re.findall(r'\(wire\s*\(pts\s*\(xy\s+([\d.-]+)\s+([\d.-]+)\)\s*\(xy\s+([\d.-]+)\s+([\d.-]+)\)\s*\)', content)
graph = defaultdict(list)
def snap(coord):
    return (round(float(coord[0]), 2), round(float(coord[1]), 2))

for w in wires:
    n1 = snap((w[0], w[1]))
    n2 = snap((w[2], w[3]))
    graph[n1].append(n2)
    graph[n2].append(n1)

# Check labels
labels = re.findall(r'\((label|global_label|hierarchical_label)\s+"([^"]+)"\s*\(at\s+([\d.-]+)\s+([\d.-]+)\s*([\d.-]*)\)', content)

# U1 relative pin coordinates for Pin 13 and Pin 24:
# Pin 13: rel=(8.89, 19.05)
# Pin 24: rel=(-5.08, -21.59)
# Absolute coordinates:
p13_rel = (8.89, 19.05)
p24_rel = (-5.08, -21.59)

# Since rot = 0, no rotation, just translate
p13_abs = snap((x + p13_rel[0], y + p13_rel[1]))
p24_abs = snap((x + p24_rel[0], y + p24_rel[1]))

print(f"Pin 13 (GND) absolute coordinate: {p13_abs}")
print(f"Pin 24 (GND) absolute coordinate: {p24_abs}")

# Let's trace Pin 13
def trace(start_node):
    visited = set()
    stack = [start_node]
    visited.add(start_node)
    path = []
    
    while stack:
        node = stack.pop()
        for neighbor in graph[node]:
            if neighbor not in visited:
                visited.add(neighbor)
                path.append((node, neighbor))
                stack.append(neighbor)
    
    node_labels = []
    for ltype, name, lx, ly, lrot in labels:
        lcoord = snap((lx, ly))
        if lcoord in visited:
            node_labels.append((name, lcoord))
            
    return visited, path, node_labels

v13, p13, l13 = trace(p13_abs)
print(f"Trace Pin 13:")
print(f"  Visited nodes: {v13}")
print(f"  Labels: {l13}")

v24, p24, l24 = trace(p24_abs)
print(f"Trace Pin 24:")
print(f"  Visited nodes: {v24}")
print(f"  Labels: {l24}")
