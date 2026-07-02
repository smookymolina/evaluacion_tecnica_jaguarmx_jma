# build_pcb_v2.py — Reconstruccion de layout PCB Jaguar MX (FASE4)
# Ejecutar con el Python de KiCad 10 (con KiCad CERRADO):
#   & "C:\Program Files\KiCad\10.0\bin\python.exe" build_pcb_v2.py
import pcbnew, json, os, shutil, math

DIR  = os.path.dirname(os.path.abspath(__file__))
PCB  = os.path.join(DIR, "PCB.kicad_pcb")
PRO  = os.path.join(DIR, "PCB.kicad_pro")
MM   = pcbnew.FromMM
ORGX, ORGY, BW, BH = 20.0, 20.0, 80.0, 55.0   # origen pagina; doc usa Y hacia arriba

def V(x, y):  # coords doc (Y up) -> VECTOR2I kicad
    return pcbnew.VECTOR2I(MM(ORGX + x), MM(ORGY + (BH - y)))

# ── Placement (coords doc FASE4 §2.3 + nudges anticolision) ──────────────
# Nudges: U1→x24 (libra clusters NTC), J9 (55,18)→(60,14) libra U4,
# J5 (75,10)→(73,6.5) libra Q1/D3, J7 (5,50)→(7,52) libra U2/LED1.
PLACE = {  # ref: (x, y, rot)
    # Hemisferio logico (X<40)
    "U1":(24,30,0), "U2":(10,46,0), "F1":(18,46,90), "LED1":(3,50,0), "R_LED":(3,46.5,90),
    "J7":(7,52,0), "J1":(4,37,0), "J2":(4,23,0),
    "C1":(6,42.5,0), "C3":(8.5,42.5,0), "C2":(13,42.5,0), "C4":(15.5,42.5,0),
    "R1":(10,36,0), "R3":(13,36,0), "D1":(16,36,0), "C5":(16,33,0), "TP6":(10,39,0),
    "R2":(10,24,0), "R4":(13,24,0), "D2":(16,24,0), "C6":(16,27,0), "TP7":(10,21,0),
    "SW1":(10,12,0), "R9":(17,14,90), "R10":(17,11,90), "R11":(17,8,90),
    "C12":(20,14,90), "C13":(20,11,90), "C14":(20,8,90),
    "C9":(34,40,0), "C15":(30,45,0),
    "TP1":(26,52,0), "TP2":(29,52,0), "TP3":(32,52,0), "TP4":(35,52,0),
    "TP5":(38,52,0), "TP8":(26,49,0),
    # Frontera
    "NT1":(40,15,0),
    # Hemisferio potencia (X>40)
    "U3":(55,35,0), "C7":(50,29.5,0), "C8":(53.5,29.5,0),
    "U4":(50,21,0), "R5":(57,24,90), "J9":(60,14,0),
    "J3":(46,6.5,0),
    "Q1":(70,24,90), "R6":(65.5,22,0), "R7":(67.5,18,90), "D3":(67,13,0),
    "J5":(73,6.5,0), "J6":(74,48,180), "C10":(70,41,0), "C11":(74,41.5,0),
}

board = pcbnew.LoadBoard(PCB)
shutil.copy(PCB, PCB.replace(".kicad_pcb", "_backup_v1.kicad_pcb"))

# ── 1. Limpiar zonas/pistas/contorno previos ──────────────────────────────
# v10.0.4: listar TODO antes de borrar y usar Delete() (Remove() corrompe SWIG)
_zl = list(board.Zones())
_tl = list(board.Tracks().iterator())
_dl = [d for d in board.Drawings().iterator() if d.GetLayer() == pcbnew.Edge_Cuts]
for it in _zl + _tl + _dl: board.Delete(it)

