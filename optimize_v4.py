# optimize_v4.py — Placement PCB v4 Jaguar MX (para ruteo manual)
# Copia PCB.kicad_pcb -> PCBv4.kicad_pcb y actualiza SOLO el (at X Y ROT) de cada footprint.
# SUPOSICION CONSERVADORA: todas las rotaciones se mantienen identicas a las originales
# (asi no hay que reescribir angulos de pads); solo cambian posiciones X/Y.
# Estrategia: logica/analogica a la izquierda (X<149), potencia a la derecha (X>151),
# NT1 en X=150 como frontera AGND/PGND. Conectores de senal/5V al borde izquierdo,
# conectores de potencia (48V in, fan, motor) al borde derecho. Desacoplos <5mm de su IC.

import re, shutil, sys, math

SRC = r"C:\Users\GIRTEC\Claude\Projects\Jaguar MX\kicad\PCB\PCB.kicad_pcb"
DST = r"C:\Users\GIRTEC\Claude\Projects\Jaguar MX\kicad\PCB\PCBv4.kicad_pcb"

# ref -> (x, y, rot)  [rot = rotacion ORIGINAL, sin cambios]
PLACEMENT = {
    # --- LOGICA / ANALOGICA (X<149) ---
    # Entrada 5V y rail 3V3 (fila superior izquierda, flujo J7->C1/C3->U2->C4/C2->F1->3V3)
    "J7":  (115.5, 78.0, -90), "TP2": (121.0, 73.5, 0),
    "C1":  (122.7, 77.2, -90), "C3": (125.3, 77.2, 90),
    "U2":  (128.7, 77.2, 0),   "C4": (132.1, 77.2, -90),
    "C2":  (134.7, 77.2, 90),  "F1": (139.5, 77.2, 0),
    "TP1": (145.5, 77.2, 0),   "TP5": (145.5, 73.0, 0),
    # MCU XIAO RP2350 centrado en bloque logico, C9 pegado a su fila izquierda
    "U1":  (138.0, 95.0, 0),   "C9": (127.4, 90.5, -90),
    # Cadena NTC interna: J1 -> R1/R3 -> C5 + D1 -> U1 (TP6 accesible)
    "J1":  (114.5, 89.5, 0),   "R1": (121.8, 87.5, 0),  "R3": (122.5, 90.0, 0),
    "C5":  (125.3, 90.0, 0),   "D1": (125.5, 84.0, 0),  "TP6": (121.0, 94.0, 0),
    # Cadena NTC externa: J2 -> R2/R4 -> C6 + D2 -> U1 (TP7 accesible)
    "J2":  (114.5, 98.5, 0),   "R2": (121.8, 97.0, 0),  "R4": (121.8, 99.5, 0),
    "C6":  (124.8, 99.5, 90),  "D2": (125.0, 103.0, 90), "TP7": (120.0, 104.5, 0),
    # LED de estado bajo U1
    "LED1": (134.0, 107.5, 180), "R_LED1": (138.5, 107.5, 0),
    # Selector 3 posiciones + pullups/filtros en fila hacia U1
    "SW1": (114.0, 112.0, 0),
    "R9":  (126.0, 110.0, -90), "C12": (129.0, 110.0, 0),
    "R10": (126.0, 112.5, 180), "C13": (129.0, 112.5, 0),
    "R11": (126.0, 115.0, 90),  "C14": (129.0, 115.0, 0),
    # --- FRONTERA ---
    "NT1": (150.0, 105.0, 0),
    # --- POTENCIA (X>151) ---
    # Borde derecho: J5 fan out (48V), J6 48V in, J3 motor out
    "J5":  (183.5, 76.5, 90), "J6": (183.5, 86.5, 90), "J3": (183.5, 96.5, 90),
    # Seccion 48V: D3 flyback junto a J5, C10/C11 bulk junto a J6
    "D3":  (176.0, 74.5, 90), "C10": (170.0, 80.0, 90), "C11": (176.5, 82.0, -90),
    "TP3": (168.0, 74.5, 0),
    # TB6612 cerca de NT1 (recibe control de U1), salidas AO hacia J3
    "U3":  (157.5, 89.0, 0),  "C7": (154.5, 81.5, 90), "C8": (158.5, 82.5, 180),
    "R5":  (151.8, 95.5, -90),
    # Driver auxiliar DIP-8 + selector J9 entre U4 y Q1
    "U4":  (155.0, 99.0, 0),  "C15": (152.3, 99.5, -90), "J9": (167.0, 97.5, 0),
    # MOSFET TO-220 con red de gate a su izquierda
    "Q1":  (172.5, 106.0, 0), "R6": (165.5, 107.5, 0), "R7": (165.5, 110.0, 180),
    "TP8": (161.5, 111.5, 0), "TP4": (183.0, 111.0, 0),
}

# Bboxes de respaldo (half-width, half-height) para footprints sin courtyard
FALLBACK = {"TP": (1.3, 1.3), "C10": (3.5, 3.5), "NT1": (1.0, 0.5)}

BOARD = (110.5, 70.4, 190.5, 125.4)
MARGIN = 0.5


def footprint_blocks(src):
    for m in re.finditer(r'\(footprint\s+"[^"]+"', src):
        depth, i = 0, m.start()
        while i < len(src):
            if src[i] == '(':
                depth += 1
            elif src[i] == ')':
                depth -= 1
                if depth == 0:
                    break
            i += 1
        yield m.start(), i + 1


def get_ref(block):
    return re.search(r'\(property\s+"Reference"\s+"([^"]+)"', block).group(1)


