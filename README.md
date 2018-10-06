# run_EBMetaD

[![https://www.singularity-hub.org/static/img/hosted-singularity--hub-%23e32929.svg](https://www.singularity-hub.org/static/img/hosted-singularity--hub-%23e32929.svg)](https://singularity-hub.org/collections/1654)

master branch status:
[![Build Status](https://travis-ci.org/jmhays/run_ebmetad.svg?branch=master)](https://travis-ci.org/jmhays/run_ebmetad)
[![codecov](https://codecov.io/gh/jmhays/run_ebmetad/branch/master/graph/badge.svg)](https://codecov.io/gh/jmhays/run_ebmetad)

devel branch status:
[![Build Status](https://travis-ci.org/jmhays/run_ebmetad.svg?branch=master)](https://travis-ci.org/jmhays/run_ebmetad)
[![codecov](https://codecov.io/gh/jmhays/run_ebmetad/branch/master/graph/badge.svg)](https://codecov.io/gh/jmhays/run_ebmetad)

Set of scripts for running EBMetaD simulations using gmxapi. This respository may be used to run EBMetaD simulations according to the method described in:

Fabrizio Marinelli, José D. Faraldo-Gómez, Ensemble-Biased Metadynamics: A Molecular Simulation Method to Sample Experimental Distributions, Biophysical Journal, Volume 108, Issue 12, 2015, Pages 2779-2782, ISSN 0006-3495, https://doi.org/10.1016/j.bpj.2015.05.024.

## Installation
### Requirements
If you're going to use a conda environment, you'll need:
- Python 3.X
- An installation of [gmxapi](https://github.com/kassonlab/gmxapi). This code has only been tested with [release 0.0.6](https://github.com/kassonlab/gmxapi/releases/tag/v0.0.6).
- The [plugin code](https://github.com/jmhays/sample_restraint/tree/ebmetad) for EBMetaD. Please make sure you install the `ebmetad` branch, _*NOT*_ `master`.

Otherwise, you can just use a Singularity container!

### Singularity 
By far the easiest option! Just pull the container hosted on singularity hub:

`singularity pull -name myimage.simg shub://jmhays/singularity-ebmetad`

For instructions on using the container, please see [this](https://github.com/jmhays/singularity-ebmetad) repository
### Conda environment
I suggest running this in a conda environment rather than `pip install`. The following conda command will handle all the `gmxapi` and `sample_restraint` python dependencies, as well as the ones for this repository.

1. `conda create -n EBMetaD numpy scipy networkx setuptools mpi4py cmake`

    If you want to run the tests, then install `pytest` as well.

2. Source, the environment, then use the standard Python `setup.py` script provided:
```
source activate EBMetaD
git clone https://github.com/jmhays/run_ebmetad.git
cd run_ebmetad
python setup.py install
```


## Running EBMetaD
An example script, `run.py`, is provided for ensemble simulations. 

Let's work through it piece by piece.
```
#!/usr/bin/env python
"""
Example run script for EBMetaD simulations
"""

import run_ebmetad.run_config as rc
import sys

```
The `import run_ebmetad.run_config` statement imports a `RunConfig` object, which handles the following things _**for a single ensemble member**_:
1. Initializing/setting up parameters for the EBMetaD run, including `w` and `sigma`, the typical MetaDynamics parameters that specify the height and width of the Gaussians.
2. Launching the run. 

Next, we add the `gmxapi` plugin to the `PYTHONPATH`. You'll need to change this line of code to reflect where you have installed the `sample_restraint` repository.
```
sys.path.append('/builds/sample_restraint/build/src/pythonmodule')
```
Then we provide some files and directory paths to the `RunConfig` object. 
```
init = {
    'tpr': '/home/jennifer/Git/run_ebmetad/tests/data/topol.tpr',
    'ensemble_dir': '/home/jennifer/test-ebmetad',
    'ensemble_num': 5,
    'pairs_json': '/home/jennifer/Git/run_ebmetad/tests/data/pair_data.json'
}

config = rc.RunConfig(**init)
```

In order to run an EBMetaD simulation, we need to provide 
1. a `tpr` (compatible with GROMACS 2017).
2. The path to our ensemble. This directory should contain subdirectories of the form `mem_<my ensemble number>`
3. The ensemble number. This is an integer used to identify which ensemble member we are running and thus, the subdirectory in which we will be running our simulations.
4. The path to the DEER metadata. Please see the example json in this repository: `run_ebmetad/data/pair_data.json`

Finally, we launch the run!
```
config.run()
```

You may change various parameters before launching the run using `config.set(**kwargs)`, for example:
```
config = rc.RunConfig(**init)
config.set(w=10, sigma=0.5)
config.run()
```
would reset the values of `w` and `sigma` before launching the run.
