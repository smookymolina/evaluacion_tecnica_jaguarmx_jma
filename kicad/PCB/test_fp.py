import pcbnew
import sys
import math

try:
    fp = pcbnew.FootprintLoad(r"C:\Program Files\KiCad\10.0\share\kicad\footprints\MountingHole.pretty", "MountingHole_3.2mm_M3_PadVia")
    if fp:
        bbox = fp.GetBoundingBox()
        print(f"Loaded footprint. Bounding box size: {pcbnew.ToMM(bbox.GetWidth())}mm x {pcbnew.ToMM(bbox.GetHeight())}mm")
        
        # The hole pad usually has radius. Let's see pads
        for pad in fp.Pads():
            print(f"Pad {pad.GetName()}: size {pcbnew.ToMM(pad.GetSize().x)}x{pcbnew.ToMM(pad.GetSize().y)}, hole {pcbnew.ToMM(pad.GetDrillSize().x)}")
    else:
        print("Footprint not found")
except Exception as e:
    print(f"Error: {e}")
