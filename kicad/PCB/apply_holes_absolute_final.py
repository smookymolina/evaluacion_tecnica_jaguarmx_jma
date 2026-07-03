import pcbnew
import sys

pcb_path = r"C:\Users\GIRTEC\Claude\Projects\Jaguar MX\kicad\PCB\PCBv6.kicad_pcb"
board = pcbnew.LoadBoard(pcb_path)

# Remove old H1-H4
for ref in ["H1", "H2", "H3", "H4"]:
    fp = board.FindFootprintByReference(ref)
    if fp:
        board.RemoveNative(fp)

lib_path = r"C:\Program Files\KiCad\10.0\share\kicad\footprints\MountingHole.pretty"
fp_name = "MountingHole_3.2mm_M3_Pad"

targets = [
    {"ref": "H1", "x": 113.5, "y": 73.5, "net": "/AGND"},
    {"ref": "H2", "x": 186.5, "y": 73.5, "net": "/PGND"},
    {"ref": "H3", "x": 113.5, "y": 121.5, "net": "/AGND"},
    {"ref": "H4", "x": 186.5, "y": 121.5, "net": "/PGND"}
]

for t in targets:
    fp = pcbnew.FootprintLoad(lib_path, fp_name)
    fp.SetReference(t["ref"])
    fp.SetPosition(pcbnew.VECTOR2I(pcbnew.FromMM(t["x"]), pcbnew.FromMM(t["y"])))
    
    # Strip courtyards
    items_to_remove = []
    for item in fp.GraphicalItems():
        layer_name = board.GetLayerName(item.GetLayer())
        if "Courtyard" in layer_name:
            items_to_remove.append(item)
    for item in items_to_remove:
        fp.Remove(item)
        
    netcode = board.GetNetcodeFromNetname(t["net"])
    for pad in fp.Pads():
        pad.SetSize(pcbnew.VECTOR2I(pcbnew.FromMM(5.0), pcbnew.FromMM(5.0)))
        if netcode > 0:
            pad.SetNetCode(netcode)
            
    board.Add(fp)

print("Refilling zones...")
filler = pcbnew.ZONE_FILLER(board)
filler.Fill(board.Zones())

print("Saving board...")
pcbnew.SaveBoard(pcb_path, board)
print("Done.")

