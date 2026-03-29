"""
Profile Extrusion System
Converts 2D outlines into 3D solids.
The silhouette-first design method — define the shape, then extrude.
All units in millimeters.
"""

import numpy as np
from stl import mesh
import math


def extrude_profile(points, thickness, z_base=0):
    """
    Takes a list of [x, y] points defining a closed 2D polygon.
    Extrudes vertically to create a 3D solid.

    points:    list of [x, y] — closed polygon vertices in order
    thickness: float — extrusion height in mm
    z_base:    float — bottom z coordinate
    """
    n = len(points)
    faces = []
    z_top = z_base + thickness

    # Side walls
    for i in range(n):
        j = (i + 1) % n
        p1, p2 = points[i], points[j]
        faces.append([[p1[0], p1[1], z_base], [p2[0], p2[1], z_base], [p2[0], p2[1], z_top]])
        faces.append([[p1[0], p1[1], z_base], [p2[0], p2[1], z_top], [p1[0], p1[1], z_top]])

    # Top and bottom caps (fan triangulation from centroid)
    cx = sum(p[0] for p in points) / n
    cy = sum(p[1] for p in points) / n
    for i in range(n):
        j = (i + 1) % n
        faces.append([[cx, cy, z_top],
                      [points[i][0], points[i][1], z_top],
                      [points[j][0], points[j][1], z_top]])
        faces.append([[cx, cy, z_base],
                      [points[j][0], points[j][1], z_base],
                      [points[i][0], points[i][1], z_base]])

    data = np.zeros(len(faces), dtype=mesh.Mesh.dtype)
    for k, f in enumerate(faces):
        data['vectors'][k] = f
    return mesh.Mesh(data)


def rounded_rect_profile(width, height, corner_radius, segments_per_corner=8):
    """
    Generate [x, y] points for a rounded rectangle centered at origin.
    Used for tool handles, wallet-cards, and rectangular markers.
    """
    pts = []
    corners = [
        (width / 2 - corner_radius, -height / 2 + corner_radius, -math.pi / 2),
        (width / 2 - corner_radius,  height / 2 - corner_radius,  0),
        (-width / 2 + corner_radius,  height / 2 - corner_radius,  math.pi / 2),
        (-width / 2 + corner_radius, -height / 2 + corner_radius,  math.pi),
    ]
    for cx, cy, start_angle in corners:
        for i in range(segments_per_corner + 1):
            angle = start_angle + (math.pi / 2) * i / segments_per_corner
            pts.append([cx + corner_radius * math.cos(angle),
                        cy + corner_radius * math.sin(angle)])
    return pts


def pennant_profile(width=35, height=22, taper=0.7):
    """
    Triangular flag / pennant silhouette.
    Classic golf flag shape — wide on the left (pole side), tapering to a point.

    width:  total width in mm
    height: total height at widest point in mm
    taper:  how aggressively it tapers toward the tip (0-1, higher = sharper)
    """
    pts = []
    steps = 40
    half_h = height / 2
    x_start = -width / 2
    x_span = width

    # Bottom edge (left to right, tapering up)
    for i in range(steps):
        t = i / (steps - 1)
        x = x_start + t * x_span
        y = -half_h * (1 - t * taper)
        pts.append([x, y])

    # Tip
    pts.append([width / 2, 0])

    # Top edge (right to left, tapering down)
    for i in range(steps - 1, -1, -1):
        t = i / (steps - 1)
        x = x_start + t * x_span
        y = half_h * (1 - t * taper)
        pts.append([x, y])

    return pts


def hourglass_profile(width=18, height=28, waist_ratio=0.35):
    """
    Hourglass / sand timer silhouette — wide at top and bottom, narrow at center.
    Communicates pace-of-play for Marshal Golf.

    width:       max width at top/bottom in mm
    height:      total height in mm
    waist_ratio: width of waist as fraction of max width (0.2-0.5)
    """
    pts = []
    steps = 60
    half_h = height / 2
    half_w = width / 2
    waist_w = half_w * waist_ratio

    # Right side (bottom to top)
    for i in range(steps):
        t = i / (steps - 1)
        y = -half_h + t * height
        # Smoothstep between waist and full width
        w = waist_w + (half_w - waist_w) * abs(math.cos(math.pi * t))
        pts.append([w, y])

    # Left side (top to bottom)
    for i in range(steps - 1, -1, -1):
        t = i / (steps - 1)
        y = -half_h + t * height
        w = waist_w + (half_w - waist_w) * abs(math.cos(math.pi * t))
        pts.append([-w, y])

    return pts


