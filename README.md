# SVT-3-4 — Александров (Серпухов)

## Задание 3 (Gmsh)

- `build_mosreg_geo.py` — генерация `mosreg_serpukhov.geo` из CSV в `data/`
- `mosreg_serpukhov.msh` — треугольная сетка Московской области со сгущением к Серпухову
- `screenshot.png` — вид сетки и радиус-векторов

```bash
python3 build_mosreg_geo.py
# Gmsh: открыть mosreg_serpukhov.geo → Mesh → 2D → Export .msh / .vtk
```

## Задание 4 (INMOST)

- `mesh.cpp` — тег `RadiusNormal` на узлах (радиус-вектор от точки Серпухова)

Сборка: репозиторий [INMOST_Practicum_2026](https://github.com/denis-anuprienko/INMOST_Practicum_2026), `cmake` + INMOST.

```bash
./mesh mosreg_serpukhov.vtk mosreg_with_vectors.vtu
```

Визуализация: ParaView → Glyph → `RadiusNormal`.
