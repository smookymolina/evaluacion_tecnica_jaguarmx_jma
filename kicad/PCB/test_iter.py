import pcbnew
import sys

pcb_path = r"C:\Users\GIRTEC\Claude\Projects\Jaguar MX\kicad\PCB\PCBv6.kicad_pcb"
board = pcbnew.LoadBoard(pcb_path)

lib_path = r"C:\Program Files\KiCad\10.0\share\kicad\footprints\MountingHole.pretty"
fp_name = "MountingHole_3.2mm_M3_Pad"
fp = pcbnew.FootprintLoad(lib_path, fp_name)

try:
    for item in fp.GraphicalItems():
        print(board.GetLayerName(item.GetLayer()))
    print("Iterable!")
except Exception as e:
    print(f"Error: {e}")

