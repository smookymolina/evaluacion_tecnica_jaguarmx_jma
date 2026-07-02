import re

guide_path = r"C:\Users\GIRTEC\Claude\Projects\Jaguar MX\FASE3_Guia_Esquematico_KiCad_JaguarMX.md"

with open(guide_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

print("Occurrences of U3 or TB6612 in Guide:")
for idx, line in enumerate(lines):
    if 'u3' in line.lower() or 'tb6612' in line.lower():
        print(f"Line {idx+1}: {line.strip()}")
