import os

filepath = r"C:\Users\GIRTEC\Claude\Projects\Jaguar MX\kicad\PCB\PCB.kicad_pcb"
with open(filepath, 'r', encoding='utf-8') as f:
    lines = f.readlines()

inside_ref = False
ref_paren_level = 0
paren_level = 0

for i in range(len(lines)):
    line = lines[i]
    
    # We update paren_level based on the characters in the line
    # However, property starts at a certain level.
    # Let's just track when we see property "Reference"
    
    if '(property "Reference"' in line:
        inside_ref = True
        # The level of the parent is the current level before this line adds its opening paren
        # Wait, the line itself has '('. Let's count properly.
    
    if inside_ref:
        if '(hide yes)' in line:
            print(f"Found hidden reference at line {i+1}, making it visible.")
            lines[i] = line.replace('(hide yes)', '')
            
    # Update paren_level
    paren_level += line.count('(') - line.count(')')
    
    # If we are inside ref and we drop back to the level where it started, we exited the property
    if inside_ref and line.count(')') > 0:
        # We need a robust way to know we exited. 
        # Actually, if we see another (property or we see (path or (attr, we probably exited.
        # But tracking paren_level is safest.
        pass

# Let's do a simpler state machine without paren_level, since KiCad formats nicely:
inside_ref = False
for i in range(len(lines)):
    line = lines[i]
    if '(property "Reference"' in line:
        inside_ref = True
    elif '(property' in line or '(path' in line or '(attr' in line or '(fp_text' in line or '(fp_line' in line:
        # A new property or footprint element started, so we are definitely out of the Reference property
        if '(property "Reference"' not in line:
            inside_ref = False
            
    if inside_ref and '(hide yes)' in line:
        lines[i] = line.replace('(hide yes)', '')
        print(f"Unhid reference at line {i+1}")

with open(filepath, 'w', encoding='utf-8') as f:
    f.writelines(lines)

print("Done")
