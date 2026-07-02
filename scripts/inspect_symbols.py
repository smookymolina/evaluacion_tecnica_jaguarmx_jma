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
    
    # Let's find each symbol inside lib_symbols
    # S-expression format: (symbol "Library:SymbolName" ... )
    symbol_matches = re.finditer(r'\(symbol\s+"([^"]+)"', lib_symbols_block)
    
    for match in symbol_matches:
        sym_name = match.group(1)
        # find the end of this specific symbol block
        sym_start = match.start()
        p_count = 0
        sym_end = sym_start
        for i in range(sym_start, len(lib_symbols_block)):
            if lib_symbols_block[i] == '(':
                p_count += 1
            elif lib_symbols_block[i] == ')':
                p_count -= 1
                if p_count == 0:
                    sym_end = i + 1
                    break
        sym_body = lib_symbols_block[sym_start:sym_end]
        
        # Print all symbols
        print(f"Symbol: {sym_name}")
        pins = re.findall(r'\(pin\s+\S+\s+\S+\s+\(at[^)]+\)\s*\(effects[^)]*\)\s*\(name\s+"([^"]*)"\s*\(effects[^)]*\)\)\s*\(number\s+"([^"]+)"', sym_body)
        if not pins:
            pin_blocks = re.findall(r'\(pin\s+\w+\s+\w+\s*\(at[^)]+\)(.*?)\(number\s+"([^"]+)"', sym_body, re.DOTALL)
            for pb, pnum in pin_blocks:
                pname_m = re.search(r'\(name\s+"([^"]*)"', pb)
                pname = pname_m.group(1) if pname_m else ""
                print(f"  Pin {pnum}: {pname}")
        else:
            for pname, pnum in pins:
                print(f"  Pin {pnum}: {pname}")
        print("-" * 40)
else:
    print("lib_symbols block not found.")
