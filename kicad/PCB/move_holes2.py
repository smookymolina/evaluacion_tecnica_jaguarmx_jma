import pcbnew
import sys

pcb_path = r"C:\Users\GIRTEC\Claude\Projects\Jaguar MX\kicad\PCB\PCBv6.kicad_pcb"
board = pcbnew.LoadBoard(pcb_path)

targets = [
    {"ref": "H1", "x": 113.8, "y": 74.5},
    {"ref": "H2", "x": 186.2, "y": 74.5},
    {"ref": "H3", "x": 113.8, "y": 121.2},
    {"ref": "H4", "x": 186.2, "y": 121.2}
]

for t in targets:
    fp = board.FindFootprintByReference(t["ref"])
    if fp:
        fp.SetPosition(pcbnew.VECTOR2I(pcbnew.FromMM(t["x"]), pcbnew.FromMM(t["y"])))
        print(f"Moved {t['ref']} to ({t['x']}, {t['y']})")
    else:
        print(f"Could not find {t['ref']}")

# Refill zones
print("Refilling zones...")
filler = pcbnew.ZONE_FILLER(board)
filler.Fill(board.Zones())

# Save the board
print("Saving board...")
pcbnew.SaveBoard(pcb_path, board)
print("Done.")

