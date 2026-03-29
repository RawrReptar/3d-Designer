"""
Design Space Explorer & Scoring Engine
Systematically generates 1000+ marker and 1000+ tool concepts,
scores them against Marshal Golf criteria, and culls to the best 5+5.
"""

import itertools
import random
import json
import os

random.seed(42)

# ===========================================================================
# DESIGN SPACE DEFINITIONS
# ===========================================================================

MARKER_SILHOUETTES = {
    'pennant':      {'desc': 'Triangular flag on pole', 'brand': 9, 'silhouette': 9, 'innovation': 5, 'story': 'Golf flag — instant course recognition'},
    'hourglass':    {'desc': 'Sand timer shape', 'brand': 10, 'silhouette': 10, 'innovation': 7, 'story': 'Pace of play — keep pace, keep peace'},
    'wave':         {'desc': 'Flowing S-curve water shape', 'brand': 7, 'silhouette': 8, 'innovation': 6, 'story': 'Water hazard, flow, rhythm of the game'},
    'tee':          {'desc': 'Golf tee side profile', 'brand': 8, 'silhouette': 8, 'innovation': 4, 'story': 'The starting point of every hole'},
    'disc':         {'desc': 'Classic round coin', 'brand': 5, 'silhouette': 3, 'innovation': 2, 'story': 'Premium regulation disc'},
    'stopwatch':    {'desc': 'Circular with crown button', 'brand': 9, 'silhouette': 7, 'innovation': 6, 'story': 'Time and pace — the marshals clock'},
    'whistle':      {'desc': 'Referee whistle profile', 'brand': 8, 'silhouette': 7, 'innovation': 7, 'story': 'The marshals call to order'},
    'leaf':         {'desc': 'Oak or grass blade', 'brand': 6, 'silhouette': 7, 'innovation': 5, 'story': 'Nature, the course landscape'},
    'topographic':  {'desc': 'Contour line nested shape', 'brand': 7, 'silhouette': 9, 'innovation': 9, 'story': 'Course terrain, reading the green'},
    'bunker':       {'desc': 'Aerial bunker outline', 'brand': 7, 'silhouette': 8, 'innovation': 8, 'story': 'Sand trap — course architecture'},
    'bridge':       {'desc': 'Arch / Swilcan bridge', 'brand': 6, 'silhouette': 7, 'innovation': 6, 'story': 'Iconic course features'},
    'compass':      {'desc': 'Compass rose directional', 'brand': 7, 'silhouette': 8, 'innovation': 6, 'story': 'Finding your line, reading direction'},
    'yardage':      {'desc': '150-yard post marker', 'brand': 8, 'silhouette': 6, 'innovation': 5, 'story': 'Distance, precision, course knowledge'},
    'divot_star':   {'desc': 'Starburst repair pattern', 'brand': 8, 'silhouette': 8, 'innovation': 8, 'story': 'Course care, etiquette embodied'},
    'shield':       {'desc': 'Heraldic crest shape', 'brand': 4, 'silhouette': 6, 'innovation': 3, 'story': 'Traditional authority'},
    'teardrop':     {'desc': 'Elongated drop shape', 'brand': 5, 'silhouette': 7, 'innovation': 5, 'story': 'Morning dew, organic form'},
    'arrow':        {'desc': 'Directional arrow head', 'brand': 6, 'silhouette': 7, 'innovation': 5, 'story': 'Direction, putting line'},
    'infinity':     {'desc': 'Figure-eight loop', 'brand': 6, 'silhouette': 8, 'innovation': 7, 'story': 'Endless pursuit of the perfect round'},
    'hexagon':      {'desc': 'Golf ball dimple unit', 'brand': 7, 'silhouette': 5, 'innovation': 4, 'story': 'Golf ball geometry reference'},
    'crescent':     {'desc': 'Moon crescent curve', 'brand': 5, 'silhouette': 7, 'innovation': 6, 'story': 'Early morning / twilight rounds'},
    'sundial':      {'desc': 'Sundial with gnomon', 'brand': 9, 'silhouette': 9, 'innovation': 8, 'story': 'Ancient timekeeper — pace theme'},
    'rake':         {'desc': 'Bunker rake profile', 'brand': 7, 'silhouette': 7, 'innovation': 6, 'story': 'Course maintenance, etiquette'},
    'acorn':        {'desc': 'Acorn / oak seed', 'brand': 5, 'silhouette': 7, 'innovation': 5, 'story': 'From small things, great oaks grow'},
    'mountain':     {'desc': 'Peak / ridge profile', 'brand': 5, 'silhouette': 7, 'innovation': 5, 'story': 'Elevation, course terrain'},
    'bell':         {'desc': 'Bell shape / marshal bell', 'brand': 8, 'silhouette': 7, 'innovation': 6, 'story': 'Marshals bell — attention signal'},
}

