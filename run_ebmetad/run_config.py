from run_ebmetad.run_data import RunData
from run_ebmetad.pair_data import MultiPair
from run_ebmetad.plugin_configs import EBMetaDPluginConfig
from run_ebmetad.directory_helper import DirectoryHelper
from copy import deepcopy
import os
import logging
import gmx
import numpy as np


class RunConfig:
    """
    Run configuration for single EBMetaD ensemble member.
    """

    def __init__(self, tpr, ensemble_dir, ensemble_num=1, pairs_json='pair_data.json'):
        """
        The run configuration specifies the files and directory structure used for the run.
        :param tpr: path to tpr. Must be gmx 2017 compatible.
        :param ensemble_dir: path to top directory which contains the full ensemble.
        :param ensemble_num: the ensemble member to run.
        :param pairs_json: path to file containing *ALL* the pair metadata. An example of
        what such a file should look like is provided in the examples directory.

        :
        """
        self.tpr = tpr
        self.ens_dir = ensemble_dir

        # a list of identifiers of the residue-residue pairs that will be restrained
        self.__names = []

        # Load the pair data from a json. Use this to set up the run metadata
        self.pairs = MultiPair()
        self.pairs.read_from_json(pairs_json)
        # use the same identifiers for the pairs here as those provided in the pair metadata
        # file this prevents mixing up pair data amongst the different pairs (i.e.,
        # accidentally applying the restraints for pair 1 to pair 2.)
        self.__names = self.pairs.get_names()

        self.run_data = RunData()

        # Set up run data for each pair
        self.run_data.set(ensemble_num=ensemble_num)
        for pd in self.pairs:
            self.run_data.from_pair_data(pd)
        self.run_data.save_config('run_config.json')

        # List of plugins
        self.__plugins = []

        # Logging
        self._logger = logging.getLogger('EBMetaD')
        self._logger.setLevel(logging.DEBUG)
        # create file handler which logs even debug messages
        fh = logging.FileHandler('ebmetad{}.log'.format(ensemble_num))
        fh.setLevel(logging.DEBUG)
        # create console handler with a higher log level
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        # create formatter and add it to the handlers
        formatter = logging.Formatter('%(asctime)s:%(name)s:%(levelname)s - %(message)s')
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)
        # add the handlers to the logger
        self._logger.addHandler(fh)
        self._logger.addHandler(ch)

        self._logger.info("Names of restraints: {}".format(self.__names))

    def __calculate_force_table(self):
        # TODO: test this properly in pytest.
        for i in range(self.pairs.num_pairs):
            pd = self.pairs[i]
            name = pd.name

            w = self.run_data.get('w', name=name)
            sigma = self.run_data.get('sigma', name=name)
            self.run_data.set(name=name, force_table=pd.build_force_table(w, sigma))
        self.run_data.save_config(fnm='run_config.json')

    def build_plugins(self, plugin_config):
        # One plugin per restraint.
        # TODO: what is the expected behavior when a list of plugins exists? Probably wipe them.

        self.__plugins = []
        general_params = self.run_data.as_dictionary()['general parameters']
        self.__calculate_force_table()

        # For each pair-wise restraint, populate the plugin with data: both the "general" data and
        # the data unique to that restraint.
        for name in self.__names:

            # We assume we've changed into the working directory. Therefore, we can check to see if a historical data
            # file exists. If it does, we read it, if is does not, we initialize a vector of all zero counts.

            hist_data_fnm = self.run_data.get('historical_data_filename', name=name)
            if os.path.exists(hist_data_fnm):
                distance_counts = np.loadtxt(hist_data_fnm, dtype=int).tolist()
            else:
                num_bins = len(self.run_data.get('force_table', name=name))
                distance_counts = [1] * num_bins

            self.run_data.set(name=name, distance_counts=distance_counts)

            pair_params = self.run_data.as_dictionary()['pair parameters'][name]
            new_restraint = deepcopy(plugin_config)
            new_restraint.scan_dictionary(general_params)  # load general data into current restraint
            new_restraint.scan_dictionary(pair_params)  # load pair-specific data into current restraint
            self.__plugins.append(new_restraint.build_plugin())

    def __change_directory(self):
        # change into the current working directory (ensemble_path/member_path/)
        dir_help = DirectoryHelper(top_dir=self.ens_dir, ensemble_num=self.run_data.get('ensemble_num'))
        dir_help.build_working_dir()
        dir_help.change_dir('ensemble_num')

    def __production(self, nsteps=None):
        if nsteps:
            md = gmx.workflow.from_tpr(self.tpr, append_output=False, nsteps=nsteps)
        else:
            md = gmx.workflow.from_tpr(self.tpr, append_output=False)

        self.build_plugins(EBMetaDPluginConfig())
        for plugin in self.__plugins:
            md.add_dependency(plugin)
        context = gmx.context.ParallelArrayContext(md, workdir_list=[os.getcwd()])
        with context as session:
            session.run()

    def run(self, nsteps=None):
        self.__change_directory()
        self.__production(nsteps=nsteps)
        self.run_data.save_config('run_config.json')
