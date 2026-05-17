#!/usr/bin/env python3
"""Generate Gmsh .geo: Moscow region boundary + Serpukhov refinement point."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
MO_CSV = ROOT / "data" / "Default Dataset.csv"
SERPUKHOV_CSV = ROOT / "data" / "Default Dataset (3).csv"
OUTPUT_GEO = ROOT / "mosreg_serpukhov.geo"

LC_MO = 8.0
LC_SERPUKHOV = 0.12
REFINE_RADIUS = 28.0


def load_csv(path: Path) -> list[tuple[float, float]]:
    pts: list[tuple[float, float]] = []
    with path.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            parts = re.split(r"[;\s]+", line.replace(",", "."))
            parts = [p for p in parts if p]
            if len(parts) >= 2:
                pts.append((float(parts[0]), float(parts[1])))
    return pts


def drop_closing_duplicate(pts: list[tuple[float, float]]) -> list[tuple[float, float]]:
    if len(pts) > 1 and pts[0] == pts[-1]:
        return pts[:-1]
    return pts


def point_in_polygon(x: float, y: float, poly: list[tuple[float, float]]) -> bool:
    inside = False
    j = len(poly) - 1
    for i in range(len(poly)):
        xi, yi = poly[i]
        xj, yj = poly[j]
        if ((yi > y) != (yj > y)) and (x < (xj - xi) * (y - yi) / (yj - yi + 1e-30) + xi):
            inside = not inside
        j = i
    return inside


def write_geo(
    mo_boundary: list[tuple[float, float]],
    serpukhov: tuple[float, float],
    out_path: Path,
) -> None:
    mo_boundary = drop_closing_duplicate(mo_boundary)
    n_mo = len(mo_boundary)
    sp_id = n_mo + 1
    sx, sy = serpukhov

    lines: list[str] = [
        f"// MO boundary: {MO_CSV.name}",
        f"// Serpukhov center: {SERPUKHOV_CSV.name}",
        'SetFactory("Built-in");',
        "",
    ]

    for i, (x, y) in enumerate(mo_boundary, start=1):
        lines.append(f"Point({i}) = {{{x}, {y}, 0, {LC_MO}}};")

    lines.append(f"Point({sp_id}) = {{{sx}, {sy}, 0, {LC_SERPUKHOV}}};")
    lines.append("")

    for i in range(1, n_mo):
        lines.append(f"Line({i}) = {{{i}, {i + 1}}};")
    lines.append(f"Line({n_mo}) = {{{n_mo}, 1}};")
    lines.append("")

    curve_tags = ", ".join(str(i) for i in range(1, n_mo + 1))
    lines += [
        f"Curve Loop(1) = {{{curve_tags}}};",
        "Plane Surface(1) = {1};",
        f"Point{{{sp_id}}} In Surface {{1}};",
        "",
        "Field[1] = Distance;",
        f"Field[1].PointsList = {{{sp_id}}};",
        "Field[2] = Threshold;",
        "Field[2].InField = 1;",
        f"Field[2].SizeMin = {LC_SERPUKHOV};",
        f"Field[2].SizeMax = {LC_MO};",
        "Field[2].DistMin = 0;",
        f"Field[2].DistMax = {REFINE_RADIUS};",
        "Field[2].Sigmoid = 1;",
        "Background Field = 2;",
        "",
        "Mesh.Algorithm = 6;",
        "Mesh.Smoothing = 5;",
        "Mesh.Optimize = 1;",
        "",
    ]

    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    mo = load_csv(MO_CSV)
    sp_list = load_csv(SERPUKHOV_CSV)
    if not sp_list:
        raise SystemExit(f"No points in {SERPUKHOV_CSV}")
    serpukhov = sp_list[0]
    if len(sp_list) > 1:
        print(f"Warning: using first of {len(sp_list)} Serpukhov points")

    mo_boundary = drop_closing_duplicate(mo)
    if not point_in_polygon(serpukhov[0], serpukhov[1], mo_boundary):
        print("Warning: Serpukhov point may be outside MO boundary")

    write_geo(mo, serpukhov, OUTPUT_GEO)
    print(f"Wrote {OUTPUT_GEO}")
    print(f"Moscow region boundary: {len(mo_boundary)} points")
    print(f"Serpukhov: ({serpukhov[0]:.4f}, {serpukhov[1]:.4f})")


if __name__ == "__main__":
    main()
