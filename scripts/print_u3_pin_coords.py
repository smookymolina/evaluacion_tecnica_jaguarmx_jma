import re

sch_path = r"C:\Users\GIRTEC\Claude\Projects\Jaguar MX\kicad\PCB\PCB.kicad_sch"

with open(sch_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Let's extract the lib_symbols block
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
    lib_symbols_block = content[start_idx:end_idx]
    
# Find Driver_Motor:TB6612FNG directly in the file content
sym_match = re.search(r'\(symbol\s+"Driver_Motor:TB6612FNG"', content)
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
    
    # Find pins
    pin_matches = re.finditer(r'\(pin\s+(\S+)\s+(\S+)\s*\(at\s+([\d.-]+)\s+([\d.-]+)\s*([\d.-]*)\)(.*?)\(number\s+"([^"]+)"', sym_body, re.DOTALL)
    for pm in pin_matches:
        ptype = pm.group(1)
        pshape = pm.group(2)
        px = float(pm.group(3))
        py = float(pm.group(4))
        prot = float(pm.group(5)) if pm.group(5) else 0.0
        pbody = pm.group(6)
        pnum = pm.group(7)
        
        name_m = re.search(r'\(name\s+"([^"]*)"', pbody)
        pname = name_m.group(1) if name_m else ""
        
        # Apply translation to U3 instance coordinates
        # U3 instance is at: X=58.42, Y=127, rot=0, unit=1
        import math
        rad = math.radians(0) # rot is 0
        cos_t = math.cos(rad)
        sin_t = math.sin(rad)
        rx = px * cos_t - py * sin_t
        ry = px * sin_t + py * cos_t
        abs_x = round(58.42 + rx, 2)
        abs_y = round(127.0 + ry, 2)
        
        print(f"Pin {pnum} ({pname}): rel=({px}, {py}), abs=({abs_x}, {abs_y})")
else:
    print("Driver_Motor:TB6612FNG not found.")
