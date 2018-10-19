"""
Classes to analyze the output of EBMetaD runs.
"""

from run_ebmetad.pair_data import MultiPair, MetaData, MultiMetaData
import json
import numpy as np


def gaussian_smoothing(weights, values, sigma=0.2):
    """

    Args:
        weights (list): these can be either counts or probabilities of observing a particular distance value.
        values (list): the distance values associated with the weights.
        sigma (float): Gaussian smoothing parameter

    Returns:
        hist: a smoothed histogram of the input data (the distance values and their associated weights)

    Notes:
        Because we store a log of COUNTS rather than raw distance data, the gaussian smoothing for the EBMetaD analysis
        will look like the gaussian smoothing we do for the DEER probability distributions. Do NOT use this gaussian
        smoothing function for BRER analysis.
    """

    num_bins = len(weights)
    if num_bins != len(values):
        raise IndexError('The number of weights ({}) does not equal the number of values ({})'.format(
            num_bins, len(values)))
    hist = [0] * num_bins
    norm = 1 / (2 * np.pi * sigma**2)
    for i in range(num_bins):
        for j in range(num_bins):
            arg_exp = -(values[j] - values[i])**2 / (2 * sigma**2)
            hist[i] += weights[j] * np.exp(arg_exp)
        hist[i] *= norm
    return hist


class SmoothedData(MetaData):
    def __init__(self, name):
        super().__init__(name)
        self.set_requirements(['experimental', 'simulation', 'bins'])

    def get_ensemble_counts(self):
        """
        Calculates the ensemble simulation distributions for each pair
        Returns:
            total_counts (dict): ensemble simulation distribution data for each pair. Structure is:
                                {'pair_name': [ensemble distribution], ...}

        """

        sim_data = self.get('simulation')
        num_bins = len(self.get('bins'))

        for pair in list(sim_data.keys()):
            total_counts[pair] = np.zeros(shape=(num_bins, 1))
            for data in self.values():
                total_counts[pair] += data
        return total_counts


class SmoothedMultiData(MultiMetaData):
    def __init__(self):
        super().__init__()

    def load_simulation_data(self, filename):
        """
        Loads simulation data into dictionary.
        Args:
            filename (str): a json containing simulation data. The structure should be as follows:
               {'pair_name': {'ensemble_num': [list of counts from simulation] ... }}

        Notes:
            - The 'pair name' should be the same as the 'pair_name' from the experimental file.
            - We keep the different ensemble member counts separate so that we can analyze individual ensemble members
            in addition to the full ensemble.
            - the list of counts is just the data contained in the "counts_{}.log" files that are written out by the
            simulation (specifically, these files are written by the EBMetaD plugin provided in the sample_restraint
            repository.
        """
        self.sim = json.load(filename)

    def load_experimental_data(self, filename):
        """
        Loads experimental DEER data.
        Args:
            filename (str): json file containing the experimental data.

        Notes:
            The structure of the json file here should be the same as the pair_data.json file you used to perform the
            runs.
        """

        self._exp.read_from_json(filename)
        self._num_bins = len(self._exp[0].get('bins'))





