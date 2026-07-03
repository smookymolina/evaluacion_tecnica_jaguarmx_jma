import pcbnew
board = pcbnew.LoadBoard(r"C:\Users\GIRTEC\Claude\Projects\Jaguar MX\kicad\PCB\PCBv6.kicad_pcb")

# Find H1
fp = board.FindFootprintByReference("H1")
print(dir(board))
print("---")
print(dir(fp))
