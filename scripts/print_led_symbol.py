import re

sch_path = r"C:\Users\GIRTEC\Claude\Projects\Jaguar MX\kicad\PCB\PCB.kicad_sch"

with open(sch_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Let's search for "property \"Reference\" \"LED1\""
matches = re.finditer(r'property\s+"Reference"\s+"LED1"', content)

for idx, match in enumerate(matches):
    pos = match.start()
    block_start = -1
    for i in range(pos, 0, -1):
        if content[i:i+7] == '(symbol':
            suffix = content[i+7:i+20]
            if '(lib_id' in suffix or ' ' in suffix:
                block_start = i
                break
    if block_start != -1:
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
