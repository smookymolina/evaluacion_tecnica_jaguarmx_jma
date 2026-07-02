import re

sch_path = r"C:\Users\GIRTEC\Claude\Projects\Jaguar MX\kicad\PCB\PCB.kicad_sch"

with open(sch_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Let's write a simpler script to find J1 and LED1 symbol instances, print their lib_id, and print the lib_symbols definition matching them
inst_matches = re.finditer(r'\(symbol\s*\(lib_id\s*"([^"]+)"', content)
for match in inst_matches:
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
    
    ref_m = re.search(r'\(property\s+"Reference"\s+"([^"]+)"', block)
    if ref_m:
        ref = ref_m.group(1)
        if ref in ["J1", "LED1", "J2"]:
            at_m = re.search(r'\(at\s+([\d.-]+)\s+([\d.-]+)\s*([\d.-]*)', block)
            lib_id = match.group(1)
            print(f"Component: {ref} | lib_id: {lib_id} | at: ({at_m.group(1)}, {at_m.group(2)})")
            
            # Find in lib_symbols
            # We can search for the lib_id block
            # For example: (symbol "lib_id" ... )
            lib_sym_name = lib_id
            # sometimes it has a suffix in lib_symbols or is defined slightly differently. Let's do a regex search for the definition
            lib_match = re.search(r'\(symbol\s+"' + re.escape(lib_id) + r'".*?\n\t\)', content, re.DOTALL)
            if not lib_match:
                # search for partial match
                base_lib_id = lib_id.split(':')[-1]
                matches = re.finditer(r'\(symbol\s+"([^"]+)"', content)
                for lm in matches:
                    sym_name = lm.group(1)
                    if base_lib_id in sym_name:
                        print(f"  Matches symbol definition: {sym_name}")
            else:
                print(f"  Found exact symbol definition.")
