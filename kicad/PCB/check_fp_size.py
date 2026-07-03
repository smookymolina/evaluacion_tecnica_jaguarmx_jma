import pcbnew
board = pcbnew.LoadBoard(r"C:\Users\GIRTEC\Claude\Projects\Jaguar MX\kicad\PCB\PCBv6.kicad_pcb")
fp = pcbnew.FootprintLoad(r"C:\Program Files\KiCad\10.0\share\kicad\footprints\MountingHole.pretty", "MountingHole_3.2mm_M3_Pad")
print(f"MountingHole_3.2mm_M3_Pad:")
for p in fp.Pads():
    print(f" Pad {p.GetName()} size {pcbnew.ToMM(p.GetSize().x)}x{pcbnew.ToMM(p.GetSize().y)} drill {pcbnew.ToMM(p.GetDrillSize().x)}")

fp2 = pcbnew.FootprintLoad(r"C:\Program Files\KiCad\10.0\share\kicad\footprints\MountingHole.pretty", "MountingHole_3.2mm_M3_ISO7380_Pad")
print(f"MountingHole_3.2mm_M3_ISO7380_Pad:")
if fp2:
    for p in fp2.Pads():
        print(f" Pad {p.GetName()} size {pcbnew.ToMM(p.GetSize().x)}x{pcbnew.ToMM(p.GetSize().y)} drill {pcbnew.ToMM(p.GetDrillSize().x)}")
