#!/usr/bin/env python3
"""
Marshal Golf — 3D Product Generator
Entry point for generating STL files.

Usage:
    python generate.py                        # generate full Authority Collection
    python generate.py --product marker_pennant
    python generate.py --product marker_hourglass
    python generate.py --product marker_wave
    python generate.py --product marker_tee
    python generate.py --product marker_disc
    python generate.py --product tool_classic
    python generate.py --product tool_wedge
    python generate.py --product tool_pennant
    python generate.py --validate output/MARSHAL-MKR-AUTH-PEN-BLK.stl
"""

import argparse
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from src.products import (
    marker_pennant, marker_hourglass, marker_wave, marker_tee, marker_disc,
    tool_classic, tool_wedge, tool_pennant,
    generate_authority_collection, save
)
from src.validate import validate_stl


PRODUCTS = {
    'marker_pennant':   (marker_pennant,   'marker'),
    'marker_hourglass': (marker_hourglass, 'marker'),
    'marker_wave':      (marker_wave,      'marker'),
    'marker_tee':       (marker_tee,       'marker'),
    'marker_disc':      (marker_disc,      'marker'),
    'tool_classic':     (tool_classic,     'tool'),
    'tool_wedge':       (tool_wedge,       'tool'),
    'tool_pennant':     (tool_pennant,     'tool'),
}


def main():
    parser = argparse.ArgumentParser(
        description='Marshal Golf — 3D STL Generator',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    parser.add_argument('--product', help='Product to generate (see usage above)')
    parser.add_argument('--validate', help='Path to STL file to validate')
    parser.add_argument('--type', default='marker', choices=['marker', 'tool'],
                        help='Product type for validation (default: marker)')
    parser.add_argument('--all', action='store_true',
                        help='Generate full Authority Collection (all 5 markers)')
    args = parser.parse_args()

    if args.validate:
        validate_stl(args.validate, product_type=args.type)
        return

    if args.product:
        if args.product not in PRODUCTS:
            print(f"Unknown product: {args.product}")
            print(f"Available: {', '.join(PRODUCTS.keys())}")
            sys.exit(1)
        fn, ptype = PRODUCTS[args.product]
        m = fn()
        path = save(m, args.product)
        validate_stl(path, product_type=ptype)
        return

    # Default: generate full collection
    generate_authority_collection()

    # Validate all generated markers
    print("\n=== Validating Authority Collection ===")
    sku_map = {
        'marker_pennant':   'MARSHAL-MKR-AUTH-PEN-BLK',
        'marker_hourglass': 'MARSHAL-MKR-AUTH-HRG-BLK',
        'marker_wave':      'MARSHAL-MKR-AUTH-WAV-BLK',
        'marker_tee':       'MARSHAL-MKR-AUTH-TEE-BLK',
        'marker_disc':      'MARSHAL-MKR-AUTH-STD-BLK',
    }
    for key, sku in sku_map.items():
        path = os.path.join('output', sku + '.stl')
        if os.path.exists(path):
            validate_stl(path, product_type='marker', verbose=True)


if __name__ == '__main__':
    main()