def wave_profile(width=34, height=12, wave_freq=1.5, wave_amp=4.0):
    """
    Organic S-curve / wave silhouette.
    Both top and bottom edges undulate for a fluid, water-inspired shape.

    width:     total width in mm
    height:    average height in mm
    wave_freq: number of wave cycles across the width
    wave_amp:  amplitude of the wave in mm
    """
    pts = []
    steps = 80
    half_w = width / 2
    half_h = height / 2

    # Top edge (left to right)
    for i in range(steps):
        t = i / (steps - 1)
        x = -half_w + t * width
        y = half_h + wave_amp * math.sin(2 * math.pi * t * wave_freq)
        pts.append([x, y])

    # Bottom edge (right to left, offset phase)
    for i in range(steps - 1, -1, -1):
        t = i / (steps - 1)
        x = -half_w + t * width
        y = -half_h - (wave_amp * 0.75) * math.sin(2 * math.pi * t * wave_freq + math.pi * 0.5)
        pts.append([x, y])

    return pts


def tee_profile(shaft_w=6, shaft_h=22, head_w=22, head_h=5):
    """
    Golf tee silhouette — shaft with a wider flat head on top.
    Instantly recognizable golf symbol.

    shaft_w: shaft width in mm
    shaft_h: shaft height in mm
    head_w:  head (cap) width in mm
    head_h:  head (cap) height in mm
    """
    hw_s = shaft_w / 2
    hw_h = head_w / 2
    total_h = shaft_h + head_h
    r = min(head_h * 0.4, hw_h * 0.25)  # corner radius on the tee head

    pts = []
    # Bottom corners of shaft (small radius)
    rs = 1.0
    for i in range(5):
        a = -math.pi / 2 + math.pi / 2 * i / 4
        pts.append([hw_s - rs + rs * math.cos(a), rs + rs * math.sin(a)])

    # Right side shaft up to head
    pts.append([hw_s, shaft_h])

    # Right shoulder of head
    for i in range(5):
        a = -math.pi / 2 + math.pi / 2 * i / 4
        pts.append([hw_h - r + r * math.cos(a), shaft_h + r + r * math.sin(a)])

    # Top-right corner
    for i in range(5):
        a = 0 + math.pi / 2 * i / 4
        pts.append([hw_h - r + r * math.cos(a), total_h - r + r * math.sin(a)])

    # Top-left corner
    for i in range(5):
        a = math.pi / 2 + math.pi / 2 * i / 4
        pts.append([-hw_h + r + r * math.cos(a), total_h - r + r * math.sin(a)])

    # Left shoulder of head
    for i in range(5):
        a = math.pi + math.pi / 2 * i / 4
        pts.append([-hw_h + r + r * math.cos(a), shaft_h + r + r * math.sin(a)])

    # Left side shaft down
    pts.append([-hw_s, shaft_h])

    # Bottom-left shaft corner
    for i in range(5):
        a = math.pi / 2 + math.pi / 2 * i / 4
        pts.append([-hw_s + rs + rs * math.cos(a), rs + rs * math.sin(a)])

    return pts


def whistle_profile(body_w=28, body_h=14, mouthpiece_w=8, mouthpiece_h=6):
    """
    Referee/marshal whistle silhouette — rounded body with a mouthpiece protrusion.
    A marshal's tool without any law-enforcement connotation.
    """
    pts = []
    # Main body: rounded rectangle
    r = body_h / 2
    body_cx = 0
    body_cy = 0

    # Right half of body (top arc)
    for i in range(12):
        angle = -math.pi / 2 + math.pi * i / 11
        pts.append([body_cx + body_w / 2 - r + r * math.cos(angle),
                    body_cy + r * math.sin(angle)])

    # Left curve of body
    for i in range(12):
        angle = math.pi / 2 + math.pi * i / 11
        pts.append([body_cx - body_w / 2 + r + r * math.cos(angle),
                    body_cy + r * math.sin(angle)])

    return pts


def sundial_profile(diameter=30, gnomon_w=4, gnomon_h=10):
    """
    Sundial silhouette — circular base with a triangular gnomon (shadow-caster)
    rising from the top. Ancient timekeeper = pace of play theme.
    """
    pts = []
    r = diameter / 2
    segments = 48

    # Circle from right side going counter-clockwise, skipping where gnomon goes
    gnomon_half_angle = math.asin(min(gnomon_w / 2 / r, 1.0))

    for i in range(segments):
        angle = -math.pi / 2 + 2 * math.pi * i / segments
        # Skip the gnomon zone at the top (angle near pi/2)
        if math.pi / 2 - gnomon_half_angle < angle < math.pi / 2 + gnomon_half_angle:
            continue
        pts.append([r * math.cos(angle), r * math.sin(angle)])

    # Insert gnomon triangle at the top
    gw = gnomon_w / 2
    g_base_y = math.sqrt(max(r**2 - gw**2, 0))
    pts_with_gnomon = []
    inserted = False
    for p in pts:
        if not inserted and p[1] > g_base_y * 0.9 and p[0] > 0:
            # Insert gnomon before this point
            pts_with_gnomon.append([gw, g_base_y])
            pts_with_gnomon.append([gw * 0.3, r + gnomon_h * 0.8])
            pts_with_gnomon.append([0, r + gnomon_h])
            pts_with_gnomon.append([-gw * 0.3, r + gnomon_h * 0.8])
            pts_with_gnomon.append([-gw, g_base_y])
            inserted = True
        pts_with_gnomon.append(p)

    if not inserted:
        # Fallback: append gnomon at end
        pts_with_gnomon.append([gw, g_base_y])
        pts_with_gnomon.append([gw * 0.3, r + gnomon_h * 0.8])
        pts_with_gnomon.append([0, r + gnomon_h])
        pts_with_gnomon.append([-gw * 0.3, r + gnomon_h * 0.8])
        pts_with_gnomon.append([-gw, g_base_y])

    return pts_with_gnomon


