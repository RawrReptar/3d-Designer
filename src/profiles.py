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
