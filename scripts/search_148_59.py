import re

sch_path = r"C:\Users\GIRTEC\Claude\Projects\Jaguar MX\kicad\PCB\PCB.kicad_sch"

with open(sch_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Search for "148.59" in the schematic
print("Occurrences of 148.59:")
matches = re.finditer(r'148\.59', content)
for m in matches:
    pos = m.start()
    # print 100 chars around it
    print(content[max(0, pos-50):min(len(content), pos+50)])
