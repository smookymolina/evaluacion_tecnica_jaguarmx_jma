import re
import shutil

src = r"C:\Users\GIRTEC\Claude\Projects\Jaguar MX\kicad\PCB\PCB.kicad_pcb"
dst = r"C:\Users\GIRTEC\Claude\Projects\Jaguar MX\kicad\PCB\PCBv2.kicad_pcb"
shutil.copy2(src, dst)

placement = {
    "U1": (135, 95, 0),
    "U3": (165, 95, 0),
    "U2": (125, 75, 270),
    "U4": (160, 110, 0),
    "Q1": (180, 105, 0),
    "J7": (115, 75, 270),
    "J6": (185, 80, 270),
    "J1": (115, 88, 270),
    "J2": (115, 102, 270),
    "J3": (155, 120, 0),
    "J5": (180, 120, 0),
    "SW1": (120, 115, 0),
    "J9": (170, 110, 0),
    "NT1": (150, 105, 0),
    # 5V In / LDO support
    "C1": (118, 73, 90),
    "C3": (118, 77, 90),
    "C2": (128, 73, 90),
    "C4": (128, 77, 90),
    "F1": (133, 75, 0),
    "C15": (115, 79, 90),
    "TP4": (115, 82, 0),
    # U1 support
    "C9": (135, 86, 0),
    # U3 support
    "C7": (160, 89, 90),
    "C8": (165, 89, 90),
    "R5": (170, 95, 0),
    # Q1 / 48V support
    "C10": (178, 80, 0),
    "C11": (180, 84, 0),
    "R6": (175, 105, 0),
    "R7": (180, 110, 90),
    "D3": (175, 120, 0),
    # NTC int
    "R3": (118, 88, 0),
    "R1": (122, 88, 0),
    "D1": (126, 88, 0),
    "C5": (128, 90, 90),
    # NTC ext
    "R4": (118, 102, 0),
    "R2": (122, 102, 0),
    "D2": (126, 102, 0),
    "C6": (128, 100, 90),
    # DIP support
    "R9": (130, 113, 0),
    "C12": (132, 113, 0),
    "R10": (130, 116, 0),
    "C13": (132, 116, 0),
    "R11": (130, 119, 0),
    "C14": (132, 119, 0),
    # LEDs and TPs
    "LED1": (115, 120, 0),
    "R_LED1": (118, 120, 0),
    "TP1": (135, 72, 0),
    "TP2": (140, 72, 0),
    "TP5": (145, 72, 0),
    "TP6": (125, 85, 0),
    "TP7": (125, 105, 0),
    "TP3": (180, 75, 0),
    "TP8": (184, 105, 0)
}

with open(dst, 'r', encoding='utf-8') as f:
    text = f.read()

out = []
i = 0
while i < len(text):
    # Find next footprint
    idx = text.find('(footprint ', i)
    if idx == -1:
        out.append(text[i:])
        break
    
    out.append(text[i:idx])
    
    # Find end of this footprint
    paren_level = 0
    end_idx = idx
    for j in range(idx, len(text)):
        if text[j] == '(':
            paren_level += 1
        elif text[j] == ')':
            paren_level -= 1
            if paren_level == 0:
                end_idx = j + 1
                break
    
    footprint_text = text[idx:end_idx]
    
    # Find reference
    ref_match = re.search(r'\(property "Reference" "([^"]+)"', footprint_text)
    if ref_match:
        ref = ref_match.group(1)
        if ref in placement:
            x, y, rot = placement[ref]
            
            # Find the first (at ...) which belongs to the footprint
            # Because property 'at's are indented more, but we can just find the first one.
            at_idx = footprint_text.find('(at ')
            if at_idx != -1:
                at_end_idx = footprint_text.find(')', at_idx)
                if rot == 0:
                    new_at = f"(at {x} {y}"
                else:
                    new_at = f"(at {x} {y} {rot}"
                
                footprint_text = footprint_text[:at_idx] + new_at + footprint_text[at_end_idx:]
    
    out.append(footprint_text)
    i = end_idx

with open(dst, 'w', encoding='utf-8') as f:
    f.write("".join(out))

print("Optimization complete!")
