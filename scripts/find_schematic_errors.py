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

if lib_symbols_block:
    symbol_matches = re.finditer(r'\(symbol\s+"([^"]+)"', lib_symbols_block)
    for match in symbol_matches:
        sym_name = match.group(1)
        sym_start = match.start()
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
        
        base_name = re.sub(r'_\d+_\d+$', '', sym_name)
        lib_symbols.setdefault(base_name, []).extend(pins)
        seen_nums = set()
        unique_pins = []
        for p in lib_symbols[base_name]:
            if p[0] not in seen_nums:
                unique_pins.append(p)
                seen_nums.add(p[0])
        lib_symbols[base_name] = unique_pins

# Remove lib_symbols from content
content_no_lib = content.replace(lib_symbols_block, "") if lib_symbols_block else content

# Parse placed symbols
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

def get_absolute_pin_coords(sym_x, sym_y, sym_rot, pin_rel_x, pin_rel_y):
    rad = math.radians(sym_rot)
    cos_t = math.cos(rad)
    sin_t = math.sin(rad)
    pin_rel_y = -pin_rel_y
    rx = pin_rel_x * cos_t - pin_rel_y * sin_t
    ry = pin_rel_x * sin_t + pin_rel_y * cos_t
    return round(sym_x + rx, 4), round(sym_y + ry, 4)

connectivity_map = {}
pin_to_coord = {}
coord_to_pins = defaultdict(list)

def add_connection(x, y, target):
    coord = (round(x, 2), round(y, 2))
    connectivity_map.setdefault(coord, []).append(target)
    if target[0] == 'PIN':
        ref, pnum, pname = target[1:]
        pin_to_coord[(ref, pnum)] = coord
        coord_to_pins[coord].append((ref, pnum, pname))

# Map pin coordinates
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

# Collect connection points
connection_points = set()
for coord in connectivity_map:
    connection_points.add(coord)
for jx, jy in junctions:
    connection_points.add((round(jx, 2), round(jy, 2)))
for pt1, pt2 in wires:
    connection_points.add((round(pt1[0], 2), round(pt1[1], 2)))
    connection_points.add((round(pt2[0], 2), round(pt2[1], 2)))

def is_point_on_segment(pt, seg_start, seg_end, tol=0.05):
    px, py = pt
    x1, y1 = seg_start
    x2, y2 = seg_end
    if not (min(x1, x2) - tol <= px <= max(x1, x2) + tol and min(y1, y2) - tol <= py <= max(y1, y2) + tol):
        return False
    line_len = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
    if line_len < 0.01:
        return math.sqrt((px - x1)**2 + (py - y1)**2) <= tol
    dist = abs((y2 - y1)*px - (x2 - x1)*py + x2*y1 - y2*x1) / line_len
    return dist <= tol

# Split wire segments
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

# Adjacency graph
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
        
        # We want to identify empty nets or isolated pins too
        nets.append({
            'nodes': net_nodes,
            'pins': net_pins,
            'labels': net_labels
        })

print("AUDIT REPORT:")
print("=" * 60)

# 1. Identify split networks (e.g. networks with the same label that are not connected)
label_to_nets = defaultdict(list)
for net in nets:
    for label in net['labels']:
        label_to_nets[label].append(net)

print("\n--- SPLIT NETWORKS ---")
has_splits = False
for label, net_list in sorted(label_to_nets.items()):
    if len(net_list) > 1:
        has_splits = True
        print(f"Net '{label}' is split into {len(net_list)} separate components:")
        for idx, net in enumerate(net_list):
            pins_in_net = [f"{ref}.{pnum}({pname})" for ref, pnum, pname in net['pins']]
            labels_in_net = [l for l in net['labels'] if l != label]
            print(f"  Component {idx+1}:")
            print(f"    Pins: {', '.join(sorted(pins_in_net)) if pins_in_net else 'No pins'}")
            if labels_in_net:
                print(f"    Other labels in this component: {', '.join(labels_in_net)}")
            # Show a sample coordinate
            if net['nodes']:
                print(f"    Location (sample): {net['nodes'][0]}")

