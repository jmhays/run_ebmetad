from run_ebmetad.plugin_configs import EBMetaDPluginConfig
import os
import pytest


def test_build_plugins(rc):
    rc.build_plugins(EBMetaDPluginConfig())


def test_logger(rc):
    rc._logger.info("Testing the logger")


def test_run(rc):
    root_dir = os.path.abspath(os.getcwd())
    rc.run(nsteps=10)
    os.chdir(root_dir)
