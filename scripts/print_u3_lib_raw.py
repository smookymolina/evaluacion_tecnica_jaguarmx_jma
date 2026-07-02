import re

sch_path = r"C:\Users\GIRTEC\Claude\Projects\Jaguar MX\kicad\PCB\PCB.kicad_sch"

with open(sch_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Let's search for "Driver_Motor:TB6612FNG"
match = re.search(r'\(symbol\s+"Driver_Motor:TB6612FNG"', content)
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
    print(sym_body[:2000]) # print first 2000 chars of symbol definition
