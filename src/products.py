"""
Product Generators
High-level functions that assemble complete Marshal Golf products.
Each function returns a finished STL mesh ready to save.
All units in millimeters.
"""

import numpy as np
from stl import mesh
import math
import os

from .primitives import cyl, ring, box, frustum, combine
from .profiles import (
    extrude_profile, rounded_rect_profile,
    pennant_profile, hourglass_profile, wave_profile, tee_profile
)
from .features import (
    magnet_well, alignment_groove, chamfer_ring,
    concentric_grooves, prong_pair, prong_pair_tapered,
    MAGNET_WELL_DIAMETER, MAGNET_WELL_DEPTH
)


OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'output')


def save(m, name):
    """Save mesh to the output directory as a binary STL."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    path = os.path.join(OUTPUT_DIR, name if name.endswith('.stl') else name + '.stl')
    m.save(path)
    size_kb = os.path.getsize(path) // 1024
    verts = m.vectors[:, :, :]
    dx = verts[:, :, 0].max() - verts[:, :, 0].min()
    dy = verts[:, :, 1].max() - verts[:, :, 1].min()
    dz = verts[:, :, 2].max() - verts[:, :, 2].min()
    print(f"Saved: {path}")
    print(f"  Dimensions: {dx:.1f} x {dy:.1f} x {dz:.1f} mm")
    print(f"  Faces: {len(m.data):,}  |  Size: {size_kb} KB")
    return path


# ---------------------------------------------------------------------------
# Ball Markers
# ---------------------------------------------------------------------------

def marker_pennant(thickness=4.5):
    """
    The Pennant — triangular flag ball marker.
    Marshal Golf's signature shape. ~35 x 22mm footprint.
    Communicates 'golf' instantly without a single word.
    """
    pts = pennant_profile(width=35, height=22, taper=0.7)
    body = extrude_profile(pts, thickness)

    # Alignment groove along the center axis (horizontal, pointing toward tip)
    groove = alignment_groove(length=28, width=0.45, depth=0.2,
                               cx=0, cy=0, cz=thickness)

    # Magnet well on back face (centered)
    well = magnet_well(cx=0, cy=0, cz=0)

    # Bottom chamfer ring approximation — small disc at edges (cosmetic only)
    # In practice: apply 0.5mm chamfer in slicer

    return combine([body, groove, well])


def marker_hourglass(thickness=4.5):
    """
    The Hourglass — sand timer ball marker.
    Communicates pace-of-play. ~18 x 28mm footprint.
    Marshal Golf's most on-brand shape.
    """
    pts = hourglass_profile(width=18, height=28, waist_ratio=0.35)
    body = extrude_profile(pts, thickness)

    # Vertical alignment groove (along the hourglass axis)
    groove = alignment_groove(length=22, width=0.45, depth=0.2,
                               cx=0, cy=0, cz=thickness, angle_deg=90)

    # Magnet well centered on back
    well = magnet_well(cx=0, cy=0, cz=0)

    return combine([body, groove, well])


def marker_wave(thickness=4.0):
    """
    The Wave — organic S-curve ball marker.
    Water hazard, flow, rhythm. ~34 x 16mm footprint.
    """
    pts = wave_profile(width=34, height=12, wave_freq=1.5, wave_amp=4.0)
    body = extrude_profile(pts, thickness)

    # Horizontal alignment groove
    groove = alignment_groove(length=26, width=0.45, depth=0.2,
                               cx=0, cy=0, cz=thickness, angle_deg=0)

    # Magnet well on back
    well = magnet_well(cx=0, cy=0, cz=0)

    return combine([body, groove, well])


def marker_tee(thickness=4.5):
    """
    The Tee — golf tee profile ball marker.
    Instantly recognizable golf icon. ~18 x 24mm footprint.
    """
    pts = tee_profile(shaft_w=6, shaft_h=22, head_w=22, head_h=5)
    # Center vertically
    pts = [[p[0], p[1] - 13.5] for p in pts]
    body = extrude_profile(pts, thickness)

    # Vertical groove along shaft
    groove = alignment_groove(length=12, width=0.45, depth=0.2,
                               cx=0, cy=-3, cz=thickness, angle_deg=90)

    well = magnet_well(cx=0, cy=-2, cz=0)

    return combine([body, groove, well])


def marker_disc(diameter=30, thickness=4.0):
    """
    The Standard — classic circular disc marker.
    Premium coin feel with concentric groove texture on back.
    Regulation 30mm diameter.
    """
    body = cyl(radius=diameter / 2, height=thickness, segments=64)

    # Concentric grooves on back face (decorative + tactile)
    grooves = concentric_grooves(
        r_start=MAGNET_WELL_DIAMETER / 2 + 2,
        r_end=diameter / 2 - 3,
        spacing=2.5,
        groove_w=0.5,
        groove_d=0.25,
        segments=64,
        cz=0
    )

    # Alignment groove on top face
    groove = alignment_groove(length=22, width=0.45, depth=0.2,
                               cx=0, cy=0, cz=thickness)

    # Magnet well
    well = magnet_well(cx=0, cy=0, cz=0)

    return combine([body, grooves, groove, well])


# ---------------------------------------------------------------------------
# Divot Tools
# ---------------------------------------------------------------------------

def tool_classic(total_length=75, handle_w=14, handle_d=10, thickness=10):
    """
    The Standard — classic two-prong divot tool with sculpted handle.
    Heavy, precise, feels like a machined instrument.
    Handle: rounded rectangle cross-section. Prongs extend from one end.
    """
    prong_len = 17
    handle_len = total_length - prong_len

    # Handle body
    handle_pts = rounded_rect_profile(handle_w, handle_d, corner_radius=2.5,
                                       segments_per_corner=6)
    handle = extrude_profile(handle_pts, handle_len, z_base=0)

    # Taper neck toward prong end
    neck = frustum(
        r_bottom=handle_w / 2 * 0.8,
        r_top=handle_w / 2 * 0.55,
        height=8,
        segments=16,
        cx=0, cy=0, cz=handle_len
    )

    # Prong pair
    prongs = prong_pair_tapered(
        length=prong_len,
        base_width=2.2,
        tip_width=1.4,
        gap=6.0,
        cx=0, cy=0,
        cz=handle_len + 8
    )

    # Magnet well at cap end
    well = magnet_well(cx=0, cy=0, cz=0)

    # Concentric texture on cap face
    grooves = concentric_grooves(
        r_start=MAGNET_WELL_DIAMETER / 2 + 1.5,
        r_end=min(handle_w, handle_d) / 2 - 1.5,
        spacing=2.0,
        groove_w=0.45,
        groove_d=0.25,
        segments=48,
        cz=0
    )

    return combine([handle, neck, prongs, well, grooves])


def tool_wedge(total_length=70, width=22, thickness=3.5):
    """
    The Wedge — ultra-thin wallet-form divot tool.
    Apple-level minimalism. Fits in a card slot.
    Flat profile, split-prong at one end, magnet well at other.
    """
    # Main flat body
    pts = rounded_rect_profile(width, total_length - 17, corner_radius=3,
                                segments_per_corner=6)
    body = extrude_profile(pts, thickness, z_base=0)

    # Split prong at top end
    prongs = prong_pair(
        length=15,
        width=1.6,
        gap=5.5,
        tip_radius=0.4,
        cx=0,
        cy=(total_length - 17) / 2,
        cz=thickness
    )

    # Magnet well at bottom end
    well = magnet_well(cx=0, cy=-(total_length - 17) / 2 + 5, cz=0)

    return combine([body, prongs, well])


def tool_pennant(total_length=80):
    """
    The Pennant Tool — shaped handle matching The Pennant marker theme.
    Creates a collectible matched set. Handle is pennant-shaped.
    """
    handle_len = 55
    prong_len = 17

    # Pennant-shaped handle (smaller than the marker version)
    handle_pts = pennant_profile(width=handle_len, height=18, taper=0.6)
    # Rotate 90° to align along Y axis
    handle_pts_rotated = [[-p[1], p[0]] for p in handle_pts]
    handle = extrude_profile(handle_pts_rotated, thickness=10, z_base=0)

    # Prongs at the narrow end
    prongs = prong_pair_tapered(
        length=prong_len,
        base_width=2.0,
        tip_width=1.3,
        gap=6.0,
        cx=0, cy=handle_len / 2 + 4,
        cz=4
    )

    # Magnet well at wide end
    well = magnet_well(cx=0, cy=-handle_len / 2 + 8, cz=0)

    return combine([handle, prongs, well])


# ---------------------------------------------------------------------------
# Full Collection
# ---------------------------------------------------------------------------

def generate_authority_collection():
    """
    Generate all 5 markers of the Authority Series.
    Saves all files to the output directory.
    """
    products = [
        ('MARSHAL-MKR-AUTH-PEN-BLK', marker_pennant),
        ('MARSHAL-MKR-AUTH-HRG-BLK', marker_hourglass),
        ('MARSHAL-MKR-AUTH-WAV-BLK', marker_wave),
        ('MARSHAL-MKR-AUTH-TEE-BLK', marker_tee),
        ('MARSHAL-MKR-AUTH-STD-BLK', marker_disc),
    ]
    paths = []
    print("\n=== Generating Authority Collection — 5 Ball Markers ===\n")
    for name, fn in products:
        m = fn()
        path = save(m, name)
        paths.append(path)
        print()
    print(f"=== Collection complete. {len(paths)} files saved to ./output/ ===\n")
    return paths