def courtyard_bbox(block):
    xs, ys = [], []
    for lm in re.finditer(r'\((?:fp_line|fp_rect)\b', block):
        depth, i = 0, lm.start()
        while i < len(block):
            if block[i] == '(':
                depth += 1
            elif block[i] == ')':
                depth -= 1
                if depth == 0:
                    break
            i += 1
        seg = block[lm.start():i + 1]
        if 'CrtYd' not in seg:
            continue
        for x, y in re.findall(r'\((?:start|end)\s+([-\d.]+)\s+([-\d.]+)\)', seg):
            xs.append(float(x)); ys.append(float(y))
    if xs:
        return min(xs), min(ys), max(xs), max(ys)
    return None


def rotate_bbox(bb, rot):
    x0, y0, x1, y1 = bb
    th = math.radians(rot)
    c, s = round(math.cos(th)), round(math.sin(th))
    pts = [(dx * c + dy * s, -dx * s + dy * c)
           for dx in (x0, x1) for dy in (y0, y1)]
    xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
    return min(xs), min(ys), max(xs), max(ys)


def main():
    src = open(SRC, encoding="utf-8").read()

    # Paso 1: recolectar bloques, refs, rotaciones y courtyards originales
    info = {}
    for a, b in footprint_blocks(src):
        block = src[a:b]
        ref = get_ref(block)
        at = re.search(r'\(at\s+([-\d.]+)\s+([-\d.]+)(?:\s+([-\d.]+))?\)', block)
        rot = float(at.group(3) or 0)
        info[ref] = {"span": (a, b), "rot": rot, "crtyd": courtyard_bbox(block)}

    refs = set(info)
    assert len(refs) == 53, f"esperaba 53 footprints, hay {len(refs)}"
    missing = refs - set(PLACEMENT)
    extra = set(PLACEMENT) - refs
    assert not missing and not extra, f"faltan {missing}, sobran {extra}"

    # Paso 2: verificar que ninguna rotacion cambia (suposicion del script)
    for ref, (x, y, rot) in PLACEMENT.items():
        assert info[ref]["rot"] == rot, f"{ref}: rot {rot} != original {info[ref]['rot']}"

    # Paso 3: reescribir solo el primer (at ...) de cada footprint
    out, pos = [], 0
    for a, b in footprint_blocks(src):
        block = src[a:b]
        ref = get_ref(block)
        x, y, rot = PLACEMENT[ref]
        rot_txt = "" if rot == 0 else f" {rot:g}"
        new_block = re.sub(r'\(at\s+[-\d.]+\s+[-\d.]+(?:\s+[-\d.]+)?\)',
                           f'(at {x:g} {y:g}{rot_txt})', block, count=1)
        out.append(src[pos:a]); out.append(new_block); pos = b
    out.append(src[pos:])
    result = "".join(out)

    # Paso 4: autoverificacion sobre la salida
    errors = []
    boxes = {}
    for ref, (x, y, rot) in PLACEMENT.items():
        bb = info[ref]["crtyd"]
        if bb is None:
            hw, hh = FALLBACK["TP" if ref.startswith("TP") else ref]
            bb = (-hw, -hh, hw, hh)
        rx0, ry0, rx1, ry1 = rotate_bbox(bb, rot)
        boxes[ref] = (x + rx0, y + ry0, x + rx1, y + ry1)

    # NT1 y lados
    if PLACEMENT["NT1"][0] != 150.0:
        errors.append("NT1 fuera de X=150")
    for ref, (x, y, _) in PLACEMENT.items():
        if ref == "NT1":
            continue
        logic = ref in {"J7","TP2","C1","C3","U2","C4","C2","F1","TP1","TP5","U1","C9",
                        "J1","R1","R3","C5","D1","TP6","J2","R2","R4","C6","D2","TP7",
                        "LED1","R_LED1","SW1","R9","C12","R10","C13","R11","C14"}
        if logic and x >= 149:
            errors.append(f"{ref}: X={x} deberia ser <149")
        if not logic and x <= 151:
            errors.append(f"{ref}: X={x} deberia ser >151")

    # Bordes de tarjeta
    for ref, (x0, y0, x1, y1) in boxes.items():
        if x0 < BOARD[0] or y0 < BOARD[1] or x1 > BOARD[2] or y1 > BOARD[3]:
            errors.append(f"{ref}: courtyard fuera de tarjeta {boxes[ref]}")

    # Overlaps con margen 0.5 mm
    items = sorted(boxes.items())
    for i in range(len(items)):
        for j in range(i + 1, len(items)):
            (r1, a1), (r2, a2) = items[i], items[j]
            if (a1[0] - MARGIN / 2 < a2[2] + MARGIN / 2 and a2[0] - MARGIN / 2 < a1[2] + MARGIN / 2 and
                    a1[1] - MARGIN / 2 < a2[3] + MARGIN / 2 and a2[1] - MARGIN / 2 < a1[3] + MARGIN / 2):
                errors.append(f"overlap/margen<0.5: {r1} vs {r2}")

    if errors:
        print("FALLOS DE VERIFICACION:")
        for e in errors:
            print(" -", e)
        sys.exit(1)

    shutil.copy2(SRC, DST)  # conserva metadata; luego sobreescribimos contenido
    open(DST, "w", encoding="utf-8", newline="\n").write(result)
    print(f"OK: 53 footprints recolocados -> {DST}")
    print("Verificado: lados logico/potencia, NT1 en X=150, bordes y courtyards sin overlap (margen 0.5 mm).")


if __name__ == "__main__":
    main()
