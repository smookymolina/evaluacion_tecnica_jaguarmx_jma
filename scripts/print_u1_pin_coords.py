import re
import math

sch_path = r"C:\Users\GIRTEC\Claude\Projects\Jaguar MX\kicad\PCB\PCB.kicad_sch"

with open(sch_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Find Seeed_Studio_XIAO_Series:XIAO-RP2350-DIP in content
sym_match = re.search(r'\(symbol\s+"Seeed_Studio_XIAO_Series:XIAO-RP2350-DIP"', content)
if sym_match:
    s_start = sym_match.start()
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
    
    pin_matches = re.finditer(r'\(pin\s+(\S+)\s+(\S+)\s*\(at\s+([\d.-]+)\s+([\d.-]+)\s*([\d.-]*)\)(.*?)\(number\s+"([^"]+)"', sym_body, re.DOTALL)
    for pm in pin_matches:
        ptype = pm.group(1)
        pshape = pm.group(2)
        px = float(pm.group(3))
        py = float(pm.group(4))
        pbody = pm.group(6)
        pnum = pm.group(7)
        
        name_m = re.search(r'\(name\s+"([^"]*)"', pbody)
        pname = name_m.group(1) if name_m else ""
        
        # Apply translation to U1 instance coordinates
        # U1 instance is at: X=165.1, Y=78.74, rot=0, unit=1
        abs_x = round(165.1 + px, 2)
        abs_y = round(78.74 + py, 2)
        
        print(f"Pin {pnum} ({pname}): rel=({px}, {py}), abs=({abs_x}, {abs_y})")
else:
    print("XIAO-RP2350-DIP not found.")
