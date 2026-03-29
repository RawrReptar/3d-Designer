"""Basic smoke tests for geometry primitives and products."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import numpy as np
from src.primitives import cyl, ring, box, frustum, combine
from src.profiles import (
    extrude_profile, rounded_rect_profile,
    pennant_profile, hourglass_profile, wave_profile
)
from src.features import magnet_well, alignment_groove, prong_pair
from src.products import (
    marker_pennant, marker_hourglass, marker_sundial, marker_stopwatch,
    marker_divot_star, tool_classic, tool_wedge, tool_pennant, tool_tshape, tool_coin
)


def test_cyl_face_count():
    m = cyl(radius=10, height=5, segments=48)
    assert len(m.data) == 48 * 4


def test_box_face_count():
    m = box(10, 10, 10)
    assert len(m.data) == 12


def test_ring_face_count():
    m = ring(outer_r=10, inner_r=5, height=3, segments=48)
    assert len(m.data) == 48 * 8


def test_frustum_face_count():
    m = frustum(r_bottom=10, r_top=6, height=5, segments=48)
    assert len(m.data) == 48 * 4


def test_combine():
    a = cyl(5, 5)
    b = box(3, 3, 3)
    c = combine([a, b])
    assert len(c.data) == len(a.data) + len(b.data)


def test_extrude_profile():
    pts = [[0, 0], [10, 0], [10, 10], [0, 10]]
    m = extrude_profile(pts, thickness=5)
    assert len(m.data) > 0


def test_pennant_profile():
    pts = pennant_profile()
    assert len(pts) > 10


def test_hourglass_profile():
    pts = hourglass_profile()
    assert len(pts) > 10


def test_wave_profile():
    pts = wave_profile()
    assert len(pts) > 10


def test_rounded_rect_profile():
    pts = rounded_rect_profile(width=20, height=10, corner_radius=2)
    assert len(pts) > 4


def test_magnet_well_returns_mesh():
    m = magnet_well()
    assert m is not None
    assert len(m.data) > 0


def test_prong_pair_returns_mesh():
    m = prong_pair()
    assert m is not None
    assert len(m.data) > 0


def test_marker_pennant_dimensions():
    m = marker_pennant()
    x = m.vectors[:, :, 0]
    y = m.vectors[:, :, 1]
    z = m.vectors[:, :, 2]
    dx = x.max() - x.min()
    dy = y.max() - y.min()
    dz = z.max() - z.min()
    assert dx <= 40, f"Marker too wide: {dx:.1f}mm"
    assert dy <= 40, f"Marker too tall: {dy:.1f}mm"
    assert dz <= 10, f"Marker too thick: {dz:.1f}mm"


def test_marker_hourglass_dimensions():
    m = marker_hourglass()
    x = m.vectors[:, :, 0]
    y = m.vectors[:, :, 1]
    z = m.vectors[:, :, 2]
    dx = x.max() - x.min()
    dy = y.max() - y.min()
    assert max(dx, dy) <= 40


def test_marker_sundial():
    m = marker_sundial()
    x = m.vectors[:, :, 0]
    y = m.vectors[:, :, 1]
    assert max(x.max() - x.min(), y.max() - y.min()) <= 40


def test_marker_stopwatch():
    m = marker_stopwatch()
    x = m.vectors[:, :, 0]
    y = m.vectors[:, :, 1]
    assert max(x.max() - x.min(), y.max() - y.min()) <= 40


def test_marker_divot_star():
    m = marker_divot_star()
    x = m.vectors[:, :, 0]
    y = m.vectors[:, :, 1]
    assert max(x.max() - x.min(), y.max() - y.min()) <= 40


def test_tool_classic_length():
    m = tool_classic(total_length=62)
    z = m.vectors[:, :, 2]
    dz = z.max() - z.min()
    assert dz >= 35, f"Tool too short: {dz:.1f}mm"
    assert dz <= 110, f"Tool too long: {dz:.1f}mm"


def test_tool_wedge():
    m = tool_wedge()
    assert len(m.data) > 0


def test_tool_pennant():
    m = tool_pennant()
    assert len(m.data) > 0


def test_tool_tshape():
    m = tool_tshape()
    assert len(m.data) > 0


def test_tool_coin():
    m = tool_coin()
    assert len(m.data) > 0


if __name__ == '__main__':
    tests = [v for k, v in globals().items() if k.startswith('test_')]
    passed = 0
    failed = 0
    for t in tests:
        try:
            t()
            print(f"  PASS  {t.__name__}")
            passed += 1
        except Exception as e:
            print(f"  FAIL  {t.__name__}: {e}")
            failed += 1
    print(f"\n{passed} passed, {failed} failed")
