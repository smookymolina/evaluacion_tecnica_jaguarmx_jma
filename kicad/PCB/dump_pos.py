import pcbnew
import sys

pcb_path = r"C:\Users\GIRTEC\Claude\Projects\Jaguar MX\kicad\PCB\PCBv6.kicad_pcb"
board = pcbnew.LoadBoard(pcb_path)

print("Component positions:")
for fp in board.GetFootprints():
    if fp.GetReference() not in ["H1", "H2", "H3", "H4"]:
        pos = fp.GetPosition()
        print(f"{fp.GetReference()}: ({pcbnew.ToMM(pos.x):.1f}, {pcbnew.ToMM(pos.y):.1f})")

