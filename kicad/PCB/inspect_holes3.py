import pcbnew
import sys
import math

pcb_path = r"C:\Users\GIRTEC\Claude\Projects\Jaguar MX\kicad\PCB\PCBv6.kicad_pcb"
board = pcbnew.LoadBoard(pcb_path)

targets = [
    {"name": "TL", "x": 114.5, "y": 77.0},
    {"name": "TR", "x": 185.5, "y": 77.0},
    {"name": "BL", "x": 114.5, "y": 118.0},
    {"name": "BR", "x": 185.5, "y": 118.0}
]

print("Checking clearance for symmetrical inset (X=4.5, Y=7.0):")
for t in targets:
    print(f"\n--- Corner {t['name']} @ ({t['x']}, {t['y']}) ---")
    for module in board.GetFootprints():
        pos = module.GetPosition()
        mx, my = pcbnew.ToMM(pos.x), pcbnew.ToMM(pos.y)
        dist = math.hypot(mx - t['x'], my - t['y'])
        if dist < 6: 
            print(f"  Warning! {module.GetReference()} is at {dist:.2f}mm ({mx:.1f}, {my:.1f})")

