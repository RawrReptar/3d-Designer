"""
Surface Features & Functional Elements
Adds alignment grooves, magnet wells, edge chamfers, grip textures,
raised text zones, and other functional/aesthetic features to base bodies.
All units in millimeters.
"""

import numpy as np
from stl import mesh
import math
from .primitives import cyl, ring, box, combine


# ---------------------------------------------------------------------------
# Magnet System
# ---------------------------------------------------------------------------

# Standard magnet: 6mm dia × 2mm height, N52 neodymium
MAGNET_DIAMETER = 6.0
MAGNET_HEIGHT = 2.0
MAGNET_WELL_DIAMETER = 6.15   # 0.15mm press-fit clearance
MAGNET_WELL_DEPTH = 2.15      # 0.15mm clearance
MAGNET_LIP_WIDTH = 0.5        # retaining lip width
MAGNET_LIP_HEIGHT = 0.3       # retaining lip height


def magnet_well(cx=0, cy=0, cz=0):
    """
    Creates the void geometry for a 6×2mm N52 magnet well.
    The well is a cylinder with a retaining lip at the opening.
    In practice: subtract this from the base body using your slicer or
    Boolean library. Here returned as a mesh for visualization/export.

    cx, cy: center position on the back face
    cz:     z position of the well opening (top of the well = marker back face)

    Returns the well cavity mesh (to be subtracted from base body).
    """
    # Main well cylinder (extends downward from cz)
    well = cyl(
        radius=MAGNET_WELL_DIAMETER / 2,
        height=MAGNET_WELL_DEPTH,
        segments=32,
        cx=cx, cy=cy,
        cz=cz - MAGNET_WELL_DEPTH
    )
    return well


def magnet_well_lip(cx=0, cy=0, cz=0):
    """
    Retaining lip ring at the magnet well opening.
    Prevents the magnet from sliding out during handling.
    This is ADDED to the base body (positive geometry).
    """
    outer_r = MAGNET_WELL_DIAMETER / 2 + MAGNET_LIP_WIDTH
    inner_r = MAGNET_WELL_DIAMETER / 2
    return ring(
        outer_r=outer_r,
        inner_r=inner_r,
        height=MAGNET_LIP_HEIGHT,
        segments=32,
        cx=cx, cy=cy, cz=cz
    )


# ---------------------------------------------------------------------------
# Alignment Features
# ---------------------------------------------------------------------------

def alignment_groove(length=20, width=0.45, depth=0.2, cx=0, cy=0, cz=0, angle_deg=0):
    """
    Thin engraved alignment line for putting alignment.
    Runs along the X axis by default, rotatable via angle_deg.

    length:    groove length in mm
    width:     groove width in mm (0.4-0.5 recommended)
    depth:     groove depth in mm (0.15-0.3 recommended)
    angle_deg: rotation around Z axis in degrees
    """
    hw = width / 2
    hl = length / 2
    angle = math.radians(angle_deg)
    cos_a, sin_a = math.cos(angle), math.sin(angle)

    def rot(x, y):
        return [cx + x * cos_a - y * sin_a,
                cy + x * sin_a + y * cos_a]

    # Groove as a flat box (will be subtracted in slicer)
    corners_2d = [
        rot(-hl, -hw),
        rot( hl, -hw),
        rot( hl,  hw),
        rot(-hl,  hw),
    ]
    v = np.array([
        [corners_2d[0][0], corners_2d[0][1], cz - depth],
        [corners_2d[1][0], corners_2d[1][1], cz - depth],
        [corners_2d[2][0], corners_2d[2][1], cz - depth],
        [corners_2d[3][0], corners_2d[3][1], cz - depth],
        [corners_2d[0][0], corners_2d[0][1], cz],
        [corners_2d[1][0], corners_2d[1][1], cz],
        [corners_2d[2][0], corners_2d[2][1], cz],
        [corners_2d[3][0], corners_2d[3][1], cz],
    ])
    faces = [
        [0, 1, 2], [0, 2, 3],   # bottom
        [4, 6, 5], [4, 7, 6],   # top
        [0, 4, 5], [0, 5, 1],   # front
        [2, 6, 7], [2, 7, 3],   # back
        [1, 5, 6], [1, 6, 2],   # right
        [0, 3, 7], [0, 7, 4],   # left
    ]
    data = np.zeros(12, dtype=mesh.Mesh.dtype)
    for k, f in enumerate(faces):
        data['vectors'][k] = v[f]
    return mesh.Mesh(data)


# ---------------------------------------------------------------------------
# Edge Treatments
# ---------------------------------------------------------------------------

def chamfer_ring(outer_r, chamfer_size=0.5, segments=48, cx=0, cy=0, cz=0):
    """
    Chamfer ring for circular objects — adds a 45° chamfer at the top outer edge.
    Place at the top of a cylinder to bevel the edge.

    outer_r:      radius of the cylinder
    chamfer_size: width (and height) of the chamfer in mm
    """
    inner_r = outer_r - chamfer_size
    faces = []
    angles = np.linspace(0, 2 * np.pi, segments, endpoint=False)
    for j in range(segments):
        a1, a2 = angles[j], angles[(j + 1) % segments]
        # Outer edge (at cz)
        ox1 = cx + outer_r * np.cos(a1); oy1 = cy + outer_r * np.sin(a1)
        ox2 = cx + outer_r * np.cos(a2); oy2 = cy + outer_r * np.sin(a2)
        # Inner edge (at cz + chamfer_size)
        ix1 = cx + inner_r * np.cos(a1); iy1 = cy + inner_r * np.sin(a1)
        ix2 = cx + inner_r * np.cos(a2); iy2 = cy + inner_r * np.sin(a2)
        faces.append([[ox1, oy1, cz], [ox2, oy2, cz], [ix2, iy2, cz + chamfer_size]])
        faces.append([[ox1, oy1, cz], [ix2, iy2, cz + chamfer_size], [ix1, iy1, cz + chamfer_size]])
    data = np.zeros(len(faces), dtype=mesh.Mesh.dtype)
    for k, f in enumerate(faces):
        data['vectors'][k] = f
    return mesh.Mesh(data)


