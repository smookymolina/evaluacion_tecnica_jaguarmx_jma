# Tutorial: tu PRIMER ruteo — Paso 3 (potencia) en KiCad 10

> Guía para alguien que nunca ha ruteado. Vamos despacio. No puedes "romper" nada: todo es reversible con `Ctrl+Z`.

---

## 0. Conceptos en 30 segundos

- Una **pista** (track) es un camino de cobre que conecta dos pads.
- Las **líneas blancas finas** que ves entre pads se llaman **ratsnest**: son las conexiones que *faltan* por hacer. Tu trabajo es convertir cada línea blanca en una pista de cobre. Cuando la haces, la línea blanca desaparece.
- Hay **2 caras de cobre**: `F.Cu` (arriba, roja) y `B.Cu` (abajo, verde). En el Paso 3 casi todo va en **F.Cu (rojo)**.
- Los **planos de tierra** (las rejillas que ya vertimos) se rellenan solos alrededor de tus pistas.

---

## 1. Abre el PCB y prepárate (una sola vez)

1. Abre **KiCad** → tu proyecto → doble clic en **PCB.kicad_pcb** (o el ícono "Editor de PCB").
2. **Navegación básica:**
   - Rueda del ratón = zoom (hacia donde apunta el cursor).
   - Rueda presionada + arrastrar = mover la vista (pan).
   - `Inicio`/`Home` = ver toda la placa.
3. **Anchos de pista predefinidos** (para elegir el grosor fácil):
   - Menú **Archivo → Configuración de la placa… → Reglas de diseño → Tamaños predefinidos**.
   - En "Pistas", agrega estos anchos (botón `+`): **1.5**, **1.0**, **0.8**, **0.4**, **0.2** mm. Acepta.
4. **Modo del router (importante para principiantes):**
   - **Preferencias → Editor de PCB → Router interactivo**.
   - En "Modo", elige **"Rodear obstáculos" (Walk around)**. Así el router esquiva pads automáticamente en vez de dejarte chocar. Acepta.

---

## 2. Cómo se usa el router (lee esto una vez)

| Acción | Tecla / clic |
|---|---|
| **Empezar** una pista | Pon el cursor sobre un pad y pulsa **`X`** (o icono "Rutear pistas") |
| Poner un **codo** (esquina) | **clic izquierdo** en el punto |
| **Terminar** la pista en un pad | doble clic sobre el pad destino (o clic y luego `Esc`) |
| **Deshacer** el último tramo mientras ruteas | **`Backspace`** |
| **Cambiar el ancho** | **`W`** (cicla los anchos que definiste) — míralo abajo a la izquierda |
| **Cambiar de cara** (pone una vía) | **`V`** (salta de F.Cu a B.Cu) |
| **Cancelar** la pista actual | **`Esc`** |
| **Borrar** una pista hecha | clic para seleccionarla + **`Supr`** |
| **Deshacer todo** | **`Ctrl+Z`** |
| **Rellenar** zonas de tierra | **`B`** |

**Regla de oro del principiante:** ve **de pad a pad siguiendo la línea blanca (ratsnest)**. Si el router se pone rojo o no te deja, pulsa `Esc` e inténtalo con un camino un poco distinto (haz un codo para rodear).

Selecciona la cara activa arriba, en la lista de capas: haz clic en **F.Cu** para que sea la capa roja.

---

## 3. Mapa del hemisferio de potencia (dónde está cada cosa)

Mira la mitad **derecha** de la placa. De arriba-derecha hacia abajo:

```
             (arriba)
   C10  C11  ── J6   ← entrada 48V (esquina sup-derecha)
   TP3            
        U3 (chip grande, centro)   Q1 (MOSFET, cuadro grande)
   R5                              R6 R7
        U4      J9                 D3   ← diodo flyback
   J3 ─────────────────────  J5   ← conectores abajo
             (abajo)
```

- **J6** = entrada 48V (2 pads gruesos, arriba-derecha).
- **C10/C11** = condensadores 48V (a la izquierda de J6). **TP3** = punto de prueba entre ellos.
- **Q1** = MOSFET (cuadro grande con 3 patas, derecha-centro).
- **D3** = diodo flyback (abajo-derecha, junto a J5).
- **J5** = ventilador (abajo-derecha). **J3** = actuador (abajo-centro).
- **U3** = TB6612 (chip de muchas patas, centro).

---

## 4. Rutea las 5 redes (orden fácil → difícil)

> Consejo: haz **una red, rellena (`B`) y respira**. No intentes todo de un tirón.

### 4.1 🟢 NET_FAN_HS — calentamiento (ancho 1.5 mm, F.Cu)
Conecta el MOSFET → diodo → ventilador. 3 pads, zona abierta y pads grandes: ideal para empezar.
1. Selecciona capa **F.Cu**. Pulsa `W` hasta que el ancho sea **1.5**.
2. Cursor sobre **Q1** pata central (`Q1.2`, la del medio del MOSFET) → **`X`**.
3. Sigue la línea blanca hasta **D3** (pad `D3.2`, el lado del diodo que mira a Q1). Haz 1-2 clics para ir en L (primero horizontal o vertical, luego gira). Doble clic en D3.2 para terminar.
4. Otra vez `X` sobre **D3.2** → sigue el ratsnest hasta **J5** pad `J5.2` (ventilador). Doble clic para terminar.
5. ✅ Las 2 líneas blancas de FAN_HS desaparecieron. Pulsa `B` para rellenar.

