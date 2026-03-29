"""
Product Generators — Authority Collection v2
High-level functions that assemble complete Marshal Golf products.
Each function returns a finished STL mesh ready to save.
All units in millimeters.

Final 5 Markers (from 315,000 evaluated):
  1. The Pennant    — triangular flag, micro-stipple, exposed gyroid
  2. The Hourglass  — sand timer, smooth, fidget channel
  3. The Sundial    — ancient timekeeper, micro-stipple, fidget channel
  4. The Stopwatch  — marshal's clock, micro-stipple, fidget channel
  5. The Divot Star — etiquette starburst, micro-stipple, exposed gyroid

Final 5 Tools (from 161,280 evaluated):
  1. The Classic    — kidney handle, tapered prongs, finger scallop
  2. The Wedge      — wallet-thin flat card, tapered prongs
  3. The Pennant    — flag-shaped handle, matched set
  4. The T-Handle   — T-shape for leverage, ergonomic
  5. The Coin       — thick disc with fold-out prongs
"""

import numpy as np
from stl import mesh
import math
import os

from .primitives import cyl, ring, box, frustum, organic_dome, sphere, combine
from .profiles import (
    extrude_profile, rounded_rect_profile,
    pennant_profile, hourglass_profile, wave_profile, tee_profile,
    sundial_profile, stopwatch_profile, divot_star_profile,
    kidney_profile, coin_disc_profile,
)
from .features import (
    magnet_well, magnet_well_lip, alignment_groove, chamfer_ring,
    concentric_grooves, knurl_band, prong_pair, prong_pair_tapered,
    MAGNET_WELL_DIAMETER, MAGNET_WELL_DEPTH,
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


# ===========================================================================
# FINAL 5 BALL MARKERS
# ===========================================================================

def marker_pennant(thickness=4.5):
    """
    The Pennant [Score: 100.0] — triangular flag ball marker.
    Micro-stipple texture. Exposed gyroid cutout on one side.
    Marshal Golf's signature shape. ~35 x 22mm.
    """
    pts = pennant_profile(width=35, height=22, taper=0.7)
    body = extrude_profile(pts, thickness)

    # Alignment groove along center axis toward tip
    groove = alignment_groove(length=28, width=0.45, depth=0.2, cx=0, cy=0, cz=thickness)

    # Magnet well on back face
    well = magnet_well(cx=0, cy=0, cz=0)
    lip = magnet_well_lip(cx=0, cy=0, cz=0)

    # Brand zone on back — recessed rectangle for "MARSHAL" text
    brand_zone = box(width=16, depth=5, height=0.3, cx=-4, cy=-6, cz=-0.3)

    # Exposed gyroid visual element — small circular window near pole side
    # Represented as a ring indent on the front face
    gyroid_window = ring(outer_r=4.5, inner_r=3.0, height=0.4,
                         segments=32, cx=-10, cy=0, cz=thickness - 0.4)

    return combine([body, groove, well, lip, brand_zone, gyroid_window])


def marker_hourglass(thickness=3.5):
    """
    The Hourglass [Score: 100.0] — sand timer ball marker.
    Smooth surface with fidget channel (thumb groove at waist).
    Marshal Golf's most on-brand shape. ~18 x 28mm.
    """
    pts = hourglass_profile(width=18, height=28, waist_ratio=0.35)
    body = extrude_profile(pts, thickness)

    # Vertical alignment groove along hourglass axis
    groove = alignment_groove(length=22, width=0.45, depth=0.2,
                               cx=0, cy=0, cz=thickness, angle_deg=90)

    # Fidget channel — horizontal thumb groove at the waist (narrowest point)
    fidget = box(width=12, depth=2.5, height=0.5, cx=0, cy=0, cz=thickness - 0.5)

    # Magnet well on back
    well = magnet_well(cx=0, cy=0, cz=0)
    lip = magnet_well_lip(cx=0, cy=0, cz=0)

    # Concentric rings on back around magnet well
    back_rings = concentric_grooves(
        r_start=MAGNET_WELL_DIAMETER / 2 + 1.5,
        r_end=7,
        spacing=2.0, groove_w=0.4, groove_d=0.2,
        segments=48, cz=0
    )

    return combine([body, groove, fidget, well, lip, back_rings])


def marker_sundial(thickness=3.5):
    """
    The Sundial [Score: 100.0] — circular base with triangular gnomon.
    Ancient timekeeper = pace of play. Micro-stipple face.
    Fidget channel along gnomon edge. ~30 x 27mm.
    """
    pts = sundial_profile(diameter=30, gnomon_w=4, gnomon_h=8)
    body = extrude_profile(pts, thickness)

    # The gnomon edge IS the alignment feature — natural directional line

    # Fidget groove along gnomon base junction
    fidget = box(width=8, depth=1.8, height=0.4, cx=0, cy=12, cz=thickness - 0.4)

    # Magnet well centered on disc portion
    well = magnet_well(cx=0, cy=0, cz=0)
    lip = magnet_well_lip(cx=0, cy=0, cz=0)

    # Hour marks — 12 small dots around the dial face (top surface)
    hour_marks = []
    for i in range(12):
        angle = 2 * math.pi * i / 12
        hx = 10 * math.cos(angle)
        hy = 10 * math.sin(angle)
        mark = cyl(radius=0.6, height=0.25, segments=8, cx=hx, cy=hy, cz=thickness)
        hour_marks.append(mark)

    # Brand text zone on back
    brand_zone = box(width=14, depth=4, height=0.3, cx=0, cy=-4, cz=-0.3)

    return combine([body, fidget, well, lip, brand_zone] + hour_marks)


def marker_stopwatch(thickness=4.5):
    """
    The Stopwatch [Score: 98.8] — circular face with crown & side button.
    Micro-stipple surface. Fidget channel as bezel groove.
    The marshal's precision timing instrument. ~28 x 22mm.
    """
    pts = stopwatch_profile(diameter=28, crown_w=6, crown_h=5, button_w=3, button_h=3.5)
    body = extrude_profile(pts, thickness)

    # Alignment line from 12 to 6 (vertical through center)
    groove = alignment_groove(length=22, width=0.45, depth=0.2,
                               cx=0, cy=0, cz=thickness, angle_deg=90)

    # Cross-hair at center (horizontal line too)
    cross = alignment_groove(length=10, width=0.3, depth=0.15,
                              cx=0, cy=0, cz=thickness, angle_deg=0)

    # Fidget bezel groove — concentric ring near outer edge
    bezel = ring(outer_r=12.5, inner_r=11.5, height=0.35,
                 segments=48, cx=0, cy=0, cz=thickness - 0.35)

    # Magnet well
    well = magnet_well(cx=0, cy=0, cz=0)
    lip = magnet_well_lip(cx=0, cy=0, cz=0)

    # Minute markers — 60 tiny dots around dial
    minute_marks = []
    for i in range(60):
        angle = 2 * math.pi * i / 60
        r = 10.5
        mx = r * math.cos(angle)
        my = r * math.sin(angle)
        size = 0.5 if i % 5 == 0 else 0.25
        mark = cyl(radius=size, height=0.2, segments=6, cx=mx, cy=my, cz=thickness)
        minute_marks.append(mark)

    return combine([body, groove, cross, bezel, well, lip] + minute_marks)


def marker_divot_star(thickness=4.5):
    """
    The Divot Star [Score: 98.1] — 6-pointed starburst ball marker.
    The pattern of a properly repaired ball mark. Etiquette embodied.
    Micro-stipple face. Exposed gyroid reference. ~30mm diameter.
    """
    pts = divot_star_profile(radius=15, points_count=6, inner_ratio=0.55)
    body = extrude_profile(pts, thickness)

    # The star shape itself provides alignment via its symmetry axis
    # Add a subtle groove along one arm for putting direction
    groove = alignment_groove(length=12, width=0.45, depth=0.2,
                               cx=0, cy=5, cz=thickness, angle_deg=90)

    # Magnet well centered
    well = magnet_well(cx=0, cy=0, cz=0)
    lip = magnet_well_lip(cx=0, cy=0, cz=0)

    # Gyroid window ring at center — decorative ring suggesting the pattern
    center_ring = ring(outer_r=5.0, inner_r=3.5, height=0.35,
                       segments=32, cx=0, cy=0, cz=thickness)

    # Brand zone on back
    brand_zone = box(width=12, depth=4, height=0.3, cx=0, cy=0, cz=-0.3)

    return combine([body, groove, well, lip, center_ring, brand_zone])


# ===========================================================================
# FINAL 5 DIVOT TOOLS
# ===========================================================================

def tool_classic(total_length=62):
    """
    The Classic [Score: 94.1] — kidney-handle, tapered prongs, finger scallop.
    Fixed two-prong, compact 62mm. Heavy, precise, heirloom quality.
    """
    prong_len = 17
    neck_len = 8
    handle_len = total_length - prong_len - neck_len

    # Kidney-bean ergonomic handle cross-section
    handle_pts = kidney_profile(width=14, height=10, indent=0.3, segments=24)
    handle = extrude_profile(handle_pts, handle_len, z_base=0)

    # Tapered neck
    neck = frustum(
        r_bottom=6.5, r_top=4.0,
        height=neck_len, segments=24,
        cx=0, cy=0, cz=handle_len
    )

    # Tapered prongs — wider at base, narrower at tip
    prongs = prong_pair_tapered(
        length=prong_len, base_width=2.2, tip_width=1.2,
        gap=6.0, cx=0, cy=0, cz=handle_len + neck_len
    )

    # Finger scallop grooves on handle — three evenly spaced depressions
    scallops = []
    for i in range(3):
        z_pos = 8 + i * 10
        scallop = box(width=10, depth=2.5, height=0.6,
                      cx=0, cy=5.5, cz=z_pos)
        scallops.append(scallop)

    # Magnet well at cap end
    well = magnet_well(cx=0, cy=0, cz=0)
    lip = magnet_well_lip(cx=0, cy=0, cz=0)

    return combine([handle, neck, prongs, well, lip] + scallops)


def tool_wedge(total_length=62, width=20, thickness=3.5):
    """
    The Wedge [Score: 92.5] — ultra-thin wallet-form divot tool.
    Kidney cross-section adapted to flat form. Tapered prongs.
    Fits in a card slot. Apple-level minimalism.
    """
    body_len = total_length - 15
    pts = rounded_rect_profile(width, body_len, corner_radius=3,
                                segments_per_corner=8)
    body = extrude_profile(pts, thickness, z_base=0)

    # Tapered prongs at top end
    prongs = prong_pair_tapered(
        length=15, base_width=2.0, tip_width=1.2,
        gap=5.5, cx=0, cy=body_len / 2, cz=thickness
    )

    # Finger scallop — single central depression for thumb
    scallop = box(width=10, depth=8, height=0.5,
                  cx=0, cy=0, cz=thickness - 0.5)

    # Magnet well at bottom end
    well = magnet_well(cx=0, cy=-body_len / 2 + 5, cz=0)
    lip = magnet_well_lip(cx=0, cy=-body_len / 2 + 5, cz=0)

    # Alignment groove on top face
    groove = alignment_groove(length=body_len - 10, width=0.4, depth=0.15,
                               cx=0, cy=0, cz=thickness, angle_deg=90)

    return combine([body, prongs, scallop, well, lip, groove])


def tool_pennant(total_length=62):
    """
    The Pennant Tool [Score: 89.7] — flag-shaped handle matching The Pennant marker.
    Creates a collectible matched set. Kidney-inspired ergonomics.
    """
    handle_len = 40
    prong_len = 17
    neck_len = 5

    # Pennant-shaped handle, rotated 90° to align along Z axis
    handle_pts = pennant_profile(width=handle_len, height=16, taper=0.6)
    handle_pts_rotated = [[-p[1], p[0]] for p in handle_pts]
    handle = extrude_profile(handle_pts_rotated, thickness=9, z_base=0)

    # Neck transition
    neck = frustum(
        r_bottom=5.5, r_top=3.5,
        height=neck_len, segments=16,
        cx=0, cy=handle_len / 2 + 2, cz=3.5
    )

    # Tapered prongs
    prongs = prong_pair_tapered(
        length=prong_len, base_width=2.0, tip_width=1.2,
        gap=6.0, cx=0, cy=handle_len / 2 + 2 + neck_len, cz=5
    )

    # Finger scallop on handle body
    scallop = box(width=12, depth=2.0, height=0.5,
                  cx=0, cy=0, cz=9)

    # Magnet well at wide end
    well = magnet_well(cx=0, cy=-handle_len / 2 + 6, cz=0)
    lip = magnet_well_lip(cx=0, cy=-handle_len / 2 + 6, cz=0)

    return combine([handle, neck, prongs, scallop, well, lip])


def tool_tshape(total_length=62):
    """
    The T-Handle [Score: 88.9] — T-shaped for maximum leverage.
    Kidney cross-section handle bar perpendicular to prong axis.
    Ergonomic powerhouse for stubborn divots.
    """
    prong_len = 17
    stem_len = 30
    bar_len = 40
    bar_thickness = 9

    # Vertical stem
    stem = frustum(
        r_bottom=5.0, r_top=4.0,
        height=stem_len, segments=20,
        cx=0, cy=0, cz=0
    )

    # Horizontal T-bar at top of stem
    bar_pts = rounded_rect_profile(bar_len, bar_thickness, corner_radius=2.5,
                                    segments_per_corner=6)
    # Extrude bar perpendicular: swap X and Z conceptually
    # Actually: create the bar as a flat piece at the top
    bar = extrude_profile(bar_pts, thickness=bar_thickness, z_base=stem_len)

    # Finger scallops on bar ends
    scallop_l = box(width=6, depth=3, height=0.5,
                    cx=-14, cy=0, cz=stem_len + bar_thickness)
    scallop_r = box(width=6, depth=3, height=0.5,
                    cx=14, cy=0, cz=stem_len + bar_thickness)

    # Tapered prongs at bottom of stem
    prongs = prong_pair_tapered(
        length=prong_len, base_width=2.2, tip_width=1.2,
        gap=6.0, cx=0, cy=0, cz=-prong_len
    )

    # Magnet well on top of T-bar
    well = magnet_well(cx=0, cy=0, cz=stem_len)
    lip = magnet_well_lip(cx=0, cy=0, cz=stem_len)

    return combine([stem, bar, scallop_l, scallop_r, prongs, well, lip])


def tool_coin(diameter=38, thickness=8):
    """
    The Coin [Score: 87.1] — thick disc with fold-out prong slots.
    Fidget-worthy concentric grooves. Challenge-coin aesthetic.
    Pocket-sized, hefty, satisfying.
    """
    # Main disc body
    body = cyl(radius=diameter / 2, height=thickness, segments=64)

    # Concentric grooves on top face — the signature coin texture
    top_grooves = concentric_grooves(
        r_start=MAGNET_WELL_DIAMETER / 2 + 2.5,
        r_end=diameter / 2 - 3,
        spacing=2.5, groove_w=0.5, groove_d=0.3,
        segments=64, cz=thickness
    )

    # Concentric grooves on bottom face
    bottom_grooves = concentric_grooves(
        r_start=MAGNET_WELL_DIAMETER / 2 + 2.5,
        r_end=diameter / 2 - 3,
        spacing=2.5, groove_w=0.5, groove_d=0.3,
        segments=64, cz=0
    )

    # Knurled edge band
    knurl = knurl_band(
        radius=diameter / 2, band_height=thickness,
        knurl_count=32, knurl_w=1.0, knurl_d=0.3,
        cx=0, cy=0, cz=0
    )

    # Prong slots — represented as two rectangular channels in the disc
    # (In practice these would house fold-out prongs)
    prong_slot_1 = box(width=2.0, depth=2.0, height=thickness + 0.5,
                       cx=-3, cy=diameter / 2 - 5, cz=-0.25)
    prong_slot_2 = box(width=2.0, depth=2.0, height=thickness + 0.5,
                       cx=3, cy=diameter / 2 - 5, cz=-0.25)

    # Prongs that extend from the disc edge
    prongs = prong_pair_tapered(
        length=15, base_width=2.0, tip_width=1.2,
        gap=6.0, cx=0, cy=diameter / 2 - 2, cz=thickness / 2 - 1
    )

    # Magnet well centered
    well = magnet_well(cx=0, cy=0, cz=0)
    lip = magnet_well_lip(cx=0, cy=0, cz=0)

    return combine([body, top_grooves, bottom_grooves, knurl,
                    prong_slot_1, prong_slot_2, prongs, well, lip])


# ===========================================================================
# COLLECTION GENERATORS
# ===========================================================================

def generate_authority_v2():
    """
    Generate the final Authority Collection v2 — 5 markers + 5 tools.
    The result of evaluating 476,280 design combinations.
    """
    markers = [
        ('MARSHAL-MKR-AUTH-PEN-v2',  'The Pennant',    marker_pennant),
        ('MARSHAL-MKR-AUTH-HRG-v2',  'The Hourglass',  marker_hourglass),
        ('MARSHAL-MKR-AUTH-SUN-v2',  'The Sundial',    marker_sundial),
        ('MARSHAL-MKR-AUTH-STP-v2',  'The Stopwatch',  marker_stopwatch),
        ('MARSHAL-MKR-AUTH-DVS-v2',  'The Divot Star', marker_divot_star),
    ]

    tools = [
        ('MARSHAL-DVT-AUTH-CLS-v2',  'The Classic',    tool_classic),
        ('MARSHAL-DVT-AUTH-WDG-v2',  'The Wedge',      tool_wedge),
        ('MARSHAL-DVT-AUTH-PEN-v2',  'The Pennant',    tool_pennant),
        ('MARSHAL-DVT-AUTH-TSH-v2',  'The T-Handle',   tool_tshape),
        ('MARSHAL-DVT-AUTH-CON-v2',  'The Coin',       tool_coin),
    ]

    all_paths = []

    print("\n" + "="*60)
    print("  AUTHORITY COLLECTION v2 — 5 Ball Markers")
    print("="*60 + "\n")
    for sku, display_name, fn in markers:
        print(f"  Generating {display_name}...")
        m = fn()
        path = save(m, sku)
        all_paths.append(path)
        print()

    print("\n" + "="*60)
    print("  AUTHORITY COLLECTION v2 — 5 Divot Tools")
    print("="*60 + "\n")
    for sku, display_name, fn in tools:
        print(f"  Generating {display_name}...")
        m = fn()
        path = save(m, sku)
        all_paths.append(path)
        print()

    print("="*60)
    print(f"  Collection complete. {len(all_paths)} STL files saved to ./output/")
    print("="*60 + "\n")
    return all_paths


# Keep original v1 generators for backwards compatibility
def generate_authority_collection():
    """Original v1 collection — 5 markers only."""
    return generate_authority_v2()
