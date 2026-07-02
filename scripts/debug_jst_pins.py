import re

sch_path = r"C:\Users\GIRTEC\Claude\Projects\Jaguar MX\kicad\PCB\PCB.kicad_sch"

with open(sch_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Find JST symbol definition
match = re.search(r'\(symbol\s+"jaguar_power:Conn_01x02_JST_P2.0mm_Horizontal_PTH"', content)
if match:
    s_start = match.start()
    pc = 0
    s_end = s_start
    for i in range(s_start, len(content)):
        if content[i] == '(':
            pc += 1
        elif content[i] == ')':
            pc -= 1
            if pc == 0:
                s_end = i + 1
                break
    sym_body = content[s_start:s_end]
    
    pins = re.findall(r'\(pin\s+\S+\s+\S+\s*\(at\s+([\d.-]+)\s+([\d.-]+)\s*([\d.-]*)\)(.*?)\(number\s+"([^"]+)"', sym_body, re.DOTALL)
    for px, py, prot, pbody, pnum in pins:
        pname_m = re.search(r'\(name\s+"([^"]*)"', pbody)
        pname = pname_m.group(1) if pname_m else ""
        print(f"Pin {pnum} ({pname}): rel=({px}, {py})")
else:
    print("Conn_01x02_JST_P2.0mm_Horizontal_PTH not found.")
