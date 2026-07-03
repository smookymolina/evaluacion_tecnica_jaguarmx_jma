import pcbnew

pcb_path = r"C:\Users\GIRTEC\Claude\Projects\Jaguar MX\kicad\PCB\PCBv6.kicad_pcb"
board = pcbnew.LoadBoard(pcb_path)

def find_first_spot(min_x, max_x, min_y, max_y, step=0.1, hole_radius=3.5):
    bboxes = []
    for fp in board.GetFootprints():
        if fp.GetReference() not in ["H1", "H2", "H3", "H4"]:
            bboxes.append(fp.GetBoundingBox())
            
    x = min_x
    while x <= max_x:
        y = min_y
        while y <= max_y:
            hole_w = pcbnew.FromMM(hole_radius * 2)
            hole_bb = pcbnew.BOX2I(pcbnew.VECTOR2I(int(pcbnew.FromMM(x) - hole_w//2), int(pcbnew.FromMM(y) - hole_w//2)), 
                                      pcbnew.VECTOR2I(int(hole_w), int(hole_w)))
            
            ok = True
            for bb in bboxes:
                if hole_bb.Intersects(bb):
                    ok = False
                    break
            if ok:
                return (x, y)
            y += step
        x += step
    return None

print("TL safe:", find_first_spot(113.8, 125, 73.8, 85))
print("TR safe:", find_first_spot(175, 186.2, 73.8, 85))
print("BL safe:", find_first_spot(113.8, 125, 110, 121.2))
print("BR safe:", find_first_spot(175, 186.2, 110, 121.2))

