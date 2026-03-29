"""
Geometry Primitives Library
Core 3D building blocks for Marshal Golf product generation.
All units in millimeters.
"""

import numpy as np
from stl import mesh
import math


def cyl(radius, height, segments=48, cx=0, cy=0, cz=0):
    """Solid cylinder with top and bottom caps."""
    angles = np.linspace(0, 2 * np.pi, segments, endpoint=False)
    data = np.zeros(segments * 4, dtype=mesh.Mesh.dtype)
    idx = 0
    for j in range(segments):
        a1, a2 = angles[j], angles[(j + 1) % segments]
        x1, y1 = cx + radius * np.cos(a1), cy + radius * np.sin(a1)
        x2, y2 = cx + radius * np.cos(a2), cy + radius * np.sin(a2)
        # Side wall
        data['vectors'][idx] = [[x1, y1, cz], [x2, y2, cz], [x2, y2, cz + height]]
        idx += 1
        data['vectors'][idx] = [[x1, y1, cz], [x2, y2, cz + height], [x1, y1, cz + height]]
        idx += 1
        # Top cap
        data['vectors'][idx] = [[cx, cy, cz + height], [x1, y1, cz + height], [x2, y2, cz + height]]
        idx += 1
        # Bottom cap
        data['vectors'][idx] = [[cx, cy, cz], [x2, y2, cz], [x1, y1, cz]]
        idx += 1
    return mesh.Mesh(data)


def ring(outer_r, inner_r, height, segments=48, cx=0, cy=0, cz=0):
    """Hollow ring / annulus with outer wall, inner wall, top face, and bottom face."""
    angles = np.linspace(0, 2 * np.pi, segments, endpoint=False)
    data = np.zeros(segments * 8, dtype=mesh.Mesh.dtype)
    idx = 0
    for j in range(segments):
        a1, a2 = angles[j], angles[(j + 1) % segments]
        ox1, oy1 = cx + outer_r * np.cos(a1), cy + outer_r * np.sin(a1)
        ox2, oy2 = cx + outer_r * np.cos(a2), cy + outer_r * np.sin(a2)
        ix1, iy1 = cx + inner_r * np.cos(a1), cy + inner_r * np.sin(a1)
        ix2, iy2 = cx + inner_r * np.cos(a2), cy + inner_r * np.sin(a2)
        # Outer wall
        data['vectors'][idx] = [[ox1, oy1, cz], [ox2, oy2, cz], [ox2, oy2, cz + height]]
        idx += 1
        data['vectors'][idx] = [[ox1, oy1, cz], [ox2, oy2, cz + height], [ox1, oy1, cz + height]]
        idx += 1
        # Inner wall (reversed normals)
        data['vectors'][idx] = [[ix2, iy2, cz], [ix1, iy1, cz], [ix1, iy1, cz + height]]
        idx += 1
        data['vectors'][idx] = [[ix2, iy2, cz], [ix1, iy1, cz + height], [ix2, iy2, cz + height]]
        idx += 1
        # Top annular face
        data['vectors'][idx] = [[ix1, iy1, cz + height], [ox1, oy1, cz + height], [ox2, oy2, cz + height]]
        idx += 1
        data['vectors'][idx] = [[ix1, iy1, cz + height], [ox2, oy2, cz + height], [ix2, iy2, cz + height]]
        idx += 1
        # Bottom annular face
        data['vectors'][idx] = [[ox1, oy1, cz], [ix1, iy1, cz], [ix2, iy2, cz]]
        idx += 1
        data['vectors'][idx] = [[ox1, oy1, cz], [ix2, iy2, cz], [ox2, oy2, cz]]
        idx += 1
    return mesh.Mesh(data)


def box(width, depth, height, cx=0, cy=0, cz=0):
    """Axis-aligned box centered on cx, cy with bottom at cz."""
    hw, hd = width / 2, depth / 2
    v = np.array([
        [cx - hw, cy - hd, cz],
        [cx + hw, cy - hd, cz],
        [cx + hw, cy + hd, cz],
        [cx - hw, cy + hd, cz],
        [cx - hw, cy - hd, cz + height],
        [cx + hw, cy - hd, cz + height],
        [cx + hw, cy + hd, cz + height],
        [cx - hw, cy + hd, cz + height],
    ])
    faces = [
        [0, 3, 1], [1, 3, 2],   # bottom
        [4, 5, 7], [5, 6, 7],   # top
        [0, 1, 5], [0, 5, 4],   # front
        [2, 3, 7], [2, 7, 6],   # back
        [1, 2, 6], [1, 6, 5],   # right
        [0, 4, 7], [0, 7, 3],   # left
    ]
    data = np.zeros(12, dtype=mesh.Mesh.dtype)
    for k, f in enumerate(faces):
        data['vectors'][k] = v[f]
    return mesh.Mesh(data)


