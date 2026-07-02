import re
from collections import defaultdict

sch_path = r"C:\Users\GIRTEC\Claude\Projects\Jaguar MX\kicad\PCB\PCB.kicad_sch"

with open(sch_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Let's parse all wires
wires = []
wire_matches = re.findall(r'\(wire\s*\(pts\s*\(xy\s+([\d.-]+)\s+([\d.-]+)\)\s*\(xy\s+([\d.-]+)\s+([\d.-]+)\)\s*\)', content)
for w in wire_matches:
    wires.append(((float(w[0]), float(w[1])), (float(w[2]), float(w[3]))))

# Snap function
def snap(coord):
    return (round(coord[0], 2), round(coord[1], 2))

# Build graph
graph = defaultdict(list)
for pt1, pt2 in wires:
    node1 = snap(pt1)
    node2 = snap(pt2)
    graph[node1].append(node2)
    graph[node2].append(node1)

# We want to find the path from U3.18 coordinate (50.8, 101.6) to any of the +3V3 components, e.g. R5.1 or R1.1
# Let's find coordinates of R5.1, R1.1, etc.
# R5 is at (57.15, 77.47). R5.1 is at (57.15, 77.47 - something) or similar.
# Let's just find the connected component of (50.8, 101.6) in the wire graph
visited = set()
stack = [(50.8, 101.6)]
visited.add((50.8, 101.6))
path_edges = []

while stack:
    node = stack.pop()
    for neighbor in graph[node]:
        if neighbor not in visited:
            visited.add(neighbor)
            path_edges.append((node, neighbor))
            stack.append(neighbor)

print(f"Connected coordinates from (50.8, 101.6) ({len(visited)} nodes):")
for node in sorted(list(visited)):
    print(f"  {node}")

print("\nWires in this connected component:")
for n1, n2 in path_edges:
    print(f"  {n1} -> {n2}")
