import pcbnew

pcb_path = r"C:\Users\GIRTEC\Claude\Projects\Jaguar MX\kicad\PCB\PCBv6.kicad_pcb"
board = pcbnew.LoadBoard(pcb_path)

targets = [
    {"ref": "H1", "x": 113.5, "y": 74.0, "net": "/AGND"},
    {"ref": "H2", "x": 186.5, "y": 74.0, "net": "/PGND"},
    {"ref": "H3", "x": 113.5, "y": 121.0, "net": "/AGND"},
    {"ref": "H4", "x": 186.5, "y": 121.0, "net": "/PGND"}
]

for t in targets:
    fp = board.FindFootprintByReference(t["ref"])
    if not fp:
        # Load it if not found (should be found since we added it)
        lib_path = r"C:\Program Files\KiCad\10.0\share\kicad\footprints\MountingHole.pretty"
        fp = pcbnew.FootprintLoad(lib_path, "MountingHole_3.2mm_M3_Pad")
        fp.SetReference(t["ref"])
        board.Add(fp)

    fp.SetPosition(pcbnew.VECTOR2I(pcbnew.FromMM(t["x"]), pcbnew.FromMM(t["y"])))
    
    for pad in fp.Pads():
        pad.SetSize(pcbnew.VECTOR2I(pcbnew.FromMM(5.0), pcbnew.FromMM(5.0)))
        netcode = board.GetNetcodeFromNetname(t["net"])
        pad.SetNetCode(netcode)
        
    for item in list(fp.GraphicalItems()):
        layer_name = board.GetLayerName(item.GetLayer())
        if "Courtyard" in layer_name:
            fp.Remove(item)

print("Refilling zones...")
filler = pcbnew.ZONE_FILLER(board)
filler.Fill(board.Zones())

print("Saving board...")
pcbnew.SaveBoard(pcb_path, board)
print("Done.")

