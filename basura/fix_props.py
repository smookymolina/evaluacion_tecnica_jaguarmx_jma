import re

filepath = r"C:\Users\GIRTEC\Claude\Projects\Jaguar MX\kicad\PCB\PCB.kicad_pcb"
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

def fix_properties(text):
    out = []
    i = 0
    while i < len(text):
        idx = text.find('(property "', i)
        if idx == -1:
            out.append(text[i:])
            break
        
        out.append(text[i:idx])
        
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
        
        prop_text = text[idx:end_idx]
        
        m = re.match(r'\(property\s+"([^"]+)"', prop_text)
        if m:
            prop_name = m.group(1)
            # Make sure Reference and Value are NOT hidden
            if prop_name in ["Reference", "Value"]:
                prop_text = re.sub(r'\s*\(hide yes\)', '', prop_text)
            else:
                # All other properties SHOULD be hidden
                if '(hide yes)' not in prop_text:
                    eff_idx = prop_text.find('(effects')
                    if eff_idx != -1:
                        # Insert (hide yes) right after (effects
                        prop_text = prop_text.replace('(effects', '(effects (hide yes)', 1)
        
        out.append(prop_text)
        i = end_idx
        
    return "".join(out)

new_content = fix_properties(content)
with open(filepath, 'w', encoding='utf-8') as f:
    f.write(new_content)
print("Properties fixed!")
