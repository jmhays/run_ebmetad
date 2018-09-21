"""
Class that handles the simulation data for EBMetaD simulations
doi: 10.1016/j.bpj.2015.05.024
"""

from src.run_ebmetad.metadata import *
from src.run_ebmetad.pair_data import PairData
import numpy as np


def get_min_max(probs, bin_width):
    cutoff = 0.005
    max_dist = bin_width * (len(probs) - 1)
    min_dist = bin_width

    mask = np.array(probs) > cutoff
    for i in range(len(mask)):
        if mask[i]:
            min_dist = i * bin_width
            break
    for i in range(len(mask) - 1, 0, -1):
        if mask[i]:
            max_dist = i * bin_width
            break
        max_dist = (len(mask) - 1) * bin_width
    return min_dist, max_dist


class GeneralParams(MetaData):
    """
    Stores the parameters that are shared by all restraints in a single simulation.
    Includes the standard MetaDynamics parameters w, sigma, and the sampling interval, as well as the ensemble number.
    """

    def __init__(self):
        super().__init__('general')
        self.set_requirements(
            ['w', 'sigma', 'sample_period', 'k', 'ensemble_num'])


class PairParams(MetaData):
    """
    Stores the parameters that are unique to a specific restraint.
    Includes the history of distance counts (how many times the simulation has sampled a particular distance),
    the force table, and the atoms to be restrained.
    """

    def __init__(self, name):
        super().__init__(name)
        self.set_requirements([
            'sites', 'force_table', 'distance_counts', 'min_dist', 'max_dist',
            'bin_width', 'historical_data_filename'
        ])


class RunData:
    """
    Stores (and manipulates, to a lesser extent) all the metadata for a EBMetaD run.
    """

    def __init__(self):
        """
        The full set of metadata for a single EBMetaD run include both the general parameters
        and the pair-specific parameters.
        """
        self.general_params = GeneralParams()
        self.__defaults_general = {
            'w': 10,
            'k': 100,
            'sigma': 0.2,
            'sample_period': 500,
            'ensemble_num': 1
        }
        self.general_params.set_from_dictionary(self.__defaults_general)
        self.pair_params = {}
        self.__names = []

    def set(self, name=None, **kwargs):
        """
        method used to set either general or a pair-specific parameter.
        :param name: restraint name. These are the same identifiers that are used in the RunConfig
        :param kwargs: parameters and their values.
        """
        for key, value in kwargs.items():
            # If a restraint name is not specified, it is assumed that the parameter is a "general" parameter.
            if not name:
                if key in self.general_params.get_requirements():
                    self.general_params.set(key, value)
                else:
                    raise ValueError(
                        'You have provided a name; this means you are probably trying to set a '
                        'pair-specific parameter. {} is not pair-specific'.
                        format(key))
            else:
                if key in self.pair_params[name].get_requirements():
                    self.pair_params[name].set(key, value)
                else:
                    raise ValueError(
                        '{} is not a pair-specific parameter'.format(key))

    def get(self, key, name=None):
        """
        get either a general or a pair-specific parameter.
        :param key: the parameter to get.
        :param name: if getting a pair-specific parameter, specify the restraint name.
        :return: the parameter value.
        """
        if key in self.general_params.get_requirements():
            return self.general_params.get(key)
        elif name:
            return self.pair_params[name].get(key)
        else:
            raise ValueError(
                'You have not provided a name, but are trying to get a pair-specific parameter. '
                'Please provide a pair name')

    def as_dictionary(self):
        """
        Get the run metadata as a heirarchical dictionary:
        ├── pair parameters
        │   ├── name of pair 1
        │   │   ├── sites
        │   │   ├── force_table
        │   │   └── ...
        │   ├── name of pair 2
        |
        ├── general parameters
            ├── w
            ├── sigma
            ├── ...

        :return: heirarchical dictionary of metadata
        """
        pair_param_dict = {}
        for name in self.pair_params.keys():
            pair_param_dict[name] = self.pair_params[name].get_as_dictionary()

        return {
            'general parameters': self.general_params.get_as_dictionary(),
            'pair parameters': pair_param_dict
        }

    def from_dictionary(self, data):
        """
        Loads metadata into the class from a dictionary.
        :param data: RunData metadata as a dictionary.
        """
        self.general_params.set_from_dictionary(data['general parameters'])
        for name in data['pair parameters'].keys():
            self.pair_params[name] = PairParams(name)
            self.pair_params[name].set_from_dictionary(
                data['pair parameters'][name])

    def from_pair_data(self, pd: PairData):
        """
        Load some of the run metadata from a PairData object.
        :param pd: PairData object from which metadata are loaded
        """
        name = pd.name
        self.pair_params[name] = PairParams(name)

        # Atoms to be restrained
        self.pair_params[name].set('sites', pd.get('sites'))

        # Historical distance count filename
        self.pair_params[name].set('historical_data_filename',
                                   'counts_{}.log'.format(name))

        # Calculate the bin width
        bins = pd.get('bins')
        self.pair_params[name].set('bin_width', bins[1] - bins[0])

        # Calculate the min and max distances for turning off the the EBMetaD restraints (at boundaries)
        min_dist, max_dist = get_min_max(
            pd.get('distribution'), self.pair_params[name].get('bin_width'))
        self.pair_params[name].set('min_dist', min_dist)
        self.pair_params[name].set('max_dist', max_dist)

        # Calculate the force table
        self.pair_params[name].set(
            'force_table',
            pd.build_force_table(self.get('w', name), self.get('sigma', name)))

    def save_config(self, fnm='state.json'):
        json.dump(self.as_dictionary(), open(fnm, 'w'))

    def load_config(self, fnm='state.json'):
        self.from_dictionary(json.load(open(fnm)))
