import re

sch_path = r"C:\Users\GIRTEC\Claude\Projects\Jaguar MX\kicad\PCB\PCB.kicad_sch"

with open(sch_path, 'r', encoding='utf-8') as f:
    content = f.read()

matches = re.finditer(r'\(symbol\s*\(lib_id\s*"Seeed_Studio_XIAO_Series:XIAO-RP2350-DIP"', content)
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
    print(block)
