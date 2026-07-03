import pcbnew

pcb_path = r"C:\Users\GIRTEC\Claude\Projects\Jaguar MX\kicad\PCB\PCBv6.kicad_pcb"
board = pcbnew.LoadBoard(pcb_path)

print("Refilling zones...")
filler = pcbnew.ZONE_FILLER(board)
filler.Fill(board.Zones())

print("Saving board...")
pcbnew.SaveBoard(pcb_path, board)
print("Done.")

