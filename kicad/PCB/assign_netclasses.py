import pcbnew

pcb_path = r"C:\Users\GIRTEC\Claude\Projects\Jaguar MX\kicad\PCB\PCBv6.kicad_pcb"
board = pcbnew.LoadBoard(pcb_path)
ds = board.GetDesignSettings()
net_classes = ds.GetNetClasses()

# Create and add Power_48V
nc_48v = pcbnew.NETCLASS("Power_48V")
nc_48v.SetTrackWidth(int(pcbnew.FromMM(1.5)))
nc_48v.SetViaDiameter(int(pcbnew.FromMM(1.4)))
nc_48v.SetViaDrill(int(pcbnew.FromMM(0.8)))
net_classes.Add(nc_48v)

# Create and add Power_5V
nc_5v = pcbnew.NETCLASS("Power_5V")
nc_5v.SetTrackWidth(int(pcbnew.FromMM(1.0)))
nc_5v.SetViaDiameter(int(pcbnew.FromMM(1.0)))
nc_5v.SetViaDrill(int(pcbnew.FromMM(0.6)))
net_classes.Add(nc_5v)

# Create and add Signal_3V3
nc_3v3 = pcbnew.NETCLASS("Signal_3V3")
nc_3v3.SetTrackWidth(int(pcbnew.FromMM(0.4)))
nc_3v3.SetViaDiameter(int(pcbnew.FromMM(0.6)))
nc_3v3.SetViaDrill(int(pcbnew.FromMM(0.3)))
net_classes.Add(nc_3v3)

# Assign nets to these classes
netinfo = board.GetNetInfo()
for netname in netinfo.NetsByName():
    if netname in ['+48V', '/NET_FAN_HS']:
        netinfo.GetNetItem(netname).SetClassName("Power_48V")
    elif netname in ['+5V', '/NET_AO1', '/NET_AO2']:
        netinfo.GetNetItem(netname).SetClassName("Power_5V")
    elif netname in ['+3V3', '/NET_3V3_LDO']:
        netinfo.GetNetItem(netname).SetClassName("Signal_3V3")

print("Saving board...")
pcbnew.SaveBoard(pcb_path, board)
print("Done.")
