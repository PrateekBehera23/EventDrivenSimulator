import configparser
import numpy as np
from typing import List

class ConfigureParameters:

    SIMULATION_INPUTS: configparser.SectionProxy
    SHOW_PLOT_CONFIG: configparser.SectionProxy
    rand_num_gen = None

    def __init__(self, config, seed = 0):
        ConfigureParameters.rand_num_gen = np.random.default_rng(seed)
        if "Data For Network Simulation Here" not in config:
            raise ValueError('"Data For Network Simulation Here" header not present in input file.')
        else:
            ConfigureParameters.SIMULATION_INPUTS = config["Data For Network Simulation Here"]
        if "Plots" in config:
            ConfigureParameters.SHOW_PLOT_CONFIG = config["Plots"]

class StoreStatistics:
    response_times: List[float] = []
    hits_c: List[bool] = []
    total_cache_hits: int = 0