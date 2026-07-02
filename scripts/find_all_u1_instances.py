import re

sch_path = r"C:\Users\GIRTEC\Claude\Projects\Jaguar MX\kicad\PCB\PCB.kicad_sch"

with open(sch_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Find all symbol instances of U1
symbol_matches = re.finditer(r'\(symbol\s*\(lib_id\s*"[^"]+"', content)
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
    block = content[start_idx:end_idx]
    if 'property "Reference" "U1"' in block:
        at_m = re.search(r'\(at\s+([\d.-]+)\s+([\d.-]+)\s*([\d.-]*)', block)
        unit_m = re.search(r'\(unit\s+(\d+)\)', block)
        lib_id_m = re.search(r'\(lib_id\s*"([^"]+)"', block)
        
        lib_id = lib_id_m.group(1) if lib_id_m else ""
        x = at_m.group(1) if at_m else ""
        y = at_m.group(2) if at_m else ""
        rot = at_m.group(3) if at_m and at_m.group(3) else "0"
        unit = unit_m.group(1) if unit_m else "1"
        
        print(f"U1 Unit {unit} ({lib_id}) at ({x}, {y}) rot={rot}")
