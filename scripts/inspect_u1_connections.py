import re

sch_path = r"C:\Users\GIRTEC\Claude\Projects\Jaguar MX\kicad\PCB\PCB.kicad_sch"

with open(sch_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# In KiCad v6+, the schematic format has:
# (symbol (lib_id ...) (at ...) ... (unit ...)
#    ...
#    (pin "1" (uuid ...))
# )
# And wires are represented by:
# (wire (pts (xy ...) (xy ...)) (uuid ...))
# Or label attachments. Labels are represented by:
# (label "NET_NAME" (at ...) (effects ...) (uuid ...))
# (global_label "NET_NAME" (at ...) (effects ...) (uuid ...))
# (hierarchical_label "NET_NAME" ... )
# Let's inspect all symbol occurrences of U1 in the file.

# First, find symbol instance for U1. It will have (property "Reference" "U1" ...)
# Let's parse symbol instances.

symbol_blocks = []
current_block = []
in_symbol = False
paren_count = 0

for line in lines:
    if '(symbol' in line:
        in_symbol = True
        paren_count = 0
        current_block = []
    
    if in_symbol:
        current_block.append(line)
        paren_count += line.count('(') - line.count(')')
        if paren_count <= 0:
            in_symbol = False
            symbol_blocks.append("".join(current_block))

print(f"Total symbol blocks in schematic: {len(symbol_blocks)}")
for idx, sym in enumerate(symbol_blocks):
    if 'property "Reference" "U1"' in sym:
        print(f"--- Symbol block for U1 (instance {idx}) ---")
        # print the first 20 lines of the block
        print("\n".join(sym.splitlines()[:30]))
        print("...")
        # Check if there are pin overrides or connections
        print("Pins in this block:")
        pin_matches = re.finditer(r'\(pin\s+"([^"]+)"\s+\(uuid\s+"([^"]+)"\)\)', sym)
        for pm in pin_matches:
            print(f"  Pin {pm.group(1)} (uuid: {pm.group(2)})")
