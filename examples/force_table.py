#!/usr/bin/env python

"""
This code provides a method to perform sensitivity analysis of the Metadynamics parameters 'w' and 'sigma'.
"""

import run_ebmetad.pair_data as pd
import argparse
import sys
import json

sys.path.append('/home/jennifer/Git/sample_restraint/build/src/pythonmodule')


def force_table(weights=[0.1], sigmas=[0.2]):

    force_table = {}

    multi_pair = pd.MultiPair()
    multi_pair.read_from_json(args.f)

    # We'll make a whole bunch of these tables for different values of w and sigma
    for w in weights:
        for s in sigmas:
            key = 'w{}_s{}'.format(w, s)
            force_table[key] = {}

            for name in multi_pair.get_names():
                idx = multi_pair.name_to_id(name)
                ft = multi_pair[idx].build_force_table(w=w, sigma=s)
                force_table[key][name] = ft
    return force_table


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        "Builds a force table for specified w and sigma")
    parser.add_argument(
        '-f',
        help=
        'path to json of pair data; should include the smoothed DEER distribution and a '
        'list of associated distance bins. See pair_data.json in the tests/ directory'
    )
    parser.add_argument(
        '-w',
        nargs='+',
        help="weight, or height, of Gaussians (as in standard metadynmaics).",
        type=float)
    parser.add_argument(
        '-s', nargs='+', help="sigma. Width of Gaussians", type=float)
    parser.add_argument(
        '-o',
        help=
        "path to where the force table will be stored. For now, stored as json."
    )
    args = parser.parse_args()

    ft = force_table(weights=args.w, sigmas=args.s)
    json.dump(ft, open(args.o, 'w'), indent=2)
