"""
Class to analyze the distance distributions. Useful for comparing to experiment.
"""

from run_ebmetad.pair_data import MultiPair, PairData
import numpy as np
from scipy.stats import entropy


class SimulationPairData(PairData):
    def __init__(self, name):
        super().__init__(name)

        # For simulation pair data, you'll have one additional requirement...
        # The simulation data!
        requirements = self.get_requirements()
        requirements.append('simulation_data')
        requirements.append('simulation_distribution')
        self.set_requirements(requirements)

    def load_simulation_data(self, path_to_count_log):
        self.set('simulation_data', np.loadtxt(path_to_count_log))

    def gaussian_smoothing(self, sigma=0.2):
        """
        Because we store a log of COUNTS rather than raw distance data, the gaussian smoothing for the EBMetaD analysis
        will look like the gaussian smoothing we do for the DEER probability distributions. Do NOT use this gaussian
        smoothing function for BRER analysis.
        :return:
        """
        if not self.get('simulation_data'):
            raise KeyError("No simulation data has been loaded for pair {}".format(self.name()))
        sim_data = self.get('simulation_data')

        # The rows of the count log file correspond to the binned distances
        bins = self.get('bins')
        num_bins = len(bins)
        if num_bins != len(sim_data):
            raise IndexError(
                "The number of bins in the experimental histogram {} does not equal the number of bins in simulation "
                "count file {}".format(num_bins, len(sim_data)))
        hist = [0]*num_bins
        norm = 1/(2*np.pi*sigma**2)
        for i in range(num_bins):
            for j in range(num_bins):
                arg_exp = -(bins[j]-bins[i])**2/(2*sigma**2)
                hist[i] += sim_data[j] * np.exp(arg_exp)
            hist[i] *= norm
        self.set('simulation_distribution', np.array(hist))

    def js(self):
        p = np.asarray(self.get('simulation_distribution'))
        q = np.asarray(self.get('distribution'))
        # normalize
        p /= p.sum()
        q /= q.sum()
        m = (p + q) / 2
        return (entropy(p, m) + entropy(q, m)) / 2


class MultiSimData(MultiPair):
    def __init__(self):
        super().__init__()