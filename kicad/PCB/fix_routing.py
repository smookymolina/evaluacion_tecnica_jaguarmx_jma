import pcbnew

pcb_path = r"C:\Users\GIRTEC\Claude\Projects\Jaguar MX\kicad\PCB\PCBv6.kicad_pcb"
board = pcbnew.LoadBoard(pcb_path)

print("Fixing track widths and vias...")
for item in board.GetTracks():
    netname = item.GetNetname()
    if isinstance(item, pcbnew.PCB_VIA):
        if netname in ['/NET_FAN_HS', '+48V']:
            item.SetWidth(int(pcbnew.FromMM(1.4)))
            item.SetDrill(int(pcbnew.FromMM(0.8)))
    elif isinstance(item, pcbnew.PCB_TRACK):
        if netname in ['/NET_FAN_HS', '+48V']:
            if item.GetWidth() < pcbnew.FromMM(1.5):
                item.SetWidth(int(pcbnew.FromMM(1.5)))
        elif netname in ['+5V', '/NET_AO1', '/NET_AO2']:
            if item.GetWidth() < pcbnew.FromMM(1.0):
                item.SetWidth(int(pcbnew.FromMM(1.0)))
        elif netname in ['+3V3']:
            if item.GetWidth() < pcbnew.FromMM(0.4):
                item.SetWidth(int(pcbnew.FromMM(0.4)))

print("Refilling zones...")
filler = pcbnew.ZONE_FILLER(board)
filler.Fill(board.Zones())

print("Saving board...")
pcbnew.SaveBoard(pcb_path, board)
print("Done.")

