#!/bin/bash
set -ev

pushd $HOME
 [ -d run_ebmetad ] || git clone --depth=1 --no-single-branch https://github.com/jmhays/run_ebmetad.git
 pushd run_ebmetad
  git branch -a
  git checkout master
  $PYTHON setup.py install
  PYTHONPATH=../sample_restraint/build/src/pythonmodule $PYTHON -m pytest --cov=./src
 popd
popd
