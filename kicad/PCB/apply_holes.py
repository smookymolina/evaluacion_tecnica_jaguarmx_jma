import pcbnew
import sys

pcb_path = r"C:\Users\GIRTEC\Claude\Projects\Jaguar MX\kicad\PCB\PCBv6.kicad_pcb"
board = pcbnew.LoadBoard(pcb_path)

lib_path = r"C:\Program Files\KiCad\10.0\share\kicad\footprints\MountingHole.pretty"
fp_name = "MountingHole_3.2mm_M3_Pad"

targets = [
    {"ref": "H1", "x": 114.5, "y": 77.5, "net": "/AGND"},
    {"ref": "H2", "x": 185.5, "y": 77.5, "net": "/PGND"},
    {"ref": "H3", "x": 114.5, "y": 117.5, "net": "/AGND"},
    {"ref": "H4", "x": 185.5, "y": 117.5, "net": "/PGND"}
]

for t in targets:
    # Load footprint
    fp = pcbnew.FootprintLoad(lib_path, fp_name)
    if not fp:
        print(f"Failed to load {fp_name}")
        sys.exit(1)
        
    fp.SetReference(t["ref"])
    fp.SetPosition(pcbnew.VECTOR2I(pcbnew.FromMM(t["x"]), pcbnew.FromMM(t["y"])))
    
    # Assign net to all pads in the mounting hole (usually just one pad)
    netcode = board.GetNetcodeFromNetname(t["net"])
    if netcode <= 0:
        print(f"Warning: Net {t['net']} not found!")
    
    for pad in fp.Pads():
        pad.SetNetCode(netcode)
        
    board.Add(fp)
    print(f"Added {t['ref']} at ({t['x']}, {t['y']}) with net {t['net']}")

# Refill zones
print("Refilling zones...")
filler = pcbnew.ZONE_FILLER(board)
filler.Fill(board.Zones())

# Save the board
print("Saving board...")
pcbnew.SaveBoard(pcb_path, board)
print("Done.")

