import itertools
import numpy as np
import random
import json
import textwrap
from math import comb
from tqdm import tqdm


class TrustsetGenerator:
    def __init__(self, node_positions, fraction=2/3, max_trustsets=100000, seed=42):
        self.node_positions = node_positions
        self.fraction = fraction
        self.max_trustsets = max_trustsets
        self.seed = seed
        self.total_combinations = self.calculate_total_combinations()
        self.sample_probability = self.calculate_sample_probability(max_trustsets)
        self.expected_combinations = self.calculate_expected_combinations(max_trustsets)
        self.reservoir = self.build_reservoir()

        print(textwrap.dedent(f"""
            ===================================================================
            Total combinations {self.total_combinations}
            Expected combinations {self.expected_combinations}
            Sample probability {self.sample_probability}
            ===================================================================
        """))

    def calculate_total_combinations(self):
        total_nodes = len(self.node_positions)
        trustset_size = int(total_nodes * self.fraction)
        return comb(total_nodes, trustset_size)

    def calculate_sample_probability(self, max_trustsets):
        return min(1, max_trustsets / self.total_combinations)
    
    def calculate_expected_combinations(self, max_trustsets):
        try:
            expected_combinations = self.total_combinations * self.sample_probability
        except OverflowError as e:
            expected_combinations = max_trustsets
        return int(expected_combinations) if expected_combinations < float('inf') else max_trustsets

    def build_reservoir(self):
        node_ids = list(self.node_positions.keys())
        total_nodes = len(node_ids)
        trustset_size = int(total_nodes * self.fraction)
        rng = np.random.default_rng(self.seed)
        
        reservoir = set()
        with tqdm(total=self.expected_combinations, desc="Building Reservoir") as pbar:
            while len(reservoir) < self.expected_combinations:
                sample = rng.choice(total_nodes, trustset_size, replace=False)
                combination = frozenset(int(node_ids[i]) for i in sample)
                if combination not in reservoir:
                    reservoir.add(combination)
                    pbar.update(1)
        
        return reservoir
    
    def generator(self):
        for trustset in self.reservoir:
            yield trustset

    def __iter__(self):
        return self.generator()


def create_trustsets(node_positions, fraction=2/3, allow_overlap=True):
    node_ids = list(node_positions.keys())
    total_nodes = len(node_ids)
    trustset_size = int(total_nodes * fraction)

    trustsets = set()

    if allow_overlap:
        for combination in itertools.combinations(node_ids, trustset_size):
            trustsets.add(frozenset(combination))
    else:
        random.shuffle(node_ids)
        for i in range(0, total_nodes, trustset_size):
            trustset = node_ids[i:i+trustset_size]
            if len(trustset) == trustset_size:
                trustsets.add(frozenset(trustset))
    
    # trustsets.add(frozenset([34, 2, 4]))
    return trustsets


def trustset_generator_factory(node_positions, fraction=2/3):
    def generator():
        node_ids = list(node_positions.keys())
        total_nodes = len(node_ids)
        trustset_size = int(total_nodes * fraction)

        for combination in itertools.combinations(node_ids, trustset_size):
            yield frozenset(combination)

    return generator


def trustset_generator_factory_random(node_positions, fraction=2/3, sample_probability=0.01, seed=42):
    def generator():
        node_ids = list(node_positions.keys())
        total_nodes = len(node_ids)
        trustset_size = int(total_nodes * fraction)
        rng = random.Random(seed)

        for combination in itertools.combinations(node_ids, trustset_size):
            if rng.random() < sample_probability:
                yield frozenset(combination)

    return generator


def create_malicious_parties(node_positions, num_malicious):
    node_ids = list(node_positions.keys())
    
    if num_malicious > len(node_ids):
        raise ValueError("Number of malicious nodes cannot exceed the total number of nodes")
    
    malicious_nodes = set(random.sample(node_ids, num_malicious))
    
    return malicious_nodes


def save_trustsets(trustsets, filename='trustsets.json'):
    trustsets_list = [list(trustset) for trustset in trustsets]
    with open(filename, 'w') as f:
        json.dump(trustsets_list, f)


def load_trustsets(filename='trustsets.json'):
    with open(filename, 'r') as f:
        trustsets_list = json.load(f)
    trustsets = set(frozenset(trustset) for trustset in trustsets_list)
    return trustsets
