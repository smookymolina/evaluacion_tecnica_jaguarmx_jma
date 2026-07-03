import pcbnew

pcb_path = r"C:\Users\GIRTEC\Claude\Projects\Jaguar MX\kicad\PCB\PCBv6.kicad_pcb"
board = pcbnew.LoadBoard(pcb_path)

targets = {
    "H1": {"x": 113.5, "y": 74.0, "net": "/AGND"},
    "H2": {"x": 186.5, "y": 74.0, "net": "/PGND"},
    "H3": {"x": 113.5, "y": 121.0, "net": "/AGND"},
    "H4": {"x": 186.5, "y": 121.0, "net": "/PGND"}
}

for fp in board.GetFootprints():
    ref = fp.GetReference()
    if ref in targets:
        t = targets[ref]
        fp.SetPosition(pcbnew.VECTOR2I(pcbnew.FromMM(t["x"]), pcbnew.FromMM(t["y"])))
        
        for pad in fp.Pads():
            pad.SetSize(pcbnew.VECTOR2I(pcbnew.FromMM(5.0), pcbnew.FromMM(5.0)))
            netcode = board.GetNetcodeFromNetname(t["net"])
            pad.SetNetCode(netcode)
            
        items_to_remove = []
        for item in fp.GraphicalItems():
            layer_name = board.GetLayerName(item.GetLayer())
            if "Courtyard" in layer_name:
                items_to_remove.append(item)
        for item in items_to_remove:
            fp.Remove(item)

print("Refilling zones...")
filler = pcbnew.ZONE_FILLER(board)
filler.Fill(board.Zones())

print("Saving board...")
pcbnew.SaveBoard(pcb_path, board)
print("Done.")

