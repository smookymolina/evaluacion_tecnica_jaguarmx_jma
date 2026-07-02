import os
import time

sch_path = r"C:\Users\GIRTEC\Claude\Projects\Jaguar MX\kicad\PCB\PCB.kicad_sch"
mtime = os.path.getmtime(sch_path)
print(f"Modification time: {time.ctime(mtime)}")
print(f"File size: {os.path.getsize(sch_path)} bytes")