# ---------------------------------------------------------------------------
# Grip Textures
# ---------------------------------------------------------------------------

def diamond_crosshatch(width, height, spacing=2.0, groove_w=0.4, groove_d=0.3,
                        cx=0, cy=0, cz=0):
    """
    Diamond crosshatch grip texture — interlocking diagonal grooves at ±45°.
    Applied to flat surfaces of tool handles.

    width, height: extent of the textured area in mm
    spacing:       distance between groove centerlines in mm
    groove_w:      width of each groove in mm
    groove_d:      depth of each groove in mm
    """
    meshes = []
    hw, hh = width / 2, height / 2
    n_grooves = int(max(width, height) / spacing) + 2

    for i in range(-n_grooves, n_grooves):
        offset = i * spacing
        # +45° diagonal groove
        grooves_45 = box(
            width=groove_w,
            depth=math.sqrt(width ** 2 + height ** 2),
            height=groove_d,
            cx=cx + offset,
            cy=cy,
            cz=cz - groove_d
        )
        # -45° diagonal groove
        grooves_n45 = box(
            width=math.sqrt(width ** 2 + height ** 2),
            depth=groove_w,
            height=groove_d,
            cx=cx,
            cy=cy + offset,
            cz=cz - groove_d
        )
        meshes.append(grooves_45)
        meshes.append(grooves_n45)

    return combine(meshes)


def concentric_grooves(r_start, r_end, spacing=2.0, groove_w=0.5, groove_d=0.3,
                        segments=64, cx=0, cy=0, cz=0):
    """
    Concentric ring grooves on a flat disc surface — like a coin or record.
    Satisfying to thumb-roll; used on coin-form divot tools and marker backs.

    r_start: inner radius of groove zone in mm
    r_end:   outer radius of groove zone in mm
    spacing: distance between groove centerlines in mm
    """
    if r_start >= r_end:
        return None
    meshes = []
    r = r_start
    while r <= r_end:
        groove = ring(
            outer_r=r + groove_w / 2,
            inner_r=max(r - groove_w / 2, 0.5),
            height=groove_d,
            segments=segments,
            cx=cx, cy=cy,
            cz=cz - groove_d
        )
        meshes.append(groove)
        r += spacing
    return combine(meshes)


def knurl_band(radius, band_height, knurl_count=24, knurl_w=1.5, knurl_d=0.4,
               cx=0, cy=0, cz=0):
    """
    Circumferential knurling band around a cylindrical handle.
    Creates the classic machined-metal grip look.

    radius:      handle radius in mm
    band_height: height of the knurled band in mm
    knurl_count: number of knurl bumps around the circumference
    knurl_w:     width of each knurl ridge in mm
    knurl_d:     protrusion height of each knurl in mm
    """
    meshes = []
    for i in range(knurl_count):
        angle = 2 * math.pi * i / knurl_count
        kx = cx + radius * math.cos(angle)
        ky = cy + radius * math.sin(angle)
        bump = cyl(
            radius=knurl_w / 2,
            height=band_height,
            segments=6,
            cx=kx, cy=ky, cz=cz
        )
        meshes.append(bump)
    return combine(meshes)


# ---------------------------------------------------------------------------
# Divot Tool Prongs
# ---------------------------------------------------------------------------

def prong_pair(length=17, width=1.8, gap=6.0, tip_radius=0.4, cx=0, cy=0, cz=0):
    """
    Standard two-prong divot tool head.
    Prongs extend in the +Z direction (print prongs pointing up for strength).

    length:     prong length in mm (15-20)
    width:      prong width in mm (1.5-2.0)
    gap:        center-to-center spacing in mm (5-7)
    tip_radius: rounded tip radius in mm (0.3-0.5)
    """
    meshes = []
    for side in [-1, 1]:
        px = cx + side * gap / 2

        # Prong shaft
        shaft = box(
            width=width,
            depth=width,
            height=length - tip_radius,
            cx=px, cy=cy, cz=cz
        )
        meshes.append(shaft)

        # Rounded tip
        tip = cyl(
            radius=width / 2,
            height=tip_radius,
            segments=16,
            cx=px, cy=cy,
            cz=cz + length - tip_radius
        )
        meshes.append(tip)

    return combine(meshes)


def prong_pair_tapered(length=17, base_width=2.2, tip_width=1.2, gap=6.0,
                        cx=0, cy=0, cz=0):
    """
    Tapered prong pair — wider at base, narrower at tip.
    More elegant profile, better strength at the base.
    """
    from .primitives import frustum
    meshes = []
    for side in [-1, 1]:
        px = cx + side * gap / 2
        prong = frustum(
            r_bottom=base_width / 2,
            r_top=tip_width / 2,
            height=length,
            segments=12,
            cx=px, cy=cy, cz=cz
        )
        meshes.append(prong)
    return combine(meshes)
