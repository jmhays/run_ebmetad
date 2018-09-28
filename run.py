#!/usr/bin/env python
"""
Example run script for EBMetaD simulations
"""

import run_ebmetad.run_config as rc
import sys

sys.path.append('/builds/sample_restraint/build/src/pythonmodule')

init = {
    'tpr': '/home/jennifer/Git/run_ebmetad/tests/data/topol.tpr',
    'ensemble_dir': '/home/jennifer/test-ebmetad',
    'ensemble_num': 5,
    'pairs_json': '/home/jennifer/Git/run_ebmetad/tests/data/pair_data.json'
}

config = rc.RunConfig(**init)

config.run()
