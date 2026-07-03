import pcbnew

try:
    fp = pcbnew.FootprintLoad(r"C:\Program Files\KiCad\10.0\share\kicad\footprints\MountingHole.pretty", "MountingHole_3.2mm_M3_Pad")
    if fp:
        print("Success loading MountingHole_3.2mm_M3_Pad")
except Exception as e:
    print(f"Error: {e}")