if not has_splits:
    print("None found! All labeled networks are single continuous components.")

# 2. Identify completely disconnected/floating pins
print("\n--- FLOATING / DISCONNECTED PINS ---")
floating_pins = []
for sym in placed_symbols:
    ref = sym['ref']
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
            # check if this pin has any wires/labels/junctions connected
            coord = pin_to_coord.get((ref, pnum))
            if coord:
                # check if there are any neighbors in the graph
                neighbors = graph[coord]
                # check if there is a label at this exact coord
                has_label = False
                if coord in connectivity_map:
                    for target in connectivity_map[coord]:
                        if target[0] == 'LABEL':
                            has_label = True
                
                if len(neighbors) == 0 and not has_label:
                    floating_pins.append((ref, pnum, pname, coord))
            else:
                floating_pins.append((ref, pnum, pname, None))

if floating_pins:
    # Sort by RefDes
    def nat_key(x):
        return [int(t) if t.isdigit() else t.lower() for t in re.split(r'(\d+)', x[0])]
    floating_pins.sort(key=nat_key)
    for ref, pnum, pname, coord in floating_pins:
        # Ignore NC pins on some components if they are meant to be NC
        # Let's print all to see
        print(f"  {ref} Pin {pnum} ({pname}): Coords {coord}")
else:
    print("None found!")

# 3. Check for specific U4 (TC4420) and J9 (Selector_TC4420) connections
print("\n--- DETAILED INSPECTION OF U4 (TC4420) ---")
u4_pins = {pnum: [] for pnum in ['1', '2', '3', '4', '5', '6', '7', '8']}
for net in nets:
    for ref, pnum, pname in net['pins']:
        if ref == 'U4':
            u4_pins[pnum].append(net)

for pnum, net_list in sorted(u4_pins.items()):
    if not net_list:
        print(f"  Pin {pnum}: Completely disconnected (no net found)")
    else:
        for net in net_list:
            labels_str = ", ".join(net['labels']) if net['labels'] else "No label"
            other_pins = [f"{r}.{p}" for r, p, n in net['pins'] if not (r == 'U4' and p == pnum)]
            print(f"  Pin {pnum} (Net labels: {labels_str}): Connected to {', '.join(other_pins) if other_pins else 'nothing else'}")

print("\n--- DETAILED INSPECTION OF J9 ---")
j9_pins = {pnum: [] for pnum in ['1', '2', '3']}
for net in nets:
    for ref, pnum, pname in net['pins']:
        if ref == 'J9':
            j9_pins[pnum].append(net)

for pnum, net_list in sorted(j9_pins.items()):
    if not net_list:
        print(f"  Pin {pnum}: Completely disconnected (no net found)")
    else:
        for net in net_list:
            labels_str = ", ".join(net['labels']) if net['labels'] else "No label"
            other_pins = [f"{r}.{p}" for r, p, n in net['pins'] if not (r == 'J9' and p == pnum)]
            print(f"  Pin {pnum} (Net labels: {labels_str}): Connected to {', '.join(other_pins) if other_pins else 'nothing else'}")

print("\n--- DETAILED INSPECTION OF C15 ---")
c15_pins = {pnum: [] for pnum in ['1', '2']}
for net in nets:
    for ref, pnum, pname in net['pins']:
        if ref == 'C15':
            c15_pins[pnum].append(net)

for pnum, net_list in sorted(c15_pins.items()):
    if not net_list:
        print(f"  Pin {pnum}: Completely disconnected (no net found)")
    else:
        for net in net_list:
            labels_str = ", ".join(net['labels']) if net['labels'] else "No label"
            other_pins = [f"{r}.{p}" for r, p, n in net['pins'] if not (r == 'C15' and p == pnum)]
            print(f"  Pin {pnum} (Net labels: {labels_str}): Connected to {', '.join(other_pins) if other_pins else 'nothing else'}")
