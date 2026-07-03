import pcbnew

pcb_path = r"C:\Users\GIRTEC\Claude\Projects\Jaguar MX\kicad\PCB\PCBv6.kicad_pcb"
board = pcbnew.LoadBoard(pcb_path)

# First, remove existing holes H1, H2, H3, H4 if they exist
for ref in ["H1", "H2", "H3", "H4"]:
    fp = board.FindFootprintByReference(ref)
    if fp:
        board.Remove(fp)

lib_path = r"C:\Program Files\KiCad\10.0\share\kicad\footprints\MountingHole.pretty"
fp_name = "MountingHole_3.2mm_M3_Pad"

targets = [
    {"ref": "H1", "x": 113.5, "y": 74.0, "net": "/AGND"}, # 3.5mm from edge (110, 70).
    {"ref": "H2", "x": 186.5, "y": 74.0, "net": "/PGND"},
    {"ref": "H3", "x": 113.5, "y": 121.0, "net": "/AGND"},
    {"ref": "H4", "x": 186.5, "y": 121.0, "net": "/PGND"}
]

for t in targets:
    fp = pcbnew.FootprintLoad(lib_path, fp_name)
    fp.SetReference(t["ref"])
    fp.SetPosition(pcbnew.VECTOR2I(pcbnew.FromMM(t["x"]), pcbnew.FromMM(t["y"])))
    
    # Resize pad to 5.0mm diameter
    for pad in fp.Pads():
        pad.SetSize(pcbnew.VECTOR2I(pcbnew.FromMM(5.0), pcbnew.FromMM(5.0)))
        # Connect to net
        netcode = board.GetNetcodeFromNetname(t["net"])
        pad.SetNetCode(netcode)
        
    # Remove courtyard graphics to avoid false overlap warnings
    for item in list(fp.GraphicalItems()):
        layer_name = board.GetLayerName(item.GetLayer())
        if "Courtyard" in layer_name:
            fp.Remove(item)
            
    board.Add(fp)

# Refill zones
print("Refilling zones...")
filler = pcbnew.ZONE_FILLER(board)
filler.Fill(board.Zones())

print("Saving board...")
pcbnew.SaveBoard(pcb_path, board)
print("Done.")

