import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import random
import time
import argparse
import configparser
import heapq
import logging
from typing import List, Union

from cache import CacheConstruction
from event import Event, RequestNewFileEvent, RecieveFileEvent
from files import FileList
from parameters import ConfigureParameters, StoreStatistics

logger = logging.getLogger("Sim")
logging.basicConfig()

FILES_LIST: Union[FileList, None] = None
TIME_NOW = 0
ACTION_QUEUE: List[Event] = []
CACHE_BUFFER = None
SEED_VALUE = None
INPUT_FILE = None
    

def main(configure_simulation):
    global ACTION_QUEUE, TIME_NOW, FILES_LIST, CACHE_BUFFER
    total_reqs = configure_simulation.getint("total_no_of_requests")
    max_time = configure_simulation.getfloat("max_time")
    completed_requests = 0

    temp = configure_simulation.getfloat("pareto_alpha")#pareto shape
    number_of_files = configure_simulation.getint("number_of_files")

    file_sizes = ConfigureParameters.rand_num_gen.pareto(temp, number_of_files)

    probabilities = ConfigureParameters.rand_num_gen.pareto(temp, number_of_files)
    total_prob = sum(probabilities)

    FILES_LIST = FileList(
        [
            (i, size, probability_val / total_prob)
            for (i, size, probability_val) in zip(range(number_of_files), file_sizes, probabilities)
        ]
    )

    CACHE_BUFFER = CacheConstruction.new(configure_simulation)

    print("Inputs:")
    print("Input Parameters For Network Simulation:")
    for key, value in ConfigureParameters.SIMULATION_INPUTS.items():
        print(f"{key}\t=\t{value}")
    print()
    print("Show Plot or Not?")
    for key, value in ConfigureParameters.SHOW_PLOT_CONFIG.items():
        print(f"{key}\t=\t{value}")

    heapq.heappush(ACTION_QUEUE, RequestNewFileEvent(TIME_NOW, FileList.file_sampler()))

    begin_time = time.time()
    counter_event = 0
    if max_time == None:
       max_time = 0
    while completed_requests < total_reqs or TIME_NOW < max_time:
        event = heapq.heappop(ACTION_QUEUE)
        TIME_NOW = event.time
        event.process_action(ACTION_QUEUE, CACHE_BUFFER, TIME_NOW)
        counter_event += 1
        if isinstance(event, RecieveFileEvent):
            completed_requests += 1
    print()
    print(
        f"Simulation finished in {time.time() - begin_time} seconds, processing {completed_requests} requests and {counter_event} events"
    )
    hit_rate_cache = StoreStatistics.total_cache_hits / completed_requests
    miss_rate_cache = 1 - hit_rate_cache

    req_rate = ConfigureParameters.SIMULATION_INPUTS.getfloat("file_request_rate")
    access_bw = ConfigureParameters.SIMULATION_INPUTS.getfloat("access_link_bandwidth")

    print("Average File Size:", FileList.avg())

    print("Cache Hit Rate: ", hit_rate_cache)

    print("Cache Miss Rate: ", miss_rate_cache)

    print("Traffic (In-bound):", miss_rate_cache * req_rate, "requests / second")

    print("Avg Access Link Use/Load:",miss_rate_cache * req_rate * FileList.avg() / access_bw)

    print()
    print()

    avg_resp_time_final = pd.DataFrame(StoreStatistics.response_times).mean()

    print("Average Response Time ",avg_resp_time_final.values)

    print()

    resp_time_len = range(len(StoreStatistics.response_times))
    resp_time = StoreStatistics.response_times
    categ = list(map(lambda resp_time_len: "orange" if resp_time_len else "green", StoreStatistics.hits_c))
    df = pd.DataFrame(
        {
            "resp_time_len": np.array(resp_time_len).flatten(),
            "resp_time": np.array(resp_time).flatten(),
            "categ": np.array(categ).flatten(),
        }
    )

    #print("df: ",df)
    #print("resp_time_len: ",resp_time_len)
    for i, dff in df.groupby("categ"):
        label = "Found in Cache" if dff.iloc[0, 0] else "Cache Miss"
        plt.scatter(dff["resp_time_len"], dff["resp_time"], 1, dff["categ"], label=label)
    plt.xlabel("Requests")
    plt.ylabel("Response Time")
    plt.legend()
    plt.title("Tracking if data is found in Cache")
    plt.savefig(f"{INPUT_FILE}_scatter_plot.png")

    plt.clf()
    hist_vals = pd.Series(resp_time)
    hist_vals = hist_vals[hist_vals.between(hist_vals.quantile(0.05), hist_vals.quantile(0.95))]
    plt.hist(hist_vals, 50)
    plt.xlabel("Response Time")
    plt.ylabel("Count")
    plt.savefig(f"{INPUT_FILE}_histogram.png")


if __name__ == "__main__":
    pars = argparse.ArgumentParser(description="Event-Driven Simulator for Network Cache System")
    pars.add_argument(
        "input",
        metavar="input",
        type=str,
        help="Input text file containing parameters to simulate from",
    )
    pars.add_argument(
        "seed", metavar="seed", type=int, help="Seed to carry out simulationn"
    )
    args = pars.parse_args()
    config = configparser.ConfigParser()
    config.read(args.input)

    INPUT_FILE = args.input
    SEED_VALUE = args.seed
    random.seed(args.seed)
    ConfigureParameters(config, args.seed)

    if "Plots" in config:
        if ConfigureParameters.SHOW_PLOT_CONFIG.getboolean("save_plot"):
            logger.setLevel(logging.DEBUG)

    main(config["Data For Network Simulation Here"])
