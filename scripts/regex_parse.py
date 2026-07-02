import re

sch_path = r"C:\Users\GIRTEC\Claude\Projects\Jaguar MX\kicad\PCB\PCB.kicad_sch"

with open(sch_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Let's count some basic terms
print("Occurrences of '(symbol':", content.count('(symbol'))
print("Occurrences of '(wire':", content.count('(wire'))
print("Occurrences of '(junction':", content.count('(junction'))
print("Occurrences of '(label':", content.count('(label'))
print("Occurrences of '(global_label':", content.count('(global_label'))
print("Occurrences of '(hierarchical_label':", content.count('(hierarchical_label'))

# Let's find wires using regex
# Wire format in KiCad v6+:
# (wire
#   (pts
#     (xy 20.32 40.64)
#     (xy 30.48 40.64)
#   )
#   (stroke (width 0) (type solid))
#   (uuid "...")
# )
wire_matches = re.findall(r'\(wire\s*\(pts\s*\(xy\s+([\d.-]+)\s+([\d.-]+)\)\s*\(xy\s+([\d.-]+)\s+([\d.-]+)\)\s*\)', content)
print(f"Wires found using simple regex: {len(wire_matches)}")

# Let's write a parser that handles the multi-line format of wire
# We can find all blocks starting with (wire and find the pts inside
wire_blocks = re.findall(r'\(wire\s*\(pts\s*(.*?)\)\s*\(stroke', content, re.DOTALL)
print(f"Wire blocks found: {len(wire_blocks)}")
for wb in wire_blocks[:5]:
    print("  Block:", wb.strip())
