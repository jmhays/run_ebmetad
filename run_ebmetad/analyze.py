"""
Classes to analyze the output of EBMetaD runs.
"""

from run_ebmetad.pair_data import MetaData, PairData, MultiMetaData, MultiPair
import json
from scipy.stats import entropy
import numpy as np


"""
First, some useful analysis functions.
"""


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
    norm = 1 / (2 * np.pi * sigma**2 * np.sum(weights))
    for i in range(num_bins):
        for j in range(num_bins):
            arg_exp = -(values[j] - values[i])**2 / (2 * sigma**2)
            hist[i] += weights[j] * np.exp(arg_exp)
        hist[i] *= norm
    return hist


def js(p, q):
    """
    Pairwise Jensen-Shannon Divergence
    Args:
        p: first probability distribution
        q: second probability distribution

    Returns: J-S Divergence of p and q

    """

    # convert to np.array
    p, q = np.asarray(p), np.asarray(q)

    # normalize p, q to probabilities
    p, q = p/p.sum(), q/q.sum()
    m = 1./2*(p + q)

    return entropy(p,m)/2. + entropy(q, m)/2.


"""
Analysis classes specific to EBMetaD data.
"""


class AnalysisData(MetaData):
    """
    Handles a single pair
    """
    def __init__(self, name):
        super().__init__(name)
        self.set_requirements(['exp_distribution', 'sim_counts', 'sim_distributions', 'bins', 'js'])
        self.avg_js = 0

    def load_exp_data(self, pd: PairData):
        self.set('exp_distribution', pd.get('distribution'))
        self.set('bins', pd.get('bins'))

    def load_sim_data(self, md: MetaData, sigma=0.2):
        """
        Load simulation metadata. For EBMetaD, this will be the counts of distances observed in simulation.
        Args:
            md:
            sigma:

        Returns:

        """
        sim_distributions = {}
        bins = self.get('bins')
        ens_avg = np.zeros(shape=(len(bins)))

        count_data = md.get_as_dictionary()
        for member_number, counts in count_data.items():
            sim_distributions[member_number] = gaussian_smoothing(counts, bins, sigma)
            ens_avg += sim_distributions[member_number]
        ens_avg /= np.sum(ens_avg)
        self.set('sim_distributions', sim_distributions)
        self.set('ensemble_avg_distribution', ens_avg.tolist())

    def do_js(self):
        js_dict = {}
        js_total = 0
        for key, value in self.get('sim_distributions').items():
            js_dict[key] = js(value, self.get('exp_distribution'))
            js_total += js_dict[key]

        self.set('js', js_dict)
        self.avg_js = js_total/len(js_dict)


class MultiPairAnalysis(MultiMetaData):
    def __init__(self):
        super().__init__()

    def __create_metadata_from_names(self, names):
        self.set_names(names)
        for name in names:
            self._metadata_list.append(AnalysisData(name=name))

    def load_sim_data(self, filename, sigma=0.2):
        """
        Loads simulation data into dictionary.
        Args:
            filename (str): a json containing simulation data. The structure should be as follows:
               {'pair_name': {'ensemble_num': [list of counts from simulation] ... }}
            sigma (float): Gaussian smoothing parameter.

        Notes:
            - The 'pair name' should be the same as the 'pair_name' from the experimental file.
            - We keep the different ensemble member counts separate so that we can analyze individual ensemble members
            in addition to the full ensemble.
            - the list of counts is just the data contained in the "counts_{}.log" files that are written out by the
            simulation (specifically, these files are written by the EBMetaD plugin provided in the sample_restraint
            repository.
        """
        raw_data = json.load(open(filename))

        # If no experimental data has been loaded yet, must create all the metadata objects here.
        if not self._metadata_list:
            self.__create_metadata_from_names(list(raw_data.keys()))

        for name, data in raw_data.items():
            md = MetaData(name=name)
            md.set_from_dictionary(data=data)

            id = self.name_to_id(name)
            self._metadata_list[id].load_sim_data(md, sigma=sigma)

    def load_experimental_data(self, filename):
        """
        Loads experimental DEER data.
        Args:
            filename (str): json file containing the experimental data.

        Notes:
            The structure of the json file here should be the same as the pair_data.json file you used to perform the
            runs.
        """

        pds = MultiPair()
        pds.read_from_json(filename)

        if not self._metadata_list:
            self.__create_metadata_from_names(pds.get_names())

        for pd in pds:
            id = self.name_to_id(pd.name)
            self._metadata_list[id].load_exp_data(pd)

    def js(self):
        for name in self.get_names():
            idx = self.name_to_id(name=name)
            self._metadata_list[idx].do_js()

    def get(self, key, name=None):
        if not name:
            name = self.get_names()[0]
            print("Warning: because you did not provide a name, "
                  "pulling {} from arbitrary pair {}".format(key, name))
        idx = self.name_to_id(name)
        return self._metadata_list[idx].get(key)