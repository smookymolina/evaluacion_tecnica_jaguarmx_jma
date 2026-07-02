import re
import math
from collections import defaultdict

sch_path = r"C:\Users\GIRTEC\Claude\Projects\Jaguar MX\kicad\PCB\PCB.kicad_sch"

with open(sch_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Parse lib_symbols
lib_symbols = {}
start_idx = content.find('(lib_symbols')
lib_symbols_block = ""
if start_idx != -1:
    paren_count = 0
    end_idx = start_idx
    for i in range(start_idx, len(content)):
        if content[i] == '(':
            paren_count += 1
        elif content[i] == ')':
            paren_count -= 1
            if paren_count == 0:
                end_idx = i + 1
                break
    lib_symbols_block = content[start_idx:end_idx]

# Parse pins inside each symbol in lib_symbols
if lib_symbols_block:
    symbol_matches = re.finditer(r'\(symbol\s+"([^"]+)"', lib_symbols_block)
    for match in symbol_matches:
        sym_name = match.group(1)
        sym_start = match.start()
        # Find matching paren
        p_count = 0
        sym_end = sym_start
        for i in range(sym_start, len(lib_symbols_block)):
            if lib_symbols_block[i] == '(':
                p_count += 1
            elif lib_symbols_block[i] == ')':
                p_count -= 1
                if p_count == 0:
                    sym_end = i + 1
                    break
        sym_body = lib_symbols_block[sym_start:sym_end]
        
        # Find all pins in this symbol
        pins = []
        pin_matches = re.finditer(r'\(pin\s+\S+\s+\S+\s*\(at\s+([\d.-]+)\s+([\d.-]+)\s*([\d.-]*)\)', sym_body)
        for pm in pin_matches:
            px = float(pm.group(1))
            py = float(pm.group(2))
            prot = float(pm.group(3)) if pm.group(3) else 0.0
            
            pin_start = pm.start()
            pc = 0
            pin_end = pin_start
            for i in range(pin_start, len(sym_body)):
                if sym_body[i] == '(':
                    pc += 1
                elif sym_body[i] == ')':
                    pc -= 1
                    if pc == 0:
                        pin_end = i + 1
                        break
            pin_body = sym_body[pin_start:pin_end]
            
            pname_m = re.search(r'\(name\s+"([^"]*)"', pin_body)
            pnum_m = re.search(r'\(number\s+"([^"]+)"', pin_body)
            
            pname = pname_m.group(1) if pname_m else ""
            pnum = pnum_m.group(1) if pnum_m else ""
            pins.append((pnum, pname, px, py, prot))
        
        # Strip unit suffix e.g. _1_1 or _0_1 or _0_0
        base_name = re.sub(r'_\d+_\d+$', '', sym_name)
        lib_symbols.setdefault(base_name, []).extend(pins)
        # Remove duplicate pins by pin number
        seen_nums = set()
        unique_pins = []
        for p in lib_symbols[base_name]:
            if p[0] not in seen_nums:
                unique_pins.append(p)
                seen_nums.add(p[0])
        lib_symbols[base_name] = unique_pins

print(f"Parsed {len(lib_symbols)} library symbols.")

# Now remove lib_symbols block from content to parse instances
if lib_symbols_block:
    content_no_lib = content.replace(lib_symbols_block, "")
else:
    content_no_lib = content

placed_symbols = []
inst_matches = re.finditer(r'\(symbol\s*\(lib_id\s+"([^"]+)"', content_no_lib)
for match in inst_matches:
    start_idx = match.start()
    p_count = 0
    end_idx = start_idx
    for i in range(start_idx, len(content_no_lib)):
        if content_no_lib[i] == '(':
            p_count += 1
        elif content_no_lib[i] == ')':
            p_count -= 1
            if p_count == 0:
                end_idx = i + 1
                break
    sym_block = content_no_lib[start_idx:end_idx]
    
    lib_id = match.group(1)
    at_m = re.search(r'\(at\s+([\d.-]+)\s+([\d.-]+)\s*([\d.-]*)', sym_block)
    ref_m = re.search(r'\(property\s+"Reference"\s+"([^"]+)"', sym_block)
    val_m = re.search(r'\(property\s+"Value"\s+"([^"]+)"', sym_block)
    uuid_m = re.search(r'\(uuid\s+"([^"]+)"', sym_block)
    
    ref = ref_m.group(1) if ref_m else "Unknown"
    val = val_m.group(1) if val_m else "Unknown"
    uuid = uuid_m.group(1) if uuid_m else ""
    x = float(at_m.group(1)) if at_m else 0.0
    y = float(at_m.group(2)) if at_m else 0.0
    rot = float(at_m.group(3)) if at_m and at_m.group(3) else 0.0
    
    placed_symbols.append({
        'lib_id': lib_id,
        'ref': ref,
        'val': val,
        'at_x': x,
        'at_y': y,
        'at_rot': rot,
        'uuid': uuid
    })

# Parse wires
wires = []
wire_matches = re.findall(r'\(wire\s*\(pts\s*\(xy\s+([\d.-]+)\s+([\d.-]+)\)\s*\(xy\s+([\d.-]+)\s+([\d.-]+)\)\s*\)', content_no_lib)
for w in wire_matches:
    wires.append(((float(w[0]), float(w[1])), (float(w[2]), float(w[3]))))

# Parse labels
labels = []
label_matches = re.findall(r'\((label|global_label|hierarchical_label)\s+"([^"]+)"\s*\(at\s+([\d.-]+)\s+([\d.-]+)\s*([\d.-]*)\)', content_no_lib)
for ltype, name, lx, ly, lrot in label_matches:
    labels.append((ltype, name, float(lx), float(ly)))

# Parse junctions
junctions = []
junc_matches = re.findall(r'\(junction\s*\(at\s+([\d.-]+)\s+([\d.-]+)\)', content_no_lib)
for jx, jy in junc_matches:
    junctions.append((float(jx), float(jy)))

print(f"Parsed {len(placed_symbols)} placed symbols.")
print(f"Parsed {len(wires)} wires.")
print(f"Parsed {len(labels)} labels.")
print(f"Parsed {len(junctions)} junctions.")

def get_absolute_pin_coords(sym_x, sym_y, sym_rot, pin_rel_x, pin_rel_y):
    rad = math.radians(sym_rot)
    cos_t = math.cos(rad)
    sin_t = math.sin(rad)
    pin_rel_y = -pin_rel_y
    rx = pin_rel_x * cos_t - pin_rel_y * sin_t
    ry = pin_rel_x * sin_t + pin_rel_y * cos_t
    return round(sym_x + rx, 4), round(sym_y + ry, 4)

connectivity_map = {}
def add_connection(x, y, target):
    coord = (round(x, 2), round(y, 2))
    connectivity_map.setdefault(coord, []).append(target)

for sym in placed_symbols:
    lib_id = sym['lib_id']
    pins = None
    if lib_id in lib_symbols:
        pins = lib_symbols[lib_id]
    else:
        for k in lib_symbols:
            if k.lower() == lib_id.lower() or k.split(':')[-1].lower() == lib_id.lower():
                pins = lib_symbols[k]
                break
    
    if pins:
        for pnum, pname, px, py, prot in pins:
            abs_x, abs_y = get_absolute_pin_coords(sym['at_x'], sym['at_y'], sym['at_rot'], px, py)
            add_connection(abs_x, abs_y, ('PIN', sym['ref'], pnum, pname))

# Add labels
for ltype, name, lx, ly in labels:
    add_connection(lx, ly, ('LABEL', name))

# Helper to check if a point lies on a segment
def is_point_on_segment(pt, seg_start, seg_end, tol=0.05):
    px, py = pt
    x1, y1 = seg_start
    x2, y2 = seg_end
    
    # Check bounding box first
    if not (min(x1, x2) - tol <= px <= max(x1, x2) + tol and min(y1, y2) - tol <= py <= max(y1, y2) + tol):
        return False
        
    # Check distance to line
    line_len = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
    if line_len < 0.01:
        return math.sqrt((px - x1)**2 + (py - y1)**2) <= tol
        
    dist = abs((y2 - y1)*px - (x2 - x1)*py + x2*y1 - y2*x1) / line_len
    return dist <= tol

# Collect all potential connection points (junctions, pin locations, label locations, endpoints of wires)
connection_points = set()
for coord in connectivity_map:
    connection_points.add(coord)
for jx, jy in junctions:
    connection_points.add((round(jx, 2), round(jy, 2)))
for pt1, pt2 in wires:
    connection_points.add((round(pt1[0], 2), round(pt1[1], 2)))
    connection_points.add((round(pt2[0], 2), round(pt2[1], 2)))

# Split wire segments at any connection points that lie on them
split_wires = []
for pt1, pt2 in wires:
    pts_on_seg = []
    p1 = (round(pt1[0], 2), round(pt1[1], 2))
    p2 = (round(pt2[0], 2), round(pt2[1], 2))
    
    for cp in connection_points:
        if cp != p1 and cp != p2:
            if is_point_on_segment(cp, p1, p2):
                pts_on_seg.append(cp)
                
    if pts_on_seg:
        pts_on_seg.sort(key=lambda p: (p[0] - p1[0])**2 + (p[1] - p1[1])**2)
        curr = p1
        for pt in pts_on_seg:
            split_wires.append((curr, pt))
            curr = pt
        split_wires.append((curr, p2))
    else:
        split_wires.append((p1, p2))

# Build adjacency graph
graph = defaultdict(list)
for node1, node2 in split_wires:
    graph[node1].append(node2)
    graph[node2].append(node1)

# Find connected components (nets)
visited = set()
nets = []
all_coords = set(graph.keys())
for coord in connectivity_map:
    all_coords.add(coord)

for coord in all_coords:
    if coord not in visited:
        net_nodes = []
        stack = [coord]
        while stack:
            node = stack.pop()
            if node not in visited:
                visited.add(node)
                net_nodes.append(node)
                for neighbor in graph[node]:
                    if neighbor not in visited:
                        stack.append(neighbor)
        
        net_pins = []
        net_labels = []
        for node in net_nodes:
            if node in connectivity_map:
                for target in connectivity_map[node]:
                    if target[0] == 'PIN':
                        net_pins.append(target[1:])
                    elif target[0] == 'LABEL':
                        net_labels.append(target[1])
        
        if net_pins or net_labels:
            nets.append({
                'nodes': net_nodes,
                'pins': net_pins,
                'labels': net_labels
            })

print(f"\n--- Extracted Netlist ({len(nets)} nets found) ---")
labeled_nets = []
unlabeled_nets = []
for idx, net in enumerate(nets):
    if net['labels']:
        name = "/".join(sorted(list(set(net['labels']))))
        labeled_nets.append((name, net))
    else:
        name = f"UNNAMED_at_{net['nodes'][0][0]}_{net['nodes'][0][1]}"
        unlabeled_nets.append((name, net))

labeled_nets.sort(key=lambda x: x[0])
unlabeled_nets.sort(key=lambda x: x[0])

for name, net in labeled_nets + unlabeled_nets:
    pin_strs = [f"{ref}.{pnum}({pname})" for ref, pnum, pname in net['pins']]
    print(f"Net {name}:")
    print(f"  Pins: {', '.join(sorted(pin_strs))}")
