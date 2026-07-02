import re

sch_path = r"C:\Users\GIRTEC\Claude\Projects\Jaguar MX\kicad\PCB\PCB.kicad_sch"

with open(sch_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Let's run a modified version of the netlist extractor that prints details of the AGND net containing LED1 or J1
# Let's see what coordinates are associated with these pins in the script
# We can just copy the core part of extract_netlist_regex.py and print details.

import math
from collections import defaultdict

# 1. Parse lib_symbols
lib_symbols = {}
start_idx = content.find('(lib_symbols')
lib_symbols_block = content[start_idx:] if start_idx != -1 else ""

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

# Parse placed symbols
content_no_lib = content.replace(lib_symbols_block, "") if lib_symbols_block else content
placed_symbols = []
inst_matches = re.finditer(r'\(symbol\s*\(lib_id\s*\"([^\"]+)\"', content_no_lib)
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
    
    ref = ref_m.group(1) if ref_m else "Unknown"
    val = val_m.group(1) if val_m else "Unknown"
    x = float(at_m.group(1)) if at_m else 0.0
    y = float(at_m.group(2)) if at_m else 0.0
    rot = float(at_m.group(3)) if at_m and at_m.group(3) else 0.0
    
    placed_symbols.append({
        'lib_id': lib_id,
        'ref': ref,
        'val': val,
        'at_x': x,
        'at_y': y,
        'at_rot': rot
    })

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

# Check coordinates of J1 and LED1 pins
for sym in placed_symbols:
    if sym['ref'] in ["J1", "LED1"]:
        lib_id = sym['lib_id']
        pins = lib_symbols.get(lib_id, [])
        print(f"Component {sym['ref']} at ({sym['at_x']}, {sym['at_y']}):")
        for pnum, pname, px, py, prot in pins:
            abs_x, abs_y = get_absolute_pin_coords(sym['at_x'], sym['at_y'], sym['at_rot'], px, py)
            print(f"  Pin {pnum} ({pname}): rel=({px}, {py}) -> abs=({abs_x}, {abs_y}) snapped=({round(abs_x, 2)}, {round(abs_y, 2)})")

# Print what targets are at coordinates near J1 and LED1
print("\nTargets in connectivity_map for J1 and LED1:")
for coord, targets in connectivity_map.items():
    for t in targets:
        if t[1] in ["J1", "LED1"]:
            print(f"  Coord {coord} -> {targets}")
            break
