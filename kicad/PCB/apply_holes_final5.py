import pcbnew
import sys

pcb_path = r"C:\Users\GIRTEC\Claude\Projects\Jaguar MX\kicad\PCB\PCBv6.kicad_pcb"
board = pcbnew.LoadBoard(pcb_path)

# Remove old ones
for ref in ["H1", "H2", "H3", "H4", "H5"]:
    fp = board.FindFootprintByReference(ref)
    if fp:
        board.RemoveNative(fp)

lib_path = r"C:\Program Files\KiCad\10.0\share\kicad\footprints\MountingHole.pretty"
fp_name = "MountingHole_3.2mm_M3_Pad"

targets = [
    {"ref": "H1", "x": 113.0, "y": 73.0, "net": "/AGND"},
    {"ref": "H2", "x": 187.0, "y": 73.0, "net": "/PGND"},
    {"ref": "H3", "x": 113.0, "y": 122.0, "net": "/AGND"},
    {"ref": "H4", "x": 187.0, "y": 122.0, "net": "/PGND"}
]

for t in targets:
    fp = pcbnew.FootprintLoad(lib_path, fp_name)
    if not fp:
        print("Failed to load footprint")
        sys.exit(1)
        
    fp.SetReference(t["ref"])
    fp.SetPosition(pcbnew.VECTOR2I(pcbnew.FromMM(t["x"]), pcbnew.FromMM(t["y"])))
    
    # Set pad size to 5.0mm to clear everything perfectly
    netcode = board.GetNetcodeFromNetname(t["net"])
    for pad in fp.Pads():
        pad.SetSize(pcbnew.VECTOR2I(pcbnew.FromMM(5.0), pcbnew.FromMM(5.0)))
        if netcode > 0:
            pad.SetNetCode(netcode)
            
    board.Add(fp)
    print(f"Added {t['ref']} at ({t['x']}, {t['y']})")

print("Refilling zones...")
filler = pcbnew.ZONE_FILLER(board)
filler.Fill(board.Zones())

print("Saving board...")
pcbnew.SaveBoard(pcb_path, board)
print("Done.")