def frustum(r_bottom, r_top, height, segments=48, cx=0, cy=0, cz=0):
    """Tapered cylinder (cone frustum) with caps."""
    angles = np.linspace(0, 2 * np.pi, segments, endpoint=False)
    data = np.zeros(segments * 4, dtype=mesh.Mesh.dtype)
    idx = 0
    for j in range(segments):
        a1, a2 = angles[j], angles[(j + 1) % segments]
        bx1 = cx + r_bottom * np.cos(a1)
        by1 = cy + r_bottom * np.sin(a1)
        bx2 = cx + r_bottom * np.cos(a2)
        by2 = cy + r_bottom * np.sin(a2)
        tx1 = cx + r_top * np.cos(a1)
        ty1 = cy + r_top * np.sin(a1)
        tx2 = cx + r_top * np.cos(a2)
        ty2 = cy + r_top * np.sin(a2)
        # Side wall
        data['vectors'][idx] = [[bx1, by1, cz], [bx2, by2, cz], [tx2, ty2, cz + height]]
        idx += 1
        data['vectors'][idx] = [[bx1, by1, cz], [tx2, ty2, cz + height], [tx1, ty1, cz + height]]
        idx += 1
        # Top cap
        data['vectors'][idx] = [[cx, cy, cz + height], [tx1, ty1, cz + height], [tx2, ty2, cz + height]]
        idx += 1
        # Bottom cap
        data['vectors'][idx] = [[cx, cy, cz], [bx2, by2, cz], [bx1, by1, cz]]
        idx += 1
    return mesh.Mesh(data)


def organic_dome(radius, height, rings=12, segments=48, cx=0, cy=0, cz=0):
    """Smooth dome surface (quarter-sphere scaled to height)."""
    faces = []
    for ri in range(rings):
        phi1 = (ri / rings) * (math.pi / 2)
        phi2 = ((ri + 1) / rings) * (math.pi / 2)
        r1 = radius * math.cos(phi1)
        r2 = radius * math.cos(phi2)
        z1 = cz + height * math.sin(phi1)
        z2 = cz + height * math.sin(phi2)
        for si in range(segments):
            th1 = (si / segments) * 2 * math.pi
            th2 = ((si + 1) / segments) * 2 * math.pi
            p1 = [cx + r1 * math.cos(th1), cy + r1 * math.sin(th1), z1]
            p2 = [cx + r1 * math.cos(th2), cy + r1 * math.sin(th2), z1]
            p3 = [cx + r2 * math.cos(th2), cy + r2 * math.sin(th2), z2]
            p4 = [cx + r2 * math.cos(th1), cy + r2 * math.sin(th1), z2]
            faces.append([p1, p2, p3])
            faces.append([p1, p3, p4])
    data = np.zeros(len(faces), dtype=mesh.Mesh.dtype)
    for k, f in enumerate(faces):
        data['vectors'][k] = f
    return mesh.Mesh(data)


def sphere(radius, rings=16, segments=32, cx=0, cy=0, cz=0):
    """Full UV sphere."""
    faces = []
    for ri in range(rings):
        phi1 = math.pi * ri / rings - math.pi / 2
        phi2 = math.pi * (ri + 1) / rings - math.pi / 2
        for si in range(segments):
            th1 = 2 * math.pi * si / segments
            th2 = 2 * math.pi * (si + 1) / segments
            p1 = [cx + radius * math.cos(phi1) * math.cos(th1),
                  cy + radius * math.cos(phi1) * math.sin(th1),
                  cz + radius * math.sin(phi1)]
            p2 = [cx + radius * math.cos(phi1) * math.cos(th2),
                  cy + radius * math.cos(phi1) * math.sin(th2),
                  cz + radius * math.sin(phi1)]
            p3 = [cx + radius * math.cos(phi2) * math.cos(th2),
                  cy + radius * math.cos(phi2) * math.sin(th2),
                  cz + radius * math.sin(phi2)]
            p4 = [cx + radius * math.cos(phi2) * math.cos(th1),
                  cy + radius * math.cos(phi2) * math.sin(th1),
                  cz + radius * math.sin(phi2)]
            faces.append([p1, p2, p3])
            faces.append([p1, p3, p4])
    data = np.zeros(len(faces), dtype=mesh.Mesh.dtype)
    for k, f in enumerate(faces):
        data['vectors'][k] = f
    return mesh.Mesh(data)


def combine(mesh_list):
    """Combine multiple meshes into a single STL mesh."""
    mesh_list = [m for m in mesh_list if m is not None]
    if not mesh_list:
        raise ValueError("No meshes to combine")
    total_faces = sum(len(m.data) for m in mesh_list)
    combined_data = np.zeros(total_faces, dtype=mesh.Mesh.dtype)
    offset = 0
    for m in mesh_list:
        n = len(m.data)
        combined_data[offset:offset + n] = m.data
        offset += n
    return mesh.Mesh(combined_data)
