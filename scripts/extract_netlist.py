import re
import sys

# Script to parse KiCad schematic (.kicad_sch) and extract the connectivity
sch_path = r"C:\Users\GIRTEC\Claude\Projects\Jaguar MX\kicad\PCB\PCB.kicad_sch"

with open(sch_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Parse lib_symbols
# Format of a library symbol:
# (symbol "Name" (pin type shape (at X Y R) ... (name "..." ...) (number "..." ...)))
# There can be sub-units inside symbol:
# (symbol "Name_1_1" (pin ...))
# Let's parse all pins for each lib_id.

# Let's find the lib_symbols block first
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

# Map from lib_id -> list of (pin_number, pin_name, rel_x, rel_y, rel_rot)
lib_symbols = {}

# Regular expression to find symbol definitions in lib_symbols
# (symbol "Lib:Name" ... (symbol "Lib:Name_0_1" ... (pin ...)) ... )
# Since KiCad v6+ has nested symbols (units), we can parse them by walking the S-expression.
# Let's write a simple parser for S-expressions or use regexes.
# To be robust, let's parse the S-expressions into python lists.

def parse_sexpr(text, start=0):
    tokens = []
    i = start
    n = len(text)
    
    # helper to skip whitespace
    def skip_ws(idx):
        while idx < n and text[idx].isspace():
            idx += 1
        return idx

    while i < n:
        i = skip_ws(i)
        if i >= n:
            break
        if text[i] == '(':
            sub, next_i = parse_sexpr(text, i + 1)
            tokens.append(sub)
            i = next_i
        elif text[i] == ')':
            return tokens, i + 1
        elif text[i] == '"':
            # quoted string
            start_q = i + 1
            i = start_q
            while i < n:
                if text[i] == '"' and text[i-1] != '\\':
                    break
                i += 1
            tokens.append(text[start_q:i])
            i += 1
        else:
            # unquoted string
            start_uq = i
            while i < n and not text[i].isspace() and text[i] not in '()':
                i += 1
            tokens.append(text[start_uq:i])
    return tokens, i

if lib_symbols_block:
    tokens, _ = parse_sexpr(lib_symbols_block)
    # The lib_symbols token is a list starting with 'lib_symbols'
    # Each sub-token is a symbol definition
    for sym_token in tokens[0][1:]:
        if isinstance(sym_token, list) and sym_token[0] == 'symbol':
            sym_name = sym_token[1]
            # It could be a base symbol or unit
            # Base symbol has pin definitions, or contains units which have pin definitions.
            # Let's collect all pins recursively
            pins = []
            def collect_pins(t):
                if not isinstance(t, list):
                    return
                if t[0] == 'pin':
                    # Extract pin details
                    # Format: (pin type shape (at X Y R) ... (name "..." ...) (number "..." ...))
                    ptype = t[1]
                    pshape = t[2]
                    px, py, prot = 0.0, 0.0, 0.0
                    pname = ""
                    pnum = ""
                    for item in t[3:]:
                        if isinstance(item, list):
                            if item[0] == 'at':
                                px = float(item[1])
                                py = float(item[2])
                                if len(item) > 3:
                                    prot = float(item[3])
                            elif item[0] == 'name':
                                pname = item[1]
                            elif item[0] == 'number':
                                pnum = item[1]
                    pins.append((pnum, pname, px, py, prot))
                else:
                    for sub in t:
                        collect_pins(sub)
            collect_pins(sym_token)
            
            # The name might be "Lib:Name" or "Lib:Name_1_1"
            # If it's a unit, we associate pins with the base name
            base_name = sym_name.split('_')[0]
            if base_name not in lib_symbols:
                lib_symbols[base_name] = []
            # Merge or overwrite pins
            # Only add if pin number doesn't exist yet, or update it
            existing_nums = {p[0] for p in lib_symbols[base_name]}
            for p in pins:
                if p[0] not in existing_nums:
                    lib_symbols[base_name].append(p)
                    existing_nums.add(p[0])
                else:
                    # update
                    lib_symbols[base_name] = [x if x[0] != p[0] else p for x in lib_symbols[base_name]]
                    
print(f"Parsed {len(lib_symbols)} library symbols.")

# Let's strip lib_symbols block from schematic content to parse instances and wires
sch_content_no_lib = content
if start_idx != -1:
    sch_content_no_lib = content[:start_idx] + content[end_idx:]

# Parse schematic instances
sch_tokens, _ = parse_sexpr("(" + sch_content_no_lib + ")")
sch_root = sch_tokens[0]

# List of placed symbols
placed_symbols = []
# List of wires: list of ((x1, y1), (x2, y2))
wires = []
# List of labels: list of (label_type, name, x, y)
labels = []
# List of junctions: list of (x, y)
junctions = []

for token in sch_root:
    if not isinstance(token, list):
        continue
    if token[0] == 'symbol':
        # Placed symbol
        lib_id = ""
        at_x, at_y, at_rot = 0.0, 0.0, 0.0
        ref = ""
        val = ""
        uuid = ""
        unit = 1
        for item in token[1:]:
            if not isinstance(item, list):
                continue
            if item[0] == 'lib_id':
                lib_id = item[1]
            elif item[0] == 'at':
                at_x = float(item[1])
                at_y = float(item[2])
                if len(item) > 3:
                    at_rot = float(item[3])
            elif item[0] == 'unit':
                unit = int(item[1])
            elif item[0] == 'uuid':
                uuid = item[1]
            elif item[0] == 'property':
                if item[1] == 'Reference':
                    ref = item[2]
                elif item[1] == 'Value':
                    val = item[2]
        placed_symbols.append({
            'lib_id': lib_id,
            'at_x': at_x,
            'at_y': at_y,
            'at_rot': at_rot,
            'unit': unit,
            'ref': ref,
            'val': val,
            'uuid': uuid
        })
    elif token[0] == 'wire':
        # Wire
        pts = []
        for item in token[1:]:
            if isinstance(item, list) and item[0] == 'pts':
                for pt in item[1:]:
                    if isinstance(pt, list) and pt[0] == 'xy':
                        pts.append((float(pt[1]), float(pt[2])))
        if len(pts) == 2:
            wires.append((pts[0], pts[1]))
    elif token[0] in ('label', 'global_label', 'hierarchical_label'):
        ltype = token[0]
        name = token[1]
        at_x, at_y = 0.0, 0.0
        for item in token[2:]:
            if isinstance(item, list) and item[0] == 'at':
                at_x = float(item[1])
                at_y = float(item[2])
        labels.append((ltype, name, at_x, at_y))
    elif token[0] == 'junction':
        at_x, at_y = 0.0, 0.0
        for item in token[1:]:
            if isinstance(item, list) and item[0] == 'at':
                at_x = float(item[1])
                at_y = float(item[2])
        junctions.append((at_x, at_y))

print(f"Parsed {len(placed_symbols)} placed symbols.")
print(f"Parsed {len(wires)} wires.")
print(f"Parsed {len(labels)} labels.")
print(f"Parsed {len(junctions)} junctions.")

# Function to rotate/translate relative pin coordinates to absolute coordinates
# KiCad rotations are clockwise in degrees (usually 0, 90, 180, 270)
# and coordinates are in mm.
import math
def get_absolute_pin_coords(sym_x, sym_y, sym_rot, pin_rel_x, pin_rel_y):
    # KiCad Y axis is pointing DOWN in schematic coordinates
    # Let's apply rotation
    rad = math.radians(sym_rot)
    # Standard rotation matrix (clockwise because Y is down)
    # X' = X * cos(theta) - Y * sin(theta)
    # Y' = X * sin(theta) + Y * cos(theta)
    cos_t = math.cos(rad)
    sin_t = math.sin(rad)
    
    # Note: relative pin coordinates are defined relative to the symbol origin (0,0)
    # Let's apply rotation to relative coordinates
    rx = pin_rel_x * cos_t - pin_rel_y * sin_t
    ry = pin_rel_x * sin_t + pin_rel_y * cos_t
    
    # Translate
    return round(sym_x + rx, 4), round(sym_y + ry, 4)

# Map from absolute coord (x, y) -> list of connected pins (e.g. ("U1", "Pin1", name)) or labels (e.g. ("Label", "+3V3"))
connectivity_map = {}

def add_connection(x, y, target):
    coord = (round(x, 2), round(y, 2))
    connectivity_map.setdefault(coord, []).append(target)

# Map all pins of placed symbols to absolute coordinates
for sym in placed_symbols:
    lib_id = sym['lib_id']
    # Check if we have this symbol in our lib_symbols map
    # lib_symbols is keyed by base name (without unit suffixes)
    base_lib_id = lib_id.split('_')[0]
    if base_lib_id in lib_symbols:
        pins = lib_symbols[base_lib_id]
        for pnum, pname, px, py, prot in pins:
            abs_x, abs_y = get_absolute_pin_coords(sym['at_x'], sym['at_y'], sym['at_rot'], px, py)
            add_connection(abs_x, abs_y, ('PIN', sym['ref'], pnum, pname))
    else:
        # Try finding by name without library prefix
        simple_name = base_lib_id.split(':')[-1] if ':' in base_lib_id else base_lib_id
        found = False
        for k in lib_symbols:
            if k.endswith(':' + simple_name) or k == simple_name:
                pins = lib_symbols[k]
                for pnum, pname, px, py, prot in pins:
                    abs_x, abs_y = get_absolute_pin_coords(sym['at_x'], sym['at_y'], sym['at_rot'], px, py)
                    add_connection(abs_x, abs_y, ('PIN', sym['ref'], pnum, pname))
                found = True
                break
        if not found:
            print(f"Warning: Symbol definition for {lib_id} ({sym['ref']}) not found in lib_symbols.")

# Add labels
for ltype, name, lx, ly in labels:
    add_connection(lx, ly, ('LABEL', name))

# Add wires
# Wires are lines from pt1 to pt2. They connect nodes together.
# Let's build a graph where nodes are absolute coordinates and edges are wires.
# We will find connected components (nets) in this graph.
from collections import defaultdict
graph = defaultdict(list)

# We snap coordinates to 2 decimal places to handle float precision issues
def snap(coord):
    return (round(coord[0], 2), round(coord[1], 2))

for pt1, pt2 in wires:
    node1 = snap(pt1)
    node2 = snap(pt2)
    graph[node1].append(node2)
    graph[node2].append(node1)

# Find all coordinates in the graph (i.e. all endpoints of wires)
all_coords = set(graph.keys())
# Add all pin coordinates to all_coords as well, in case they are endpoints of wires or lie on wires
# (Wait, if a pin coordinate is not an exact endpoint of a wire, but lies on a horizontal/vertical wire,
# does it connect? Yes! In KiCad, wires are usually segment-by-segment, so they end exactly on pins.
# But just in case, we'll SNAP all pin coordinates and label coordinates)
for coord in connectivity_map:
    all_coords.add(coord)

# Let's find connected components (nets) using DFS
visited = set()
nets = []

for coord in all_coords:
    if coord not in visited:
        # Start a new net
        net_nodes = []
        stack = [coord]
        while stack:
            node = stack.pop()
            if node not in visited:
                visited.add(node)
                net_nodes.append(node)
                # Traverse neighbors
                for neighbor in graph[node]:
                    if neighbor not in visited:
                        stack.append(neighbor)
        
        # We have the nodes in this net. Let's find what pins and labels are in this net.
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

# Let's output all nets!
print(f"\n--- Extracted Netlist ({len(nets)} nets found) ---")
for idx, net in enumerate(nets):
    name = "UNNAMED_" + str(idx)
    if net['labels']:
        # If there are labels, use the first label as the net name (or list all labels)
        name = "/".join(set(net['labels']))
    
    pin_strs = [f"{ref}.{pnum}({pname})" for ref, pnum, pname in net['pins']]
    print(f"Net {name}:")
    print(f"  Pins: {', '.join(pin_strs)}")
    if net['labels']:
        print(f"  Labels: {', '.join(net['labels'])}")
