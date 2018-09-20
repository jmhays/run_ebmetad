from run_ebmetad.run_config import RunConfig
from run_ebmetad.plugin_configs import EBMetaDPluginConfig
import os
import pytest
from tests.test_pair_data import data_dir


@pytest.fixture()
def rc(tmpdir, data_dir):
    init = {
        'tpr': '{}/topol.tpr'.format(data_dir),
        'ensemble_dir': tmpdir,
        'ensemble_num': 1,
        'pairs_json': '{}/pair_data.json'.format(data_dir)
    }
    return RunConfig(**init)


def test_build_plugins(rc):
    rc.build_plugins(EBMetaDPluginConfig())


def test_logger(rc):
    rc._logger.info("Testing the logger")
