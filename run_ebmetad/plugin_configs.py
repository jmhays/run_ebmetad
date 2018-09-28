"""
Classes used to build gmxapi plugin for EBMetaD simulations.
Each class corresponds to ONE restraint since gmxapi plugins each correspond to one restraint.
"""

from run_ebmetad.metadata import MetaData
from abc import abstractmethod
import gmx


class PluginConfig(MetaData):
    def __init__(self):
        super().__init__('build_plugin')

    def scan_dictionary(self, dictionary):
        """
        Scans a dictionary and stores whatever parameters it needs for the build_plugin
        :param dictionary: a dictionary containing metadata, some of which may be needed for the run.
        The dictionary may contain *extra* data, i.e., this can be a superset of the needed plugin data.
        """
        for requirement in self.get_requirements():
            if requirement in dictionary.keys():
                self.set(requirement, dictionary[requirement])

    def scan_metadata(self, data):
        """
        This scans either a RunData or PairData obj and stores whatever parameters it needs for a run.
        :param data: either type RunData or type PairData
        """
        self.scan_dictionary(data.get_as_dictionary())

    def set_parameters(self, **kwargs):
        self.scan_dictionary(kwargs)

    @abstractmethod
    def build_plugin(self):
        pass


class EBMetaDPluginConfig(PluginConfig):
    def __init__(self):
        super(PluginConfig, self).__init__(name='ebmetad')
        self.set_requirements([
            'sites', 'force_table', 'distance_counts', 'bin_width', 'min_dist',
            'max_dist', 'k', 'sample_period', 'historical_data_filename'
        ])

    def build_plugin(self):
        if self.get_missing_keys():
            raise KeyError('Must define {}'.format(self.get_missing_keys()))
        print(self.get_as_dictionary().keys())
        potential = gmx.workflow.WorkElement(
            namespace="myplugin",
            operation="ebmetad_restraint",
            depends=[],
            params=self.get_as_dictionary())
        potential.name = '{}'.format(self.get('sites'))
        return potential