# ── 2. Contorno 80x55, esquinas R2 ────────────────────────────────────────
def seg(p1, p2):
    s = pcbnew.PCB_SHAPE(board); s.SetShape(pcbnew.SHAPE_T_SEGMENT)
    s.SetStart(p1); s.SetEnd(p2); s.SetLayer(pcbnew.Edge_Cuts); s.SetWidth(MM(0.1))
    board.Add(s)
def arc(p1, pm, p2):
    s = pcbnew.PCB_SHAPE(board); s.SetShape(pcbnew.SHAPE_T_ARC)
    s.SetArcGeometry(p1, pm, p2); s.SetLayer(pcbnew.Edge_Cuts); s.SetWidth(MM(0.1))
    board.Add(s)
R, k = 2.0, 2.0 * (1 - math.sqrt(0.5))  # sagita 45deg
seg(V(R,0), V(BW-R,0));  seg(V(R,BH), V(BW-R,BH))
seg(V(0,R), V(0,BH-R));  seg(V(BW,R), V(BW,BH-R))
arc(V(0,R),    V(k,k),       V(R,0))       # inf-izq
arc(V(BW-R,0), V(BW-k,k),    V(BW,R))      # inf-der
arc(V(BW,BH-R),V(BW-k,BH-k), V(BW-R,BH))   # sup-der
arc(V(R,BH),   V(k,BH-k),    V(0,BH-R))    # sup-izq

# ── 3. Posicionar componentes ─────────────────────────────────────────────
for ref, (x, y, rot) in PLACE.items():
    fp = board.FindFootprintByReference(ref)
    if not fp: print("WARN: no existe", ref); continue
    fp.SetPosition(V(x, y)); fp.SetOrientationDegrees(rot)

def net(name):
    n = board.FindNet(name)
    if not n: print("WARN: net no encontrada", name)
    return n

# ── 4. Zonas AGND / PGND (F.Cu + B.Cu), pour termico Q1, keepouts ────────
def zone(netname, layer, pts, prio=1, thermal=True, minw=0.25):
    z = pcbnew.ZONE(board); z.SetLayer(layer)
    n = net(netname)
    if n: z.SetNetCode(n.GetNetCode())
    o = z.Outline(); o.NewOutline()
    for (x, y) in pts:
        p = V(x, y); o.Append(p.x, p.y)
    z.SetAssignedPriority(prio); z.SetMinThickness(MM(minw))
    try: z.SetPadConnection(pcbnew.ZONE_CONNECTION_THERMAL if thermal
                            else pcbnew.ZONE_CONNECTION_FULL)
    except AttributeError: pass
    z.SetThermalReliefSpokeWidth(MM(0.5)); z.SetThermalReliefGap(MM(0.3))
    board.Add(z); return z

def rect(x1, y1, x2, y2): return [(x1,y1),(x2,y1),(x2,y2),(x1,y2)]

for lay in (pcbnew.F_Cu, pcbnew.B_Cu):
    zone("/AGND", lay, rect(0, 0, 39.5, BH))
    zone("/PGND", lay, rect(40.5, 0, BW, BH), minw=0.3)

# Pour termico bajo tab de Q1 (12x8mm, conexion solida, prio 2)
QTX, QTY = 73.0, 24.0  # centro del pour (tab hacia X=80)
for lay in (pcbnew.F_Cu, pcbnew.B_Cu):
    zone("/PGND", lay, rect(QTX-6, QTY-4, QTX+6, QTY+4), prio=2, thermal=False)

# Keepout X=39..41 (sin pistas/vias) con canal Y=14..16 para NT1
def keepout(pts):
    z = pcbnew.ZONE(board); z.SetIsRuleArea(True)
    z.SetLayer(pcbnew.F_Cu)
    try:
        ls = pcbnew.LSET(); ls.AddLayer(pcbnew.F_Cu); ls.AddLayer(pcbnew.B_Cu)
        z.SetLayerSet(ls)
    except Exception: pass
    z.SetDoNotAllowTracks(True); z.SetDoNotAllowVias(True)
    for m in ("SetDoNotAllowZoneFills", "SetDoNotAllowCopperPour"):
        if hasattr(z, m): getattr(z, m)(False); break
    z.SetDoNotAllowPads(False); z.SetDoNotAllowFootprints(False)
    o = z.Outline(); o.NewOutline()
    for (x, y) in pts:
        p = V(x, y); o.Append(p.x, p.y)
    board.Add(z)
