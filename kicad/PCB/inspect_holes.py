import pcbnew
import sys
import math

pcb_path = r"C:\Users\GIRTEC\Claude\Projects\Jaguar MX\kicad\PCB\PCBv6.kicad_pcb"
board = pcbnew.LoadBoard(pcb_path)

print("Board loaded successfully.")

# Target coordinates (mm)
targets = [
    {"name": "TL", "x": 115.0, "y": 75.0, "net": "/AGND"},
    {"name": "TR", "x": 185.0, "y": 75.0, "net": "/PGND"},
    {"name": "BL", "x": 115.0, "y": 120.0, "net": "/AGND"},
    {"name": "BR", "x": 185.0, "y": 120.0, "net": "/PGND"}
]

# Check clearance around these points
print("\nChecking components near target coordinates (radius 6mm):")
for t in targets:
    print(f"--- Corner {t['name']} @ ({t['x']}, {t['y']}) ---")
    tx = pcbnew.FromMM(t['x'])
    ty = pcbnew.FromMM(t['y'])
    
    for module in board.GetFootprints():
        pos = module.GetPosition()
        mx, my = pcbnew.ToMM(pos.x), pcbnew.ToMM(pos.y)
        dist = math.hypot(mx - t['x'], my - t['y'])
        if dist < 15: # if within 15mm, report
            print(f"  Found {module.GetReference()} at ({mx:.2f}, {my:.2f}), distance {dist:.2f}mm")

