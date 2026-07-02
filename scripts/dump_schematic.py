import re

sch_path = r"C:\Users\GIRTEC\Claude\Projects\Jaguar MX\kicad\PCB\PCB.kicad_sch"

with open(sch_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Let's find all global_label, label, hierarchical_label in the schematic
labels = re.findall(r'\((global_label|label|hierarchical_label)\s+"([^"]+)"\s+\(at\s+([\d.-]+)\s+([\d.-]+)', content)
print(f"Total labels found: {len(labels)}")
# Group labels by name and print them
labels_by_name = {}
for ltype, name, x, y in labels:
    labels_by_name.setdefault(name, []).append((ltype, x, y))

for name in sorted(labels_by_name.keys()):
    locs = ", ".join([f"{ltype}({x}, {y})" for ltype, x, y in labels_by_name[name]])
    print(f"Label: {name} -> {locs}")

print("\n" + "="*40 + "\n")

# Let's find all placed symbols and their references and coordinates
# Placed symbol instance looks like:
# (symbol (lib_id "...") (at X Y R) ... (property "Reference" "REF" ...) ... )
# Let's extract symbol reference and coordinates

# Let's first remove the lib_symbols block to avoid parsing library definitions
start_idx = content.find('(lib_symbols')
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
    content_no_lib = content[:start_idx] + content[end_idx:]
else:
    content_no_lib = content

# Parse symbol instances in content_no_lib
# Each symbol instance starts with (symbol (lib_id ...)
symbol_matches = re.finditer(r'\(symbol\s+\(lib_id', content_no_lib)

instances = []
for match in symbol_matches:
    start_idx = match.start()
    paren_count = 0
    end_idx = start_idx
    for i in range(start_idx, len(content_no_lib)):
        if content_no_lib[i] == '(':
            paren_count += 1
        elif content_no_lib[i] == ')':
            paren_count -= 1
            if paren_count == 0:
                end_idx = i + 1
                break
    sym_block = content_no_lib[start_idx:end_idx]
    
    ref_m = re.search(r'\(property\s+"Reference"\s+"([^"]+)"', sym_block)
    val_m = re.search(r'\(property\s+"Value"\s+"([^"]+)"', sym_block)
    at_m = re.search(r'\(at\s+([\d.-]+)\s+([\d.-]+)\s*([\d.-]*)', sym_block)
    unit_m = re.search(r'\(unit\s+(\d+)\)', sym_block)
    
    ref = ref_m.group(1) if ref_m else "Unknown"
    val = val_m.group(1) if val_m else "Unknown"
    x = at_m.group(1) if at_m else "0"
    y = at_m.group(2) if at_m else "0"
    rot = at_m.group(3) if at_m and at_m.group(3) else "0"
    unit = unit_m.group(1) if unit_m else "1"
    
    instances.append((ref, val, x, y, rot, unit))

instances.sort(key=lambda x: (x[0], int(x[5])))
print(f"Total symbol instances: {len(instances)}")
for ref, val, x, y, rot, unit in instances:
    print(f"Instance: {ref} (Val: {val}) at ({x}, {y}), rot={rot}, unit={unit}")