MARKER_TEXTURES = {
    'smooth':       {'tactile': 5, 'printability': 10, 'premium': 7, 'desc': 'Polished smooth surface'},
    'micro_stipple': {'tactile': 9, 'printability': 8, 'premium': 9, 'desc': 'Fine random micro-bumps (SLA)'},
    'concentric':   {'tactile': 8, 'printability': 9, 'premium': 8, 'desc': 'Concentric ring grooves'},
    'crosshatch':   {'tactile': 7, 'printability': 7, 'premium': 6, 'desc': 'Diamond crosshatch pattern'},
    'organic_flow': {'tactile': 9, 'printability': 7, 'premium': 10, 'desc': 'Flowing contour lines following form'},
    'dimple':       {'tactile': 6, 'printability': 8, 'premium': 5, 'desc': 'Golf ball dimple pattern'},
    'brushed':      {'tactile': 7, 'printability': 6, 'premium': 8, 'desc': 'Simulated brushed metal grain'},
}

MARKER_THICKNESSES = {
    'slim':    {'mm': 2.5, 'weight': 4, 'premium': 5, 'printability': 9},
    'medium':  {'mm': 3.5, 'weight': 7, 'premium': 7, 'printability': 9},
    'thick':   {'mm': 4.5, 'weight': 9, 'premium': 9, 'printability': 8},
}

MARKER_ALIGNMENT = {
    'center_line':  {'function': 9, 'clean': 8, 'desc': 'Single center groove'},
    'dual_line':    {'function': 8, 'clean': 6, 'desc': 'Two parallel lines'},
    'arrow_line':   {'function': 10, 'clean': 7, 'desc': 'Directional arrow groove'},
    'shape_edge':   {'function': 7, 'clean': 10, 'desc': 'Shape edge provides natural line'},
    'none':         {'function': 0, 'clean': 10, 'desc': 'No alignment feature'},
}

MARKER_BACK_DESIGN = {
    'plain_magnet':     {'cost': 10, 'premium': 4, 'desc': 'Flat back with magnet well only'},
    'concentric_back':  {'cost': 7, 'premium': 8, 'desc': 'Concentric rings around magnet well'},
    'brand_zone':       {'cost': 6, 'premium': 9, 'desc': 'Recessed area for brand mark'},
    'mirror_texture':   {'cost': 5, 'premium': 10, 'desc': 'Matching texture on both sides'},
    'secondary_art':    {'cost': 4, 'premium': 10, 'desc': 'Unique secondary design on back'},
}

MARKER_SIZES = {
    'small':  {'mm': 26, 'pocketable': 10, 'presence': 4},
    'medium': {'mm': 32, 'pocketable': 8, 'presence': 7},
    'large':  {'mm': 38, 'pocketable': 5, 'presence': 10},
}

