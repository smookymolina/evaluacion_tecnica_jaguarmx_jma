from __future__ import annotations

import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SRC = ROOT / 'kicad' / 'PCB' / 'PCB.kicad_pcb'
DST = ROOT / 'kicad' / 'PCB' / 'PCBv3.kicad_pcb'

PLACEMENT = {
    'U1': (140.0, 95.0, 0),
    'U2': (126.0, 82.0, 0),
    'J7': (118.5, 75.5, 90),
    'J1': (116.0, 120.0, 0),
    'J2': (126.0, 120.0, 0),
    'SW1': (139.0, 120.0, 0),
    'NT1': (150.0, 105.0, 0),
    'F1': (126.0, 92.0, 0),
    'C1': (120.0, 80.0, 90),
    'C2': (130.0, 80.0, 90),
    'C3': (120.0, 84.0, 90),
    'C4': (129.9, 84.0, 90),
    'C5': (129.0, 91.2, 90),
    'C6': (129.0, 105.2, 90),
    'C7': (158.8, 89.0, 90),
    'C8': (165.0, 89.0, 90),
    'C9': (136.0, 82.0, 0),
    'C10': (176.0, 82.0, 0),
    'C11': (178.0, 86.0, 0),
    'C12': (133.0, 108.0, 0),
    'C13': (133.0, 111.5, 0),
    'C14': (133.0, 115.0, 0),
    'C15': (116.0, 79.0, 90),
    'R1': (123.0, 88.0, 0),
    'R2': (123.0, 102.0, 0),
    'R3': (120.0, 88.0, 0),
    'R4': (120.0, 102.0, 0),
    'R5': (172.0, 95.0, 0),
    'R6': (174.0, 105.0, 0),
    'R7': (180.0, 111.0, 90),
    'R9': (129.0, 108.0, 0),
    'R10': (129.0, 111.5, 0),
    'R11': (129.0, 115.0, 0),
    'R_LED1': (120.5, 115.5, 0),
    'D1': (128.0, 88.0, 0),
    'D2': (128.0, 102.0, 0),
    'D3': (174.0, 117.0, 0),
    'Q1': (178.5, 109.0, 0),
    'U3': (165.0, 95.0, 180),
    'U4': (159.5, 111.0, 0),
    'J6': (182.0, 75.5, 90),
    'J3': (182.0, 119.0, 90),
    'J5': (170.0, 119.0, 90),
    'J9': (170.0, 75.5, 0),
    'LED1': (115.5, 115.5, 0),
    'TP1': (131.0, 72.0, 0),
    'TP2': (136.0, 72.0, 0),
    'TP3': (174.0, 82.0, 0),
    'TP4': (116.0, 82.0, 0),
    'TP5': (141.0, 72.0, 0),
    'TP6': (124.0, 85.0, 0),
    'TP7': (124.0, 105.0, 0),
    'TP8': (174.0, 114.0, 0),
}


def fmt(v: float) -> str:
    return f'{v:g}'


def iter_blocks(text: str):
    i = 0
    while True:
        start = text.find('(footprint ', i)
        if start == -1:
            yield text[i:]
            break
        yield text[i:start]
        depth = 0
        end = None
        for j in range(start, len(text)):
            ch = text[j]
            if ch == '(':
                depth += 1
            elif ch == ')':
                depth -= 1
                if depth == 0:
                    end = j + 1
                    break
        if end is None:
            raise ValueError('Unbalanced parentheses in KiCad PCB')
        yield text[start:end]
        i = end


def update_footprint(block: str) -> str:
    m = re.search(r'\(property "Reference" "([^"]+)"', block)
    if not m:
        return block
    ref = m.group(1)
    if ref not in PLACEMENT:
        return block
    x, y, rot = PLACEMENT[ref]
    at = f'(at {fmt(x)} {fmt(y)}'
    if rot:
        at += f' {fmt(rot)}'
    at += ')'
    return re.sub(r'^(\t\t)\(at\s+[^)]*\)', lambda m: f'{m.group(1)}{at}', block, count=1, flags=re.M)


def main() -> None:
    if len(PLACEMENT) != 53:
        raise ValueError(f'Expected 53 placements, got {len(PLACEMENT)}')
    shutil.copy2(SRC, DST)
    text = DST.read_text(encoding='utf-8')
    refs = set(re.findall(r'\(property "Reference" "([^"]+)"', text))
    missing = sorted(refs - set(PLACEMENT))
    extra = sorted(set(PLACEMENT) - refs)
    if missing or extra:
        raise ValueError(f'Reference mismatch. missing={missing} extra={extra}')
    out = []
    for block in iter_blocks(text):
        if block.startswith('(footprint '):
            block = update_footprint(block)
        out.append(block)
    DST.write_text(''.join(out), encoding='utf-8')
    print(f'Wrote {DST}')


if __name__ == '__main__':
    main()
