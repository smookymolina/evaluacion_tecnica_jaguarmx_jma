import pcbnew
import sys

pcb_path = r"C:\Users\GIRTEC\Claude\Projects\Jaguar MX\kicad\PCB\PCBv6.kicad_pcb"
board = pcbnew.LoadBoard(pcb_path)

lib_path = r"C:\Program Files\KiCad\10.0\share\kicad\footprints\MountingHole.pretty"
fp_name = "MountingHole_3.2mm_M3_Pad"
test_fp = pcbnew.FootprintLoad(lib_path, fp_name)
board.Add(test_fp)

def check_pos(x, y):
    test_fp.SetPosition(pcbnew.VECTOR2I(pcbnew.FromMM(x), pcbnew.FromMM(y)))
    bb_hole = test_fp.GetBoundingBox()
    
    # Check board edge (110 to 190, 70 to 125)
    # The bounding box of the footprint must be fully inside the edge limits + 0.5mm clearance
    if pcbnew.ToMM(bb_hole.GetLeft()) < 110.5 or pcbnew.ToMM(bb_hole.GetRight()) > 189.5: return False
    if pcbnew.ToMM(bb_hole.GetTop()) < 70.5 or pcbnew.ToMM(bb_hole.GetBottom()) > 124.5: return False
    
    # Check courtyard overlap
    for module in board.GetFootprints():
        if module.GetReference() in ["H1", "H2", "H3", "H4"]: continue
        if module == test_fp: continue
        if test_fp.HitTest(module.GetBoundingBox()):
            return False
    return True

print("Searching TL...")
for x in range(1100, 1300):
    for y in range(700, 900):
        if check_pos(x/10.0, y/10.0):
            print(f"TL Safe: {x/10.0}, {y/10.0}")
            break
    else: continue
    break

print("Searching TR...")
for x in range(1890, 1600, -1):
    for y in range(700, 900):
        if check_pos(x/10.0, y/10.0):
            print(f"TR Safe: {x/10.0}, {y/10.0}")
            break
    else: continue
    break