MARKER_SPECIAL = {
    'none':           {'innovation': 0, 'complexity': 0, 'price_add': 0, 'desc': 'No special feature'},
    'exposed_gyroid':  {'innovation': 10, 'complexity': 8, 'price_add': 9, 'desc': 'Cutaway revealing internal lattice'},
    'raised_boss':    {'innovation': 3, 'complexity': 3, 'price_add': 2, 'desc': 'Central raised dome or plateau'},
    'edge_rope':      {'innovation': 5, 'complexity': 6, 'price_add': 4, 'desc': 'Twisted rope detail around perimeter'},
    'perimeter_groove': {'innovation': 3, 'complexity': 2, 'price_add': 1, 'desc': 'Recessed groove around outer edge'},
    'window_cutout':  {'innovation': 8, 'complexity': 7, 'price_add': 7, 'desc': 'Through-hole window revealing layer beneath'},
    'fidget_channel': {'innovation': 9, 'complexity': 8, 'price_add': 8, 'desc': 'Thumb groove for fidget interaction'},
    'dome_top':       {'innovation': 4, 'complexity': 4, 'price_add': 3, 'desc': 'Gentle dome rise on top surface'},
}

# ---------------------------------------------------------------------------
# DIVOT TOOL DESIGN SPACE
# ---------------------------------------------------------------------------

TOOL_FORM_FACTORS = {
    'classic':      {'desc': 'Fixed two-prong, sculpted handle', 'ergonomic': 8, 'innovation': 4, 'premium': 8, 'printability': 9},
    'switchblade':  {'desc': 'Folding prongs with spring deploy', 'ergonomic': 7, 'innovation': 8, 'premium': 9, 'printability': 4},
    'wedge':        {'desc': 'Ultra-thin flat card form', 'ergonomic': 5, 'innovation': 7, 'premium': 7, 'printability': 10},
    'hook':         {'desc': 'Curved clip for belt/bag', 'ergonomic': 6, 'innovation': 6, 'premium': 6, 'printability': 7},
    'coin':         {'desc': 'Thick disc with fold-out prongs', 'ergonomic': 6, 'innovation': 7, 'premium': 8, 'printability': 6},
    'pennant':      {'desc': 'Flag-shaped handle matching marker', 'ergonomic': 7, 'innovation': 6, 'premium': 9, 'printability': 8},
    'tshape':       {'desc': 'T-handle for leverage', 'ergonomic': 9, 'innovation': 5, 'premium': 6, 'printability': 8},
    'lshape':       {'desc': 'L-shaped with clip hook', 'ergonomic': 7, 'innovation': 6, 'premium': 5, 'printability': 7},
}

TOOL_HANDLE_SHAPES = {
    'round':     {'comfort': 7, 'grip': 6, 'desc': 'Circular cross-section'},
    'oval':      {'comfort': 9, 'grip': 8, 'desc': 'Oval / elliptical cross-section'},
    'teardrop':  {'comfort': 8, 'grip': 9, 'desc': 'Teardrop with finger indexing'},
    'flat':      {'comfort': 5, 'grip': 5, 'desc': 'Flat rectangular slab'},
    'kidney':    {'comfort': 9, 'grip': 9, 'desc': 'Kidney bean ergonomic contour'},
    'dshape':    {'comfort': 8, 'grip': 8, 'desc': 'D-shape with flat back'},
}

TOOL_PRONG_STYLES = {
    'parallel':    {'strength': 8, 'effectiveness': 8, 'desc': 'Straight parallel prongs'},
    'v_spread':    {'strength': 7, 'effectiveness': 7, 'desc': 'Slight V-splay outward'},
    'tapered':     {'strength': 9, 'effectiveness': 9, 'desc': 'Wide base tapering to narrow tip'},
    's_curve':     {'strength': 7, 'effectiveness': 9, 'desc': 'Subtle S-curve for lift'},
    'single_wedge': {'strength': 10, 'effectiveness': 6, 'desc': 'Single broad chisel prong'},
}

TOOL_TEXTURES = {
    'smooth':       {'tactile': 5, 'grip_score': 4, 'premium': 7},
    'diamond':      {'tactile': 8, 'grip_score': 9, 'premium': 7},
    'knurled':      {'tactile': 8, 'grip_score': 8, 'premium': 8},
    'concentric':   {'tactile': 7, 'grip_score': 6, 'premium': 8},
    'organic':      {'tactile': 9, 'grip_score': 7, 'premium': 10},
    'stipple':      {'tactile': 8, 'grip_score': 8, 'premium': 8},
    'finger_scallop': {'tactile': 9, 'grip_score': 10, 'premium': 9},
}

