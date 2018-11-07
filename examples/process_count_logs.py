#!/usr/bin/env python
"""
Simple script for processing count logs from multiple ensemble members
Generates a json file that can be used in conjunction with the Analysis 
classes in this package and with the plot.ipynb notebook in the examples
directory.
"""

import glob
import json
import os
import re
import argparse
import numpy


def get_ensemble_numbers(ensemble_dir):
    directories = glob.glob("{}/mem_*".format(ensemble_dir))
    if not directories:
        raise ValueError("{} is not a valid ensemble directory".format(ensemble_dir))
    mems = [re.search(r'mem_\d+', single_dir).group(0) for single_dir in directories]
    nums = [int(re.search(r'\d+', mem).group(0)) for mem in mems]
    return nums


def get_pairs(ensemble_dir, member_num):
    logs = glob.glob("{}/mem_{}/count*log".format(ensemble_dir, member_num))
    pair_strings = [re.search(r'\d+_\d+', log).group(0) for log in logs]
    return pair_strings


def load_sim_data(ensemble_dir, member_nums, pairs):
    simulation_data = {}
    for pair in pairs:
        simulation_data[pair] = {}
        for mem_num in member_nums:
            count_file = "{}/mem_{}/counts_{}.log".format(ensemble_dir, mem_num, pair)
            if os.path.exists(count_file):
                # Subtract one because had started with uniform prior
                counts = numpy.subtract(numpy.loadtxt(count_file), 1).tolist()
            else:
                print("WARNING: {} does not exist. This file will be skipped".format(count_file))
            if not counts:
                print("WARNING: {} is empty. This file will be skipped".format(count_file))
                break
            simulation_data[pair]['mem_{}'.format(mem_num)] = counts
    return simulation_data


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', required=True, help='ensemble directory')
    parser.add_argument('-o', help='output json file')
    args = parser.parse_args()
    ensemble_dir = args.f
    output_json = args.o

    nums = get_ensemble_numbers(ensemble_dir)
    pairs = get_pairs(ensemble_dir, nums[0])
    sim_data = load_sim_data(ensemble_dir, nums, pairs)
    json.dump(sim_data, open(output_json, "w"))


if __name__ == '__main__':
    main()
