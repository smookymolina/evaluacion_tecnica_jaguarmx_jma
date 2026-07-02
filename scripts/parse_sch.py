import re

sch_path = r"C:\Users\GIRTEC\Claude\Projects\Jaguar MX\kicad\PCB\PCB.kicad_sch"

with open(sch_path, 'r', encoding='utf-8') as f:
    content = f.read()

# KiCad v6+ symbol syntax:
# (symbol (lib_id ...) (at ...) ...
#   (property "Reference" "R1" ...)
#   (property "Value" "10k" ...)
#   (property "Footprint" "..." ...)
# )

# Let's find all symbol instances
# In KiCad S-expression, symbol instances are at the root level (inside (kicad_sch ...)) and look like:
# (symbol (lib_id ...) (at ...) ... (property "Reference" ...) (property "Value" ...) (property "Footprint" ...))

# We can find them by parsing the top-level S-expressions or using a regex for symbol blocks.
# Let's find all symbol blocks that are NOT inside lib_symbols.
# The lib_symbols block is (lib_symbols ...). We can split the content or remove lib_symbols first.

lib_symbols_match = re.search(r'\(lib_symbols.*?\n\t\)', content, re.DOTALL)
if not lib_symbols_match:
    # Try a broader search for lib_symbols block if formatting differs
    # S-expressions have matching parens. Let's do a simple count of parens to find the end of lib_symbols.
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
        content_no_lib = content[:start_idx] + content[end_idx:]
    else:
        content_no_lib = content
else:
    content_no_lib = content.replace(lib_symbols_match.group(0), "")

# Now find all symbol definitions in content_no_lib
# Each symbol definition starts with (symbol (lib_id ...)
# Let's find them and extract properties
symbol_matches = re.finditer(r'\(symbol\s+\(lib_id', content_no_lib)

components = []

for match in symbol_matches:
    start_idx = match.start()
    paren_count = 0
    end_idx = start_idx
    for i in range(start_idx, len(content_no_lib)):
        if content_no_lib[i] == '(':
            paren_count += 1
        elif content_no_lib[i] == ')':
            paren_count -= 1
            if paren_count == 0:
                end_idx = i + 1
                break
    
    symbol_block = content_no_lib[start_idx:end_idx]
    
    # Extract Reference, Value, Footprint
    ref_m = re.search(r'\(property\s+"Reference"\s+"([^"]+)"', symbol_block)
    val_m = re.search(r'\(property\s+"Value"\s+"([^"]+)"', symbol_block)
    fp_m = re.search(r'\(property\s+"Footprint"\s+"([^"]*)"', symbol_block)
    
    ref = ref_m.group(1) if ref_m else "Unknown"
    val = val_m.group(1) if val_m else "Unknown"
    fp = fp_m.group(1) if fp_m else ""
    
    components.append((ref, val, fp))

# Sort by reference
def natural_sort_key(s):
    return [int(text) if text.isdigit() else text.lower() for text in re.split(r'(\d+)', s[0])]

components.sort(key=natural_sort_key)

print(f"Total placed components found: {len(components)}")
print(f"{'RefDes':<8} | {'Value':<20} | {'Footprint':<50}")
print("-" * 85)
for ref, val, fp in components:
    print(f"{ref:<8} | {val:<20} | {fp:<50}")
