# run-EBMetaD
[![Build Status](https://travis-ci.org/jmhays/run_ebmetad.svg?branch=master)](https://travis-ci.org/jmhays/run_ebmetad)
[![codecov](https://codecov.io/gh/jmhays/run_ebmetad/branch/master/graph/badge.svg)](https://codecov.io/gh/jmhays/run_ebmetad)
[![https://www.singularity-hub.org/static/img/hosted-singularity--hub-%23e32929.svg](https://www.singularity-hub.org/static/img/hosted-singularity--hub-%23e32929.svg)](https://singularity-hub.org/collections/1654)

Set of scripts for running EBMetaD simulations using gmxapi. 

## Installation
### Requirements
- Python 3.X
- An installation of [gmxapi](https://github.com/kassonlab/gmxapi). This code has only been tested with [release 0.0.6](https://github.com/kassonlab/gmxapi/releases/tag/v0.0.6).
- The [plugin code](https://github.com/jmhays/sample_restraint) for EBMetaD. Please make sure you install the `ebmetad` branch, _*NOT*_ `master`.

### Installation of run_ebmetad
I suggest running this in a conda environment. The following conda command will handle all the `gmxapi` and `sample_restraint` python dependencies as well as the ones for this repository.

1. `conda create -n EBMetaD numpy scipy networkx setuptools mpi4py cmake`

    If you want to run tests, then install `pytest` as well.

2. `source activate EBMetaD`
3. `git clone` this repo.
4. Use the standard `setup.py` installation procedure: `python setup.py install`.

    You can test by running `python -m pytest` 

## Running EBMetaD
An example script is provided for ensemble simulations: `run.py`. More details coming...