keepout(rect(39, 0, 41, 14))
keepout(rect(39, 16, 41, BH))

# ── 5. Vias: helper compatible v8/v10 ─────────────────────────────────────
def via(x, y, netname, drill, pad):
    v = pcbnew.PCB_VIA(board); v.SetPosition(V(x, y))
    v.SetViaType(pcbnew.VIATYPE_THROUGH)
    v.SetLayerPair(pcbnew.F_Cu, pcbnew.B_Cu)
    v.SetDrill(MM(drill))
    try: v.SetWidth(MM(pad))
    except TypeError: v.SetWidth(pcbnew.PADSTACK.ALL_LAYERS, MM(pad))
    n = net(netname)
    if n: v.SetNetCode(n.GetNetCode())
    board.Add(v)

# Array termico bajo Q1: grilla 1.2mm dentro del pour 12x8
xn = QTX - 6 + 0.9
while xn < QTX + 6 - 0.5:
    yn = QTY - 4 + 0.9
    while yn < QTY + 4 - 0.5:
        via(xn, yn, "/PGND", 0.4, 0.8)
        yn += 1.2
    xn += 1.2

# Stitching: evita bbox de footprints (inflado 1mm)
def bboxes():
    bl = []
    for fp in board.GetFootprints():
        try: bb = fp.GetBoundingBox(False)
        except TypeError: bb = fp.GetBoundingBox()
        bb.Inflate(MM(1.0)); bl.append(bb)
    return bl
BBS = bboxes()
def libre(x, y):
    p = V(x, y)
    return not any(bb.Contains(p) for bb in BBS)

y = 2.5
while y < BH:                       # AGND grilla 5mm, via 0.3/0.7
    x = 2.5
    while x < 38.0:
        if libre(x, y): via(x, y, "/AGND", 0.3, 0.7)
        x += 5.0
    y += 5.0
y = 2.0
while y < BH:                       # PGND grilla 3mm, via 0.6/1.0
    x = 42.5
    while x < BW - 1.0:
        if libre(x, y) and not (QTX-7 < x < QTX+7 and QTY-5 < y < QTY+5):
            via(x, y, "/PGND", 0.6, 1.0)
        x += 3.0
    y += 3.0

# ── 6. Ruteado inicial (cadena greedy por net, ruta en L, F.Cu) ──────────
def pads_of(netname):
    return [pad for fp in board.GetFootprints() for pad in fp.Pads()
            if pad.GetNetname() == netname]

def track(p1, p2, n, w):
    if p1 == p2: return
    t = pcbnew.PCB_TRACK(board); t.SetStart(p1); t.SetEnd(p2)
    t.SetWidth(MM(w)); t.SetLayer(pcbnew.F_Cu); t.SetNetCode(n.GetNetCode())
    board.Add(t)

def route_net(netname, w, l_shape=True):
    n = net(netname)
    if not n: return
    pads = pads_of(netname)
    if len(pads) < 2: return
    rest = sorted(pads, key=lambda p: p.GetPosition().x)
    cur, chain = rest.pop(0), []
    while rest:  # vecino mas cercano
        rest.sort(key=lambda p: (p.GetPosition() - cur.GetPosition()).EuclideanNorm())
        chain.append((cur, rest[0])); cur = rest.pop(0)
    for a, b in chain:
        pa, pb = a.GetPosition(), b.GetPosition()
        if l_shape and pa.x != pb.x and pa.y != pb.y:
            mid = pcbnew.VECTOR2I(pb.x, pa.y)
            track(pa, mid, n, w); track(mid, pb, n, w)
        else:
            track(pa, pb, n, w)

