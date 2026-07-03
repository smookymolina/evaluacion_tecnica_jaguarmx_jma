import pcbnew
board = pcbnew.LoadBoard(r"C:\Users\GIRTEC\Claude\Projects\Jaguar MX\kicad\PCB\PCBv6.kicad_pcb")

# Find a mounting hole footprint or just load it from standard lib
try:
    lib_path = "MountingHole" # This is a logical name, pcbnew.FootprintLoad requires library table or direct path.
    # Usually we can add a footprint via PCB_IO or plugin
    pass
except Exception as e:
    print(e)
