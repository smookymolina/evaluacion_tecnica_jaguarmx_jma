import re

sch_path = r"C:\Users\GIRTEC\Claude\Projects\Jaguar MX\kicad\PCB\PCB.kicad_sch"

with open(sch_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Let's search for "property \"Reference\" \"U1\""
matches = re.finditer(r'property\s+"Reference"\s+"U1"', content)

for idx, match in enumerate(matches):
    print(f"Match {idx+1}:")
    # Let's find the start of the symbol block containing this match
    # We can go backwards to find the outer-most (symbol that is open at this point
    pos = match.start()
    paren_count = 0
    # Let's walk backwards to find the matching (symbol
    # A symbol block starts with (symbol ...
    # We can walk backwards and look for (symbol (lib_id "..."
    # or just find the enclosing S-expression
    block_start = -1
    for i in range(pos, 0, -1):
        if content[i:i+7] == '(symbol':
            # check if it is part of a lib_id or start of block
            # In KiCad, instances are (symbol (lib_id "...") (at ...)
            # Let's check if the text following is (lib_id
            suffix = content[i+7:i+20]
            if '(lib_id' in suffix or ' ' in suffix:
                block_start = i
                break
    
    if block_start != -1:
        # Find the end of this block
        p_count = 0
        block_end = block_start
        for i in range(block_start, len(content)):
            if content[i] == '(':
                p_count += 1
            elif content[i] == ')':
                p_count -= 1
                if p_count == 0:
                    block_end = i + 1
                    break
        block = content[block_start:block_end]
        print(block)
        print("="*40)
