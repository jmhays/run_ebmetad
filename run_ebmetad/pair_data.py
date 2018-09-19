"""
Classes to handle pair metadata
"""

import numpy as np
from run_ebmetad.metadata import MetaData, MultiMetaData
import json


def entropy(probs):
    S = 0
    for p in probs:
        if p > 1E-5:
            S += p * np.log(p)
    return S


class PairData(MetaData):
    def __init__(self, name):
        super().__init__(name=name)
        self.set_requirements(['distribution', 'bins', 'sites'])

    def build_force_table(self, w=10, sigma=0.2):

        dists = self.get('bins')
        probs = self.get('distribution')
        nbins = len(probs)

        force_table = np.zeros(shape=(nbins, nbins))

        # Calculate the effective volume pre-factor
        probs = np.divide(probs, np.sum(probs))  # Normalization, just in case
        effective_volume = np.exp(entropy(probs))

        # Calculate the full pre-factor
        pf = w / effective_volume / sigma**2

        for i in range(nbins):  # Current distance
            for j in range(nbins):  # Historical distances
                exponent = -(dists[i] - dists[j])**2 / sigma**2 / 2
                # add 1.0 to the probability so that we apply standard metadynamics when p_DEER(x) = 0.
                deer = 1. / (probs[j] + 1)
                # The distance better not ever be zero, so hopefully we don't have to worry about this case
                if 0 not in [dists[i], dists[j]]:
                    force_table[i, j] = pf * deer * (
                        1. - dists[j] / dists[i]) * np.exp(exponent)

        return force_table.tolist()


class MultiPair(MultiMetaData):
    def __init__(self):
        super().__init__()

    def read_from_json(self, filename='state.json'):
        self._metadata_list = []
        self._names = []
        data = json.load(open(filename, 'r'))
        for name, metadata in data.items():
            self._names.append(name)
            metadata_obj = PairData(name=name)
            metadata_obj.set_from_dictionary(metadata)
            self._metadata_list.append(metadata_obj)