TOOL_LENGTHS = {
    'compact':  {'mm': 62, 'pocketable': 10, 'leverage': 5},
    'standard': {'mm': 75, 'pocketable': 7, 'leverage': 8},
    'long':     {'mm': 90, 'pocketable': 4, 'leverage': 10},
}

TOOL_CONNECTIONS = {
    'top_magnet':   {'compatibility': 10, 'ease': 9, 'desc': 'Standard magnet at cap end'},
    'side_magnet':  {'compatibility': 6, 'ease': 7, 'desc': 'Magnet on handle side face'},
    'dual_magnet':  {'compatibility': 10, 'ease': 10, 'desc': 'Two magnets for stronger hold'},
    'clip_magnet':  {'compatibility': 8, 'ease': 8, 'desc': 'Clip + magnet combo'},
}

TOOL_SPECIAL = {
    'none':           {'innovation': 0, 'complexity': 0, 'price_add': 0},
    'bottle_opener':  {'innovation': 3, 'complexity': 4, 'price_add': 3},
    'groove_cleaner': {'innovation': 4, 'complexity': 3, 'price_add': 2},
    'club_rest':      {'innovation': 3, 'complexity': 2, 'price_add': 2},
    'belt_clip':      {'innovation': 5, 'complexity': 5, 'price_add': 4},
    'cigar_groove':   {'innovation': 4, 'complexity': 3, 'price_add': 3},
    'carabiner_hole': {'innovation': 4, 'complexity': 2, 'price_add': 2},
    'exposed_lattice': {'innovation': 10, 'complexity': 8, 'price_add': 9},
}


# ===========================================================================
# SCORING ENGINE
# ===========================================================================

def score_marker(silhouette, texture, thickness, alignment, back, size, special):
    """Score a marker design on 0-100 scale."""
    s = MARKER_SILHOUETTES[silhouette]
    t = MARKER_TEXTURES[texture]
    th = MARKER_THICKNESSES[thickness]
    a = MARKER_ALIGNMENT[alignment]
    b = MARKER_BACK_DESIGN[back]
    sz = MARKER_SIZES[size]
    sp = MARKER_SPECIAL[special]

    # 1. Silhouette strength (25% weight) — the #1 differentiator
    silhouette_score = s['silhouette'] * 2.5

    # 2. Brand alignment (20%)
    brand_score = s['brand'] * 2.0

    # 3. Tactile quality (15%) — texture + thickness + special
    tactile_score = (t['tactile'] * 0.5 + th['weight'] * 0.5 + (sp['innovation'] * 0.3 if sp['innovation'] > 5 else 0)) * 1.5

    # 4. Innovation (15%) — does it use 3D printing advantages?
    innovation_score = (s['innovation'] * 0.4 + sp['innovation'] * 0.6) * 1.5

    # 5. Printability (10%)
    printability_score = (t['printability'] * 0.5 + th['printability'] * 0.5) * 1.0

    # 6. Premium perception (10%)
    premium_score = (t['premium'] * 0.3 + b['premium'] * 0.3 + th['premium'] * 0.2 + sp['price_add'] * 0.2) * 1.0

    # 7. Functional completeness (5%)
    functional_score = (a['function'] * 0.5 + (5 if alignment != 'none' else 0)) * 0.5

    total = silhouette_score + brand_score + tactile_score + innovation_score + printability_score + premium_score + functional_score

    # Penalties
    if silhouette == 'disc' and special == 'none':
        total -= 10  # Generic disc with nothing special
    if silhouette == 'shield':
        total -= 5   # Too close to military/police
    if alignment == 'none' and silhouette not in ('disc', 'hexagon'):
        total -= 3   # Missing alignment on a non-round shape
    if back == 'plain_magnet' and thickness == 'thick':
        total -= 2   # Thick premium marker with plain back = missed opportunity

    # Bonuses
    if s['brand'] >= 8 and sp['innovation'] >= 7:
        total += 5   # High brand + high innovation = exceptional
    if t['tactile'] >= 8 and th['weight'] >= 8:
        total += 3   # Great feel + great heft
    if silhouette in ('hourglass', 'sundial', 'stopwatch') and special == 'fidget_channel':
        total += 4   # Time theme + fidget = addictive product

    return round(min(total, 100), 1)


