from parameters import ConfigureParameters, StoreStatistics
import heapq
from files import FileList, File
from dataclasses import dataclass, field
from typing import Any
from queue import Queue

@dataclass
class Event:
    time: float
    file: File
    preceding: Any = None
    content: Any = field(default_factory=dict)

    def __lt__(self, other):
        return self.time < other.time

    def __le__(self, other):
        return self.time <= other.time

@dataclass
class RequestNewFileEvent(Event):
    def process_action(self, cache_queue, cache, time_curr):
        if cache.get(self.file):
            net_bw = ConfigureParameters.SIMULATION_INPUTS.getfloat("network_bandwidth")
            heapq.heappush(
                cache_queue,
                RecieveFileEvent(
                    time_curr + (self.file.size / net_bw),
                    self.file,
                    self,
                    {"cache_hit": True},
                ),
            )
        else:
            cache_check_time = ConfigureParameters.SIMULATION_INPUTS.getfloat("cache_check_time")
            heapq.heappush(
                cache_queue,
                QueueArrivalEvent(time_curr + cache_check_time, self.file, self),
            )

        f_req_rate = ConfigureParameters.SIMULATION_INPUTS.getfloat("file_request_rate")
        poisson_val = ConfigureParameters.rand_num_gen.exponential(1 / f_req_rate)
        heapq.heappush(
            cache_queue,
            RequestNewFileEvent(time_curr + poisson_val, FileList.file_sampler()),
        )


@dataclass
class RecieveFileEvent(Event):
    def process_action(self, cache_queue, cache, time_curr):
        end_t = self.time
        prev = self.preceding
        while prev.preceding:
            prev = prev.preceding
        begin_t = prev.time
        StoreStatistics.response_times.append(end_t - begin_t)
        StoreStatistics.hits_c.append(self.content["cache_hit"])
        StoreStatistics.total_cache_hits += self.content["cache_hit"]
        return 1


QUEUE_FIFO: Queue = Queue()


@dataclass
class QueueArrivalEvent(Event):
    def process_action(self, cache_queue, cache, time_curr):
        if not QUEUE_FIFO.empty():
            QUEUE_FIFO.put((self.file, self))
        else:
            access_bw = ConfigureParameters.SIMULATION_INPUTS.getfloat("access_link_bandwidth")
            heapq.heappush(
                cache_queue,
                QueueDepartureEvent(
                    time_curr + (self.file.size / access_bw), self.file, self
                ),
            )


@dataclass
class QueueDepartureEvent(Event):
    def process_action(self, cache_queue, cache, time_curr):
        cache.add(self.file)
        net_bw = ConfigureParameters.SIMULATION_INPUTS.getfloat("network_bandwidth")
        heapq.heappush(
            cache_queue,
            RecieveFileEvent(
                time_curr + (self.file.size / net_bw),
                self.file,
                self,
                {"cache_hit": False},
            ),
        )
        if not QUEUE_FIFO.empty():
            (head, ev) = QUEUE_FIFO.get()
            access_bw = ConfigureParameters.SIMULATION_INPUTS.getfloat("access_link_bandwidth")
            heapq.heappush(
                cache_queue,
                QueueDepartureEvent(time_curr + (head.size / access_bw), head, ev),
            )