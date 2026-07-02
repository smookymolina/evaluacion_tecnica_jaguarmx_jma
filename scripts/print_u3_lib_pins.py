import re

sch_path = r"C:\Users\GIRTEC\Claude\Projects\Jaguar MX\kicad\PCB\PCB.kicad_sch"

with open(sch_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Let's find the symbol block of U3 in lib_symbols
sym_match = re.search(r'\(symbol\s+"Driver_Motor:TB6612FNG"(.*?)\n\t\)', content, re.DOTALL)
if not sym_match:
    # try parenthesization matching
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
        
        # print the pin sub-expressions
        pins = re.findall(r'\(pin\s+\S+\s+\S+\s*\(at\s+[\d.-]+\s+[\d.-]+\s*[\d.-]*\).*?\(number\s+"[^"]+"\s*\(effects[^)]*\)\)\s*\)', sym_body, re.DOTALL)
        print("Pins in library definition:")
        for p in pins:
            print(p.strip())