def score_tool(form, handle, prong, texture, length, connection, special):
    """Score a divot tool design on 0-100 scale."""
    f = TOOL_FORM_FACTORS[form]
    h = TOOL_HANDLE_SHAPES[handle]
    p = TOOL_PRONG_STYLES[prong]
    t = TOOL_TEXTURES[texture]
    l = TOOL_LENGTHS[length]
    c = TOOL_CONNECTIONS[connection]
    sp = TOOL_SPECIAL[special]

    # 1. Ergonomic quality (25%)
    ergo_score = (f['ergonomic'] * 0.4 + h['comfort'] * 0.3 + h['grip'] * 0.15 + t['grip_score'] * 0.15) * 2.5

    # 2. Innovation (20%)
    innovation_score = (f['innovation'] * 0.5 + sp['innovation'] * 0.5) * 2.0

    # 3. Premium perception (15%)
    premium_score = (f['premium'] * 0.4 + t['premium'] * 0.3 + sp['price_add'] * 0.3) * 1.5

    # 4. Functional effectiveness (15%)
    functional_score = (p['effectiveness'] * 0.5 + p['strength'] * 0.3 + l['leverage'] * 0.2) * 1.5

    # 5. Printability (10%)
    printability_score = f['printability'] * 1.0

    # 6. Pocketability (10%)
    pocket_score = l['pocketable'] * 1.0

    # 7. Ecosystem fit (5%)
    ecosystem_score = c['compatibility'] * 0.5

    total = ergo_score + innovation_score + premium_score + functional_score + printability_score + pocket_score + ecosystem_score

    # Penalties
    if form == 'switchblade' and length == 'compact':
        total -= 5  # Not enough room for spring mechanism
    if form == 'wedge' and prong in ('s_curve', 'v_spread'):
        total -= 4  # Wedge form doesn't support complex prong geometry
    if handle == 'flat' and texture == 'knurled':
        total -= 3  # Knurling on flat surface doesn't make sense
    if special == 'bottle_opener' and form == 'coin':
        total -= 3  # Gimmicky combo
    if form == 'lshape' and length == 'long':
        total -= 4  # L-shape at 90mm is unwieldy

    # Bonuses
    if form == 'pennant' and special == 'none':
        total += 3   # Matched set purity — the shape IS the feature
    if h['comfort'] >= 9 and t['grip_score'] >= 8:
        total += 4   # Exceptional hand feel
    if form == 'classic' and handle in ('kidney', 'teardrop') and prong == 'tapered':
        total += 5   # Perfect classic tool recipe
    if form == 'wedge' and length == 'compact':
        total += 3   # Wallet-perfect

    return round(min(total, 100), 1)


# ===========================================================================
# DESIGN GENERATION & CULLING PIPELINE
# ===========================================================================

def generate_marker_designs():
    """Generate all valid marker combinations and score them."""
    designs = []
    axes = [
        list(MARKER_SILHOUETTES.keys()),
        list(MARKER_TEXTURES.keys()),
        list(MARKER_THICKNESSES.keys()),
        list(MARKER_ALIGNMENT.keys()),
        list(MARKER_BACK_DESIGN.keys()),
        list(MARKER_SIZES.keys()),
        list(MARKER_SPECIAL.keys()),
    ]

    total_combos = 1
    for a in axes:
        total_combos *= len(a)

    print(f"Marker design space: {total_combos:,} total combinations")

    # Sample strategically: all silhouettes × top combos
    for combo in itertools.product(*axes):
        sil, tex, thick, align, back, size, special = combo
        score = score_marker(sil, tex, thick, align, back, size, special)
        designs.append({
            'type': 'marker',
            'silhouette': sil,
            'texture': tex,
            'thickness': thick,
            'alignment': align,
            'back': back,
            'size': size,
            'special': special,
            'score': score,
            'name': f"{sil}_{tex}_{thick}_{size}_{special}",
        })

    designs.sort(key=lambda d: d['score'], reverse=True)
    print(f"Generated {len(designs):,} marker designs")
    return designs


