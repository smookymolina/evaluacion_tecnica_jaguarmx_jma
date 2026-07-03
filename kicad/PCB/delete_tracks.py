import pcbnew

pcb_path = r"C:\Users\GIRTEC\Claude\Projects\Jaguar MX\kicad\PCB\PCBv6.kicad_pcb"
board = pcbnew.LoadBoard(pcb_path)

print("Borrando pistas y vías...")
tracks = board.GetTracks()
# Collect items to delete
items_to_delete = []
for item in tracks:
    items_to_delete.append(item)

for item in items_to_delete:
    board.RemoveNative(item)

print("Rellenando zonas (por si acaso)...")
filler = pcbnew.ZONE_FILLER(board)
filler.Fill(board.Zones())

print("Guardando...")
pcbnew.SaveBoard(pcb_path, board)
print("Hecho.")
