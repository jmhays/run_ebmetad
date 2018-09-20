#!/bin/bash
set -ev

pushd $HOME
 [ -d run_ebmetad ] || git clone --depth=1 --no-single-branch https://github.com/jmhays/run_ebmetad.git
 pushd run_ebmetad
  git branch -a
  git checkout master
  mkdir build
  pushd build
    $PYTHON ../setup.py install
  popd
  pushd tests
   $PYTHON -m pytest
  popd
 popd
popd