def generate_tool_designs():
    """Generate all valid tool combinations and score them."""
    designs = []
    axes = [
        list(TOOL_FORM_FACTORS.keys()),
        list(TOOL_HANDLE_SHAPES.keys()),
        list(TOOL_PRONG_STYLES.keys()),
        list(TOOL_TEXTURES.keys()),
        list(TOOL_LENGTHS.keys()),
        list(TOOL_CONNECTIONS.keys()),
        list(TOOL_SPECIAL.keys()),
    ]

    total_combos = 1
    for a in axes:
        total_combos *= len(a)

    print(f"Tool design space: {total_combos:,} total combinations")

    for combo in itertools.product(*axes):
        form, handle, prong, tex, length, conn, special = combo
        score = score_tool(form, handle, prong, tex, length, conn, special)
        designs.append({
            'type': 'tool',
            'form_factor': form,
            'handle_shape': handle,
            'prong_style': prong,
            'texture': tex,
            'length': length,
            'connection': conn,
            'special': special,
            'score': score,
            'name': f"{form}_{handle}_{prong}_{tex}_{length}_{special}",
        })

    designs.sort(key=lambda d: d['score'], reverse=True)
    print(f"Generated {len(designs):,} tool designs")
    return designs


def cull(designs, target, ensure_diversity_key=None):
    """
    Cull a sorted list of designs to target count.
    If ensure_diversity_key is provided, ensures at least one representative
    from each unique value of that key.
    """
    if ensure_diversity_key:
        # First, take the best from each category
        seen = {}
        selected = []
        for d in designs:
            key = d[ensure_diversity_key]
            if key not in seen:
                seen[key] = True
                selected.append(d)

        # Fill remaining slots with top remaining designs
        selected_set = set(id(d) for d in selected)
        for d in designs:
            if len(selected) >= target:
                break
            if id(d) not in selected_set:
                selected.append(d)
                selected_set.add(id(d))

        selected.sort(key=lambda d: d['score'], reverse=True)
        return selected[:target]
    else:
        return designs[:target]


def select_final_five(designs, diversity_key):
    """
    Select final 5 designs ensuring each has a DIFFERENT primary attribute.
    This is the key constraint — no two products should share a silhouette/form.
    """
    selected = []
    used_keys = set()
    for d in designs:
        key = d[diversity_key]
        if key not in used_keys:
            used_keys.add(key)
            selected.append(d)
            if len(selected) >= 5:
                break
    return selected


def print_designs(designs, label, limit=10):
    """Pretty-print top designs."""
    print(f"\n{'='*70}")
    print(f"  {label} (showing top {min(limit, len(designs))} of {len(designs)})")
    print(f"{'='*70}")
    for i, d in enumerate(designs[:limit]):
        if d['type'] == 'marker':
            print(f"  #{i+1:3d} [{d['score']:5.1f}] {d['silhouette']:15s} | {d['texture']:15s} | "
                  f"{d['thickness']:7s} | {d['size']:7s} | {d['special']:15s}")
        else:
            print(f"  #{i+1:3d} [{d['score']:5.1f}] {d['form_factor']:12s} | {d['handle_shape']:10s} | "
                  f"{d['prong_style']:13s} | {d['texture']:15s} | {d['length']:10s} | {d['special']:15s}")
    print(f"{'='*70}\n")


