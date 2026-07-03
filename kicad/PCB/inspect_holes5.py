import pcbnew
import sys
import math

pcb_path = r"C:\Users\GIRTEC\Claude\Projects\Jaguar MX\kicad\PCB\PCBv6.kicad_pcb"
board = pcbnew.LoadBoard(pcb_path)

targets = [
    {"name": "TL", "x": 113.5, "y": 76.5},
    {"name": "TR", "x": 186.5, "y": 76.5},
    {"name": "BL", "x": 113.5, "y": 120.5},
    {"name": "BR", "x": 186.5, "y": 120.5}
]

print("Checking clearance for new targets:")
for t in targets:
    print(f"\n--- Corner {t['name']} @ ({t['x']}, {t['y']}) ---")
    for module in board.GetFootprints():
        # skip our mounting holes H1, H2, H3, H4
        if module.GetReference() in ["H1", "H2", "H3", "H4"]:
            continue
        pos = module.GetPosition()
        mx, my = pcbnew.ToMM(pos.x), pcbnew.ToMM(pos.y)
        dist = math.hypot(mx - t['x'], my - t['y'])
        if dist < 6: 
            print(f"  Warning! {module.GetReference()} is at {dist:.2f}mm ({mx:.1f}, {my:.1f})")

