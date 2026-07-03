import pcbnew
import sys
board = pcbnew.LoadBoard(r"C:\Users\GIRTEC\Claude\Projects\Jaguar MX\kicad\PCB\PCBv6.kicad_pcb")
fp = board.FindFootprintByReference("H1")
print(f"H1 found: {fp}")
try:
    board.RemoveNative(fp)
    print("RemoveNative worked!")
except Exception as e:
    print(f"RemoveNative failed: {e}")
    try:
        board.DeleteNative(fp)
        print("DeleteNative worked!")
    except Exception as e2:
        print(f"DeleteNative failed: {e2}")

pcbnew.SaveBoard(r"C:\Users\GIRTEC\Claude\Projects\Jaguar MX\kicad\PCB\PCBv6.kicad_pcb", board)
