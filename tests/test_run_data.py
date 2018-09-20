from run_ebmetad.run_data import RunData
from tests.test_pair_data import multi_pair_data, raw_pair_data
from tests.test_pair_data import data_dir
import pytest


@pytest.fixture()
def run_data(multi_pair_data):
    """
    Constructs a RunData object from pair data.
    :param multi_pair_data: MultiPair object used for initialization.
    :return: Initialized RunData obj.
    """
    run_data = RunData()
    for name in multi_pair_data.get_names():
        idx = multi_pair_data.name_to_id(name)
        run_data.from_pair_data(multi_pair_data[idx])
    return run_data


def test_missing_keys(run_data):
    """
    Checks that there are no missing keys after initialization of RunData object.
    :param run_data: example RunData object.
    """
    assert (not run_data.general_params.get_missing_keys())


def test_pair_parameters(run_data):
    assert (set(
        run_data.pair_params.keys()) == {'196_228', '105_216', '052_210'})


def test_general_parameters(run_data):
    assert (run_data.general_params.get_requirements() == [
        'w', 'sigma', 'sample_period', 'k', 'ensemble_num'
    ])
