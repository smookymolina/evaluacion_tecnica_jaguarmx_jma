import re

sch_path = r"C:\Users\GIRTEC\Claude\Projects\Jaguar MX\kicad\PCB\PCB.kicad_sch"

with open(sch_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Let's find all symbols in lib_symbols block that contain "XIAO"
lib_symbols_match = re.search(r'\(lib_symbols(.*?)\n\t\)', content, re.DOTALL)
if lib_symbols_match:
    block = lib_symbols_match.group(1)
else:
    start_idx = content.find('(lib_symbols')
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
    block = content[start_idx:end_idx]

# Find symbols in block
matches = re.finditer(r'\(symbol\s+"([^"]+)"', block)
for m in matches:
    name = m.group(1)
    if "XIAO" in name:
        print(f"Symbol: {name}")
        # find matching paren
        s_start = m.start()
        pc = 0
        s_end = s_start
        for i in range(s_start, len(block)):
            if block[i] == '(':
                pc += 1
            elif block[i] == ')':
                pc -= 1
                if pc == 0:
                    s_end = i + 1
                    break
        body = block[s_start:s_end]
        
        # find pins
        pins = re.findall(r'\(pin\s+\S+\s+\S+\s*\(at\s+([\d.-]+)\s+([\d.-]+)\s*([\d.-]*)\)(.*?)\(number\s+"([^"]+)"', body, re.DOTALL)
        for px, py, prot, pbody, pnum in pins:
            pname_m = re.search(r'\(name\s+"([^"]*)"', pbody)
            pname = pname_m.group(1) if pname_m else ""
            print(f"  Pin {pnum} ({pname}): rel=({px}, {py})")
