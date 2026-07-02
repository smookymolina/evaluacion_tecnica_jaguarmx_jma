import re
from collections import defaultdict

sch_path = r"C:\Users\GIRTEC\Claude\Projects\Jaguar MX\kicad\PCB\PCB.kicad_sch"

with open(sch_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Let's find all wires
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
    
    # find labels in visited
    node_labels = []
    for ltype, name, lx, ly, lrot in labels:
        lcoord = snap((lx, ly))
        if lcoord in visited:
            node_labels.append((name, lcoord))
            
    return visited, path, node_labels

print("Trace U3.Pin18 (GND) (50.8, 101.6):")
v18, p18, l18 = trace((50.8, 101.6))
print(f"  Visited nodes: {v18}")
print(f"  Labels: {l18}")

print("\nTrace U3.Pin20 (VCC) (50.8, 152.4):")
v20, p20, l20 = trace((50.8, 152.4))
print(f"  Visited nodes: {v20}")
print(f"  Labels: {l20}")
