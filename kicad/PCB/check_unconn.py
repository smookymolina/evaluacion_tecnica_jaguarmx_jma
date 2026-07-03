import pcbnew

pcb_path = r"C:\Users\GIRTEC\Claude\Projects\Jaguar MX\kicad\PCB\PCBv6.kicad_pcb"
board = pcbnew.LoadBoard(pcb_path)
conn = board.GetConnectivity()
conn.Build(board)

unconn_agnd = 0
unconn_pgnd = 0
total_unconn_edges = conn.GetUnconnectedEdges()

unrouted_pads = set()

print(f"Total unconnected edges: {len(total_unconn_edges)}")

for edge in total_unconn_edges:
    item1 = edge.GetSourceItem()
    item2 = edge.GetTargetItem()
    net = item1.GetNetname()
    if net == '/AGND':
        unconn_agnd += 1
    elif net == '/PGND':
        unconn_pgnd += 1
    
    if isinstance(item1, pcbnew.PAD):
        unrouted_pads.add(item1.GetParent().GetReference())
    if isinstance(item2, pcbnew.PAD):
        unrouted_pads.add(item2.GetParent().GetReference())

print(f"AGND unconnected edges: {unconn_agnd}")
print(f"PGND unconnected edges: {unconn_pgnd}")
print(f"Components with unrouted pads ({len(unrouted_pads)}): {', '.join(sorted(unrouted_pads))}")
