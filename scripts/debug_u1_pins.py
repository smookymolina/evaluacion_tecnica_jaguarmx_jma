import re

sch_path = r"C:\Users\GIRTEC\Claude\Projects\Jaguar MX\kicad\PCB\PCB.kicad_sch"

with open(sch_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Let's search for U1 symbol block in content
match = re.search(r'\(symbol\s*\(lib_id\s*"Seeed_Studio_XIAO_Series:XIAO-RP2350-DIP".*?property\s*"Reference"\s*"U1".*?\)', content, re.DOTALL)
if not match:
    # try parenthesization matching
    matches = re.finditer(r'\(symbol\s*\(lib_id\s*"[^"]+"', content)
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
        if 'property "Reference" "U1"' in block:
            sym_block = block
            break
else:
    sym_block = match.group(0)

# Let's see what pins are in U1 block in the schematic
pins_in_block = re.findall(r'\(pin\s+"([^"]+)"\s+\(uuid\s+"([^"]+)"\)\)', sym_block)
print("Pins in U1 instance:")
for p, u in pins_in_block:
    print(f"  Pin {p} (uuid: {u})")