def stopwatch_profile(diameter=28, crown_w=6, crown_h=5, button_w=3, button_h=3.5):
    """
    Stopwatch silhouette — circular face with crown at top and side pusher button.
    Marshal's timing tool — pace of play.
    """
    pts = []
    r = diameter / 2
    segments = 64

    # Crown angular zone at top (angle pi/2)
    crown_half = math.asin(min(crown_w / 2 / r, 1.0))
    # Button angular zone at 2 o'clock (angle ~pi/6)
    button_angle = math.pi / 6
    button_half = math.asin(min(button_w / 2 / r, 1.0))

    for i in range(segments):
        angle = 2 * math.pi * i / segments

        # Skip crown zone
        if abs(angle - math.pi / 2) < crown_half:
            continue
        # Skip button zone
        if abs(angle - button_angle) < button_half:
            continue

        pts.append([r * math.cos(angle), r * math.sin(angle)])

    # Now insert crown and button features
    cw = crown_w / 2
    crown_base_y = math.sqrt(max(r**2 - cw**2, 0))
    bw = button_w / 2
    btn_base_x = r * math.cos(button_angle)
    btn_base_y = r * math.sin(button_angle)
    btn_nx = math.cos(button_angle)
    btn_ny = math.sin(button_angle)

    result = []
    crown_done = False
    button_done = False

    for idx, p in enumerate(pts):
        angle = math.atan2(p[1], p[0])
        if angle < 0:
            angle += 2 * math.pi

        # Insert button around pi/6
        if not button_done and angle > button_angle + button_half:
            bx1 = r * math.cos(button_angle - button_half)
            by1 = r * math.sin(button_angle - button_half)
            bx2 = r * math.cos(button_angle + button_half)
            by2 = r * math.sin(button_angle + button_half)
            result.append([bx1, by1])
            result.append([bx1 + button_h * btn_nx, by1 + button_h * btn_ny])
            result.append([bx2 + button_h * btn_nx, by2 + button_h * btn_ny])
            result.append([bx2, by2])
            button_done = True

        # Insert crown around pi/2
        if not crown_done and angle > math.pi / 2 + crown_half:
            result.append([cw, crown_base_y])
            result.append([cw, crown_base_y + crown_h * 0.7])
            result.append([cw * 0.5, crown_base_y + crown_h])
            result.append([-cw * 0.5, crown_base_y + crown_h])
            result.append([-cw, crown_base_y + crown_h * 0.7])
            result.append([-cw, crown_base_y])
            crown_done = True

        result.append(p)

    return result


def divot_star_profile(radius=15, points_count=6, inner_ratio=0.55):
    """
    Divot repair starburst — the pattern left when you properly repair a ball mark.
    Communicates course etiquette and care.
    """
    pts = []
    inner_r = radius * inner_ratio
    total_pts = points_count * 2
    segments_per_arm = 3

    for i in range(total_pts):
        angle = 2 * math.pi * i / total_pts - math.pi / 2
        next_angle = 2 * math.pi * ((i + 1) % total_pts) / total_pts - math.pi / 2
        r_curr = radius if i % 2 == 0 else inner_r
        r_next = inner_r if i % 2 == 0 else radius

        for j in range(segments_per_arm):
            t = j / segments_per_arm
            a = angle + t * (next_angle - angle)
            cr = r_curr + t * (r_next - r_curr)
            pts.append([cr * math.cos(a), cr * math.sin(a)])

    return pts


def kidney_profile(width=16, height=12, indent=0.3, segments=32):
    """
    Kidney bean cross-section — ergonomic grip shape for tool handles.
    """
    pts = []
    hw = width / 2
    hh = height / 2

    for i in range(segments):
        angle = 2 * math.pi * i / segments
        x = hw * math.cos(angle)
        y = hh * math.sin(angle)
        if math.cos(angle) > 0:
            indent_amount = indent * hw * math.sin(angle) ** 2
            x -= indent_amount
        pts.append([x, y])

    return pts


def coin_disc_profile(diameter=38, edge_segments=64):
    """Thick coin disc for coin-form divot tools."""
    pts = []
    r = diameter / 2
    for i in range(edge_segments):
        angle = 2 * math.pi * i / edge_segments
        pts.append([r * math.cos(angle), r * math.sin(angle)])
    return pts
