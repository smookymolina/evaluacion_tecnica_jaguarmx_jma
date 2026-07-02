import re

sch_path = r"C:\Users\GIRTEC\Claude\Projects\Jaguar MX\kicad\PCB\PCB.kicad_sch"

with open(sch_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Let's find all symbols placed in the schematic and check their coordinates
# format: (symbol (lib_id ...) (at X Y R) ... (property "Reference" ...))
# We will print any symbols within X: [120, 180], Y: [70, 160]

symbol_matches = re.finditer(r'\(symbol\s*\(lib_id\s*"([^"]+)"', content)
for match in symbol_matches:
    start_idx = match.start()
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
    sym_block = content[start_idx:end_idx]
    
    at_m = re.search(r'\(at\s+([\d.-]+)\s+([\d.-]+)\s*([\d.-]*)', sym_block)
    ref_m = re.search(r'\(property\s+"Reference"\s+"([^"]+)"', sym_block)
    val_m = re.search(r'\(property\s+"Value"\s+"([^"]+)"', sym_block)
    unit_m = re.search(r'\(unit\s+(\d+)\)', sym_block)
    
    if at_m and ref_m:
        x = float(at_m.group(1))
        y = float(at_m.group(2))
        ref = ref_m.group(1)
        val = val_m.group(1) if val_m else ""
        unit = unit_m.group(1) if unit_m else "1"
        if 120 <= x <= 180 and 70 <= y <= 160:
            print(f"Placed Symbol: {ref} ({val}), unit={unit} at ({x}, {y})")
