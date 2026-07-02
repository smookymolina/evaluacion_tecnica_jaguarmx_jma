import re

sch_path = r"C:\Users\GIRTEC\Claude\Projects\Jaguar MX\kicad\PCB\PCB.kicad_sch"

with open(sch_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Find all symbol instances in content
matches = list(re.finditer(r'\(symbol\s*\(lib_id\s*"[^"]+"', content))

for ref in ["U1", "U2", "U3", "U4", "J1", "J2", "LED1", "SW1", "C12", "C13", "C14"]:
    found = False
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
        if f'property "Reference" "{ref}"' in block:
            at_m = re.search(r'\(at\s+([\d.-]+)\s+([\d.-]+)\s*([\d.-]*)', block)
            print(f"Placed Symbol: {ref} at ({at_m.group(1)}, {at_m.group(2)})")
            found = True
            break
    if not found:
        print(f"Symbol {ref} not found.")
