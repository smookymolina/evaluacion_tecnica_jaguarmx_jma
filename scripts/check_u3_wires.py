import re

sch_path = r"C:\Users\GIRTEC\Claude\Projects\Jaguar MX\kicad\PCB\PCB.kicad_sch"

with open(sch_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Let's find all wires and print those that have any coordinate matching U3 pins
# U3 pins absolute coordinates:
# Pin 1: (73.66, 137.16)
# Pin 2: (73.66, 137.16)
# Pin 3: (60.96, 101.6)
# Pin 4: (60.96, 101.6)
# Pin 5: (73.66, 132.08)
# Pin 6: (73.66, 132.08)
# Pin 7: (73.66, 119.38)
# Pin 8: (73.66, 119.38)
# Pin 9: (66.04, 101.6)
# Pin 10: (66.04, 101.6)
# Pin 11: (73.66, 124.46)
# Pin 12: (73.66, 124.46)
# Pin 13: (63.5, 152.4)
# Pin 14: (66.04, 152.4)
# Pin 15: (43.18, 129.54)
# Pin 16: (43.18, 116.84)
# Pin 17: (43.18, 119.38)
# Pin 18: (50.8, 101.6)
# Pin 19: (43.18, 137.16)
# Pin 20: (50.8, 152.4)
# Pin 21: (43.18, 124.46)
# Pin 22: (43.18, 121.92)
# Pin 23: (43.18, 132.08)
# Pin 24: (60.96, 152.4)

u3_pins = {
    (73.66, 137.16): "Pin 1/2 (AO1)",
    (60.96, 101.6): "Pin 3/4 (PGND1)",
    (73.66, 132.08): "Pin 5/6 (AO2)",
    (73.66, 119.38): "Pin 7/8 (BO2)",
    (66.04, 101.6): "Pin 9/10 (PGND2)",
    (73.66, 124.46): "Pin 11/12 (BO1)",
    (63.5, 152.4): "Pin 13 (VM2)",
    (66.04, 152.4): "Pin 14 (VM3)",
    (43.18, 129.54): "Pin 15 (PWMB)",
    (43.18, 116.84): "Pin 16 (BIN2)",
    (43.18, 119.38): "Pin 17 (BIN1)",
    (50.8, 101.6): "Pin 18 (GND)",
    (43.18, 137.16): "Pin 19 (STBY)",
    (50.8, 152.4): "Pin 20 (VCC)",
    (43.18, 124.46): "Pin 21 (AIN1)",
    (43.18, 121.92): "Pin 22 (AIN2)",
    (43.18, 132.08): "Pin 23 (PWMA)",
    (60.96, 152.4): "Pin 24 (VM1)"
}

wires = re.findall(r'\(wire\s*\(pts\s*\(xy\s+([\d.-]+)\s+([\d.-]+)\)\s*\(xy\s+([\d.-]+)\s+([\d.-]+)\)\s*\)', content)

print("Wires connected directly to U3 pins:")
for pt1_x, pt1_y, pt2_x, pt2_y in wires:
    p1 = (round(float(pt1_x), 2), round(float(pt1_y), 2))
    p2 = (round(float(pt2_x), 2), round(float(pt2_y), 2))
    
    conn1 = u3_pins.get(p1, None)
    conn2 = u3_pins.get(p2, None)
    
    if conn1 or conn2:
        print(f"Wire: {p1} -> {p2}")
        if conn1:
            print(f"  Start is U3 {conn1}")
        if conn2:
            print(f"  End is U3 {conn2}")
