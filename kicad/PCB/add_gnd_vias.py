import pcbnew
import os

pcb_path = r"C:\Users\GIRTEC\Claude\Projects\Jaguar MX\kicad\PCB\PCBv6.kicad_pcb"
board = pcbnew.LoadBoard(pcb_path)

added_vias = 0
for pad in board.GetPads():
    netname = pad.GetNetname()
    if netname in ['/AGND', '/PGND']:
        # If it's an SMD pad on the Top layer, it needs a via to reach the Bottom GND plane
        if pad.GetAttribute() == pcbnew.PAD_ATTRIB_SMD:
            # We check if a via already exists at this position to avoid duplicates
            pos = pad.GetPosition()
            existing_via = False
            for item in board.GetTracks():
                if isinstance(item, pcbnew.PCB_VIA) and item.GetPosition() == pos:
                    existing_via = True
                    break
            
            if not existing_via:
                via = pcbnew.PCB_VIA(board)
                board.Add(via)
                via.SetPosition(pos)
                via.SetNetCode(pad.GetNetCode())
                via.SetLayerPair(pcbnew.F_Cu, pcbnew.B_Cu)
                
                if netname == '/PGND':
                    # Power GND via size
                    via.SetWidth(int(pcbnew.FromMM(1.0)))
                    via.SetDrill(int(pcbnew.FromMM(0.6)))
                else:
                    # Analog GND via size
                    via.SetWidth(int(pcbnew.FromMM(0.6)))
                    via.SetDrill(int(pcbnew.FromMM(0.3)))
                    
                added_vias += 1

print(f"Added {added_vias} vias.")

print("Refilling zones...")
filler = pcbnew.ZONE_FILLER(board)
filler.Fill(board.Zones())

pcbnew.SaveBoard(pcb_path, board)
print("Done.")
