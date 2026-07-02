import re

sch_path = r"C:\Users\GIRTEC\Claude\Projects\Jaguar MX\kicad\PCB\PCB.kicad_sch"

with open(sch_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Let's search for "LED1" in the schematic
matches = re.finditer(r'LED1', content)
for m in matches:
    pos = m.start()
    print(content[pos-100:pos+100])
