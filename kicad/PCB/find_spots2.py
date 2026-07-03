import pcbnew

pcb_path = r"C:\Users\GIRTEC\Claude\Projects\Jaguar MX\kicad\PCB\PCBv6.kicad_pcb"
board = pcbnew.LoadBoard(pcb_path)

def get_clear_spots(min_x, max_x, min_y, max_y, hole_radius_with_clearance=3.65):
    bboxes = []
    for fp in board.GetFootprints():
        if fp.GetReference() not in ["H1", "H2", "H3", "H4"]:
            bboxes.append(fp.GetBoundingBox())
            
    best_spots = []
    for x_mm in range(int(min_x*10), int(max_x*10)):
        for y_mm in range(int(min_y*10), int(max_y*10)):
            x = x_mm / 10.0
            y = y_mm / 10.0
            
            hole_w = pcbnew.FromMM(hole_radius_with_clearance * 2)
            hole_bb = pcbnew.BOX2I(pcbnew.VECTOR2I(int(pcbnew.FromMM(x) - hole_w//2), int(pcbnew.FromMM(y) - hole_w//2)), 
                                      pcbnew.VECTOR2I(int(hole_w), int(hole_w)))
            
            ok = True
            for bb in bboxes:
                if hole_bb.Intersects(bb):
                    ok = False
                    break
            if ok:
                best_spots.append((x, y))
    return best_spots

print("TL safe spots:", get_clear_spots(113.65, 120, 73.65, 80)[:10])
print("TR safe spots:", get_clear_spots(180, 186.35, 73.65, 80)[-10:])
print("BL safe spots:", get_clear_spots(113.65, 120, 115, 121.35)[-10:])
print("BR safe spots:", get_clear_spots(180, 186.35, 115, 121.35)[-10:])

