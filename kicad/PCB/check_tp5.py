import pcbnew
board = pcbnew.LoadBoard(r"C:\Users\GIRTEC\Claude\Projects\Jaguar MX\kicad\PCB\PCBv6.kicad_pcb")
tp5 = board.FindFootprintByReference("TP5")
if tp5:
    for pad in tp5.Pads():
        print(f"TP5 Pad {pad.GetName()} size: {pcbnew.ToMM(pad.GetSize().x)}x{pcbnew.ToMM(pad.GetSize().y)}")
J1 = board.FindFootprintByReference("J1")
if J1:
    print(f"J1 Bbox: {pcbnew.ToMM(J1.GetBoundingBox().GetWidth())}x{pcbnew.ToMM(J1.GetBoundingBox().GetHeight())}")