### 4.2 🟢 NET_AO1 y NET_AO2 — aprende el "strap" (ancho 1.0 mm)
Estos van del chip U3 al conector del actuador J3. Cada uno tiene **dos pads juntos en el chip** (hay que unirlos con un puente corto = *strap*).
1. Ancho `W` → **1.0**. Capa **F.Cu**.
2. **Strap AO1:** cursor sobre `U3.1` → `X` → clic corto hasta `U3.2` (el pad de al lado, 0.65 mm). Doble clic. *(Si el router se queja por ser muy ancho aquí, baja a 0.4 con `W` solo para este puentecito.)*
3. **Bajada a J3:** `X` sobre `U3.1` → sal **hacia la izquierda** (aléjate del chip 1 mm) → baja recto → llega a `J3.1` (pad del conector, abajo-centro). Doble clic.
4. Repite igual para **AO2**: strap `U3.5`↔`U3.6`, luego bajada de `U3.5` a `J3.2`. Mantén esta pista **paralela** a la de AO1, sin tocarla.
5. `B` para rellenar.

> **Truco para salir de un chip:** siempre sal del pad *perpendicular a la fila de patas* (aquí, hacia la izquierda), avanza ~1 mm, y **ahí** empieza a girar. Nunca cruces por delante de las otras patas.

### 4.3 🟡 +48V — el lazo de potencia (ancho 1.5 mm, F.Cu)
Es la entrada de 48V. Va: **J6 → C11 → C10 → D3 → J5**, más el punto de prueba TP3. Pistas cortas y rectas (evita zigzags).
1. Ancho `W` → **1.5**. Capa **F.Cu**.
2. `X` en `J6.1` (pad de entrada +48V) → sube/baja recto a `C11.1`. Doble clic.
3. `X` en `C11.1` → a `TP3.1` (el punto de prueba, muy cerca). Doble clic.
4. `X` en `C11.1` → a `C10.1`. **Ojo:** cada condensador tiene un pad +48V y otro PGND (tierra) al lado. Conecta **solo el pad +48V** (el que marca la línea blanca). Si te acercas al de tierra, el router se pone rojo → haz un codo para rodear.
5. `X` en `C10.1` → baja recto hasta `D3.1` (pad +48V del diodo, abajo). Pasa entre Q1 y J9 con un codo si hace falta.
6. `X` en `D3.1` → a `J5.1` (pad +48V del ventilador). Doble clic.
7. `B` para rellenar. Verifica que ya no queden líneas blancas de +48V.

### 4.4 🟡 +5V — el más largo (ancho 1.0 mm)
Alimenta el LDO, el chip U3 y el driver U4. Tiene ~14 tramos pero son cortos. Ve por bloques siguiendo el ratsnest:
- **Bloque LDO (izquierda):** `J7.1` → `U2.1` → `U2.3`; y `C1.1`/`C3.2` hacia `U2.3` (condensadores de entrada).
- **Cruce al centro:** de `J7.1`/`TP2.1` → `C15.1` → cruza a `C7.1`/`C8.1` (junto a U3). Este tramo **cruza la frontera** por F.Cu: hazlo perpendicular y directo.
- **Pines de U3:** `C8.1` → `U3.13`, strap `U3.13`↔`U3.14`, y `U3.24`. Usa la técnica de salir perpendicular del chip.
- **Driver U4:** `U4.8`→`U4.7`→`U4.5` (3 pads en fila del mismo lado). Straps cortos.
- `B` para rellenar.

> Si un tramo de +5V no cabe por arriba (F.Cu), puedes bajarlo a **B.Cu**: mientras ruteas, pulsa `V` (pone una vía y cambia de cara), avanza por abajo, y pulsa `V` otra vez para volver a subir cerca del destino.

---

## 5. Cierre del Paso 3

1. Pulsa **`B`** (rellenar todas las zonas).
2. **Inspecciona → Ejecutar DRC** (o el icono de la mariquita 🐞). Objetivo: que las redes de potencia ya **no** aparezcan en "elementos no conectados". Ignora por ahora los avisos de *silkscreen*.
3. Guarda con **`Ctrl+S`**.

Cuando termines, dime y validamos juntos con el DRC de línea de comandos (o pásame el archivo y lo reviso). Luego seguimos con el **Paso 4** (analógico NTC + control).

---

### Si algo sale mal
- **No me deja terminar la pista / todo rojo:** `Esc`, y prueba otro camino con un codo para rodear el obstáculo.
- **Ancho equivocado:** selecciona la pista + `Supr`, y rehazla con el `W` correcto.
- **Borré algo por error:** `Ctrl+Z`.
- **Se ven islas de cobre raras:** pulsa `B` para rerellenar las zonas.
