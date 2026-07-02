import re

sch_path = r"C:\Users\GIRTEC\Claude\Projects\Jaguar MX\kicad\PCB\PCB.kicad_sch"

with open(sch_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Let's search for the symbol block of U3
match = re.search(r'\(symbol\s*\(lib_id\s*"Driver_Motor:TB6612FNG".*?property\s*"Reference"\s*"U3".*?\)', content, re.DOTALL)
if not match:
    # broad search
    matches = re.finditer(r'\(symbol\s*\(lib_id\s*"[^"]+"', content)
    for m in matches:
        start_idx = m.start()
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
        if 'property "Reference" "U3"' in block:
            print("U3 Instance block:")
            print(block)
            break
else:
    print("U3 Instance block:")
    print(match.group(0))
