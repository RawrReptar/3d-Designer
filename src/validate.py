"""
STL Validation
Checks geometry and dimensions before export.
Based on the Quality Validation Checklist from the Marshal Golf skill reference.
"""

import os
import numpy as np
from stl import mesh


# ---------------------------------------------------------------------------
# Dimension specs
# ---------------------------------------------------------------------------

SPECS = {
    'marker': {
        'max_xy': 40,        # longest dimension in mm
        'min_xy': 25,
        'max_z': 8,          # thickness including raised features/grooves (body target: 4-5mm)
        'min_z': 2,
        'max_faces_warn': 50_000,
        'min_faces_warn': 200,
    },
    'tool': {
        'max_length': 100,
        'min_length': 35,     # compact coin/wedge tools can be shorter
        'max_width': 22,
        'min_width': 10,
        'max_faces_warn': 200_000,
        'min_faces_warn': 500,
    },
}


def validate_stl(filepath, product_type='marker', verbose=True):
    """
    Validate an STL file against Marshal Golf quality standards.

    filepath:     path to .stl file
    product_type: 'marker' or 'tool'
    verbose:      print results to console

    Returns a dict with all measurements and a list of warnings.
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"STL file not found: {filepath}")

    m = mesh.Mesh.from_file(filepath)

    # --- Dimensions ---
    x_vals = m.vectors[:, :, 0]
    y_vals = m.vectors[:, :, 1]
    z_vals = m.vectors[:, :, 2]

    x_min, x_max = float(x_vals.min()), float(x_vals.max())
    y_min, y_max = float(y_vals.min()), float(y_vals.max())
    z_min, z_max = float(z_vals.min()), float(z_vals.max())

    dx = x_max - x_min
    dy = y_max - y_min
    dz = z_max - z_min
    longest = max(dx, dy, dz) if product_type == 'tool' else max(dx, dy)

    # --- Face count ---
    n_faces = len(m.data)

    # --- Degenerate triangles (zero area) ---
    degenerate = 0
    for i in range(n_faces):
        v = m.vectors[i]
        edge1 = v[1] - v[0]
        edge2 = v[2] - v[0]
        cross = np.cross(edge1, edge2)
        area = np.linalg.norm(cross) / 2
        if area < 1e-10:
            degenerate += 1

    # --- File size ---
    file_size_kb = os.path.getsize(filepath) // 1024

    # --- Warnings ---
    warnings = []
    spec = SPECS.get(product_type, SPECS['marker'])

    if product_type == 'marker':
        if longest > spec['max_xy']:
            warnings.append(f"Longest dimension {longest:.1f}mm exceeds max {spec['max_xy']}mm")
        if longest < spec['min_xy']:
            warnings.append(f"Longest dimension {longest:.1f}mm is below min {spec['min_xy']}mm")
        if dz > spec['max_z']:
            warnings.append(f"Thickness {dz:.1f}mm exceeds max {spec['max_z']}mm (body only)")
        if dz < spec['min_z']:
            warnings.append(f"Thickness {dz:.1f}mm is below min {spec['min_z']}mm")

    elif product_type == 'tool':
        if longest > spec['max_length']:
            warnings.append(f"Length {longest:.1f}mm exceeds max {spec['max_length']}mm")
        if longest < spec['min_length']:
            warnings.append(f"Length {longest:.1f}mm is below min {spec['min_length']}mm")

    if n_faces < spec['min_faces_warn']:
        warnings.append(f"Low face count ({n_faces}) — may look faceted")
    if n_faces > spec['max_faces_warn']:
        warnings.append(f"High face count ({n_faces}) — consider decimating for slicers")
    if degenerate > 0:
        warnings.append(f"{degenerate} degenerate (zero-area) triangles found")
    if file_size_kb > 10_000:
        warnings.append(f"Large file size ({file_size_kb}KB) — consider mesh simplification")

    result = {
        'filepath': filepath,
        'product_type': product_type,
        'dx': dx, 'dy': dy, 'dz': dz,
        'longest': longest,
        'x_range': (x_min, x_max),
        'y_range': (y_min, y_max),
        'z_range': (z_min, z_max),
        'n_faces': n_faces,
        'degenerate': degenerate,
        'file_size_kb': file_size_kb,
        'warnings': warnings,
        'passed': len(warnings) == 0,
    }

    if verbose:
        _print_report(result)

    return result


def _print_report(result):
    status = "PASS" if result['passed'] else "WARN"
    print(f"\n{'='*50}")
    print(f"  STL Validation Report [{status}]")
    print(f"{'='*50}")
    print(f"  File:       {os.path.basename(result['filepath'])}")
    print(f"  Type:       {result['product_type']}")
    print(f"  Dimensions: {result['dx']:.2f} x {result['dy']:.2f} x {result['dz']:.2f} mm")
    print(f"  Longest:    {result['longest']:.2f} mm")
    print(f"  Faces:      {result['n_faces']:,}")
    print(f"  File size:  {result['file_size_kb']} KB")
    if result['degenerate']:
        print(f"  Degenerate: {result['degenerate']}")
    if result['warnings']:
        print(f"\n  Warnings:")
        for w in result['warnings']:
            print(f"    ! {w}")
    else:
        print(f"\n  No issues found.")
    print(f"{'='*50}\n")