def run_pipeline():
    """Full pipeline: generate → score → cull → select final 5+5."""

    print("\n" + "="*70)
    print("  MARSHAL GOLF — DESIGN SPACE EXPLORATION PIPELINE")
    print("  Keep Pace. Keep Peace.")
    print("="*70 + "\n")

    # --- MARKERS ---
    print("--- PHASE 1: BALL MARKER GENERATION ---\n")
    markers = generate_marker_designs()
    print_designs(markers, "ALL MARKERS — Top 10", 10)

    print("--- PHASE 2: MARKER CULLING (→ 500) ---")
    markers_500 = cull(markers, 500, ensure_diversity_key='silhouette')
    print(f"  Culled to {len(markers_500)} markers")
    print(f"  Score range: {markers_500[-1]['score']:.1f} — {markers_500[0]['score']:.1f}")

    print("\n--- PHASE 3: MARKER CULLING (→ 100) ---")
    markers_100 = cull(markers_500, 100, ensure_diversity_key='silhouette')
    print(f"  Culled to {len(markers_100)} markers")
    print(f"  Score range: {markers_100[-1]['score']:.1f} — {markers_100[0]['score']:.1f}")
    print_designs(markers_100, "TOP 100 MARKERS — First 20", 20)

    print("--- PHASE 4: FINAL 5 MARKERS ---")
    final_markers = select_final_five(markers_100, 'silhouette')
    print_designs(final_markers, "FINAL 5 MARKERS", 5)

    # --- TOOLS ---
    print("\n--- PHASE 5: DIVOT TOOL GENERATION ---\n")
    tools = generate_tool_designs()
    print_designs(tools, "ALL TOOLS — Top 10", 10)

    print("--- PHASE 6: TOOL CULLING (→ 500) ---")
    tools_500 = cull(tools, 500, ensure_diversity_key='form_factor')
    print(f"  Culled to {len(tools_500)} tools")
    print(f"  Score range: {tools_500[-1]['score']:.1f} — {tools_500[0]['score']:.1f}")

    print("\n--- PHASE 7: TOOL CULLING (→ 100) ---")
    tools_100 = cull(tools_500, 100, ensure_diversity_key='form_factor')
    print(f"  Culled to {len(tools_100)} tools")
    print(f"  Score range: {tools_100[-1]['score']:.1f} — {tools_100[0]['score']:.1f}")
    print_designs(tools_100, "TOP 100 TOOLS — First 20", 20)

    print("--- PHASE 8: FINAL 5 TOOLS ---")
    final_tools = select_final_five(tools_100, 'form_factor')
    print_designs(final_tools, "FINAL 5 TOOLS", 5)

    # --- SUMMARY ---
    print("\n" + "="*70)
    print("  FINAL SELECTION — THE AUTHORITY COLLECTION v2")
    print("="*70)

    print("\n  BALL MARKERS:")
    for i, d in enumerate(final_markers, 1):
        s = MARKER_SILHOUETTES[d['silhouette']]
        print(f"    {i}. The {d['silhouette'].title():15s} [{d['score']:.1f}]")
        print(f"       {s['story']}")
        print(f"       {d['texture']}, {d['thickness']}, {d['size']}, {d['special']}")
        print()

    print("  DIVOT TOOLS:")
    for i, d in enumerate(final_tools, 1):
        f = TOOL_FORM_FACTORS[d['form_factor']]
        print(f"    {i}. The {d['form_factor'].title():15s} [{d['score']:.1f}]")
        print(f"       {f['desc']}")
        print(f"       {d['handle_shape']}, {d['prong_style']}, {d['texture']}, {d['length']}")
        print()

    print("="*70 + "\n")

    return final_markers, final_tools


if __name__ == '__main__':
    final_markers, final_tools = run_pipeline()

    # Save results
    os.makedirs('output', exist_ok=True)
    results = {
        'markers': final_markers,
        'tools': final_tools,
    }
    with open('output/final_selection.json', 'w') as f:
        json.dump(results, f, indent=2)
    print("Saved final selection to output/final_selection.json")
