import pcbnew
import sys
import math

pcb_path = r"C:\Users\GIRTEC\Claude\Projects\Jaguar MX\kicad\PCB\PCBv6.kicad_pcb"
board = pcbnew.LoadBoard(pcb_path)

targets = [
    {"name": "TL", "x": 113.5, "y": 73.5},
    {"name": "TR", "x": 186.5, "y": 73.5},
    {"name": "BL", "x": 113.5, "y": 121.5},
    {"name": "BR", "x": 186.5, "y": 121.5}
]

print("Checking clearance for inset 3.5mm (radius 4.5mm):")
for t in targets:
    print(f"\n--- Corner {t['name']} @ ({t['x']}, {t['y']}) ---")
    for module in board.GetFootprints():
        pos = module.GetPosition()
        mx, my = pcbnew.ToMM(pos.x), pcbnew.ToMM(pos.y)
        dist = math.hypot(mx - t['x'], my - t['y'])
        if dist < 6: 
            print(f"  Warning! {module.GetReference()} is at {dist:.2f}mm")