# Celula 48V primero (lazo corto), luego motor, riel, analogico, gate
route_net("/+48V",              1.5)   # J6 -> C10 -> C11 -> J5.1
route_net("/NET_FAN_HS",        1.5)   # J5.2 -> D3 -> Q1.Drain
route_net("/+5V",               1.5)
route_net("/NET_AO1",           1.0)
route_net("/NET_AO2",           1.0)
route_net("/+3V3",              0.4)
route_net("/NET_TEMP_INT_FILT", 0.2, l_shape=False)  # <10mm, recto, sin vias
route_net("/NET_TEMP_EXT_FILT", 0.2, l_shape=False)
route_net("/NET_Q1_GATE",       0.2)
route_net("/NET_VENT_GATE",     0.2)

# ── 7. Constraints globales + relleno + guardar ──────────────────────────
ds = board.GetDesignSettings()
ds.m_MinClearance       = MM(0.15)
ds.m_TrackMinWidth      = MM(0.2)
ds.m_CopperEdgeClearance = MM(0.3)

pcbnew.ZONE_FILLER(board).Fill(board.Zones())
pcbnew.SaveBoard(PCB, board)
print("OK: PCB reconstruido y guardado (backup en PCB_backup_v1.kicad_pcb)")

# ── 8. Netclasses en .kicad_pro ───────────────────────────────────────────
CLASSES = [
    dict(name="Power_48V",   clearance=0.6,  track_width=1.5, via_diameter=1.4, via_drill=0.8),
    dict(name="Power_5V",    clearance=0.3,  track_width=1.5, via_diameter=1.0, via_drill=0.6),
    dict(name="Motor_AO",    clearance=0.3,  track_width=1.0, via_diameter=1.0, via_drill=0.6),
    dict(name="Signal_3V3",  clearance=0.15, track_width=0.4, via_diameter=0.8, via_drill=0.4),
    dict(name="Signal_Logic",clearance=0.15, track_width=0.2, via_diameter=0.7, via_drill=0.3),
]
ASSIGN = {
    "Power_48V":  ["/+48V", "/NET_FAN_HS"],
    "Power_5V":   ["/+5V", "/PGND"],
    "Motor_AO":   ["/NET_AO1", "/NET_AO2"],
    "Signal_3V3": ["/+3V3", "/NET_3V3_LDO"],
    "Signal_Logic": ["/AGND", "/NET_SW1", "/NET_SW2", "/NET_SW3",
        "/NET_TEMP_INT_DIV", "/NET_TEMP_INT_FILT", "/NET_TEMP_EXT_DIV",
        "/NET_TEMP_EXT_FILT", "/NET_AIN1", "/NET_AIN2", "/NET_MOTOR_EN",
        "/NET_VENT", "/NET_VENT_GATE", "/NET_VENT_DRV", "/NET_STBY",
        "/NET_Q1_GATE", "/NET_LED_ANODE"],
}
BASE = dict(bus_width=12, wire_width=6, line_style=0, diff_pair_gap=0.25,
            diff_pair_via_gap=0.25, diff_pair_width=0.2,
            microvia_diameter=0.3, microvia_drill=0.1,
            pcb_color="rgba(0, 0, 0, 0.000)", schematic_color="rgba(0, 0, 0, 0.000)")
with open(PRO, "r", encoding="utf-8") as f: pro = json.load(f)
ns = pro.setdefault("net_settings", {})
ns["classes"] = [dict(BASE, **c) for c in CLASSES]
ns["netclass_patterns"] = [{"netclass": k, "pattern": p}
                           for k, v in ASSIGN.items() for p in v]
with open(PRO, "w", encoding="utf-8") as f: json.dump(pro, f, indent=2)
print("OK: netclasses escritas en PCB.kicad_pro")
