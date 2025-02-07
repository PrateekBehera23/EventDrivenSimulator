from queue import Queue
from typing import Union
from collections import OrderedDict
from files import File

class CacheConstruction:
    @staticmethod
    def new(configure_simulation):
        cache_replacement_policy = configure_simulation.get("cache_replacement_policy")
        cache_size = configure_simulation.getfloat("cache_capacity")
        if cache_replacement_policy == "LRU":
            return LeastPopularFirstCache(cache_size)
        elif cache_replacement_policy == "FIFO":
            return FIFOCacheMethod(cache_size)
        elif cache_replacement_policy == "LF":
            return LargestFirstCacheMethod(cache_size)
        else:
            raise "Invalid cache type! Please select from one of the following caches replacement policies: 1)FIFO 2)LRU 3)LF"

class FIFOCacheMethod:
    """
    FIFO Cache
    """
    def __init__(self, cache_size):
        self.cache_size = cache_size
        self.cache = {}
        self.cache_queue = Queue()

    def get(self, file: File) -> File:
        return self.cache.get(file.serial_id, None)

    def size(self):
        return sum(map(lambda x: x.size, self.cache.values()))

    def add(self, file: File):
        if file.serial_id in self.cache:
            return
        size1 = self.size()
        while size1 + file.size >= self.cache_size:
            if not self.cache_queue:
                return
            val_tempk = self.cache_queue.get()
            if val_tempk in self.cache:
                size1 -= self.cache[val_tempk].size
                del self.cache[val_tempk]
        self.cache[file.serial_id] = file
        self.cache_queue.put(file.serial_id)


class LeastPopularFirstCache:
    """
    Oldest First / Least Popular or LRU
    """

    cache_size: float
    cache: OrderedDict

    def __init__(self, cache_size: float):
        self.cache_size = cache_size
        self.cache = OrderedDict()

    def size(self):
        return sum(map(lambda x: x.size, self.cache.values()))

    def get(self, file: File) -> Union[File, None]:
        if file.serial_id in self.cache:
            self.cache.move_to_end(file.serial_id)
            return self.cache[file.serial_id]
        else:
            return None

    def add(self, file: File):
        if file.serial_id in self.cache:
            return
        self.cache[file.serial_id] = file
        self.cache.move_to_end(file.serial_id)
        size1 = self.size()
        while size1 >= self.cache_size:
            (_, item) = self.cache.popitem(last=False)
            size1 -= item.size


class LargestFirstCacheMethod:
    cache_size: float
    cache: dict

    def __init__(self, cache_size: float):
        self.cache_size = cache_size
        self.cache = {}

    def size(self):
        return sum(map(lambda x: x.size, self.cache.values()))

    def get(self, file: File) -> Union[File, None]:
        if file.serial_id in self.cache:
            return self.cache[file.serial_id]
        else:
            return None

    def add(self, file: File):
        if file.serial_id in self.cache:
            return
        size1 = self.size()
        while size1 + file.size >= self.cache_size:
            if not self.cache:
                return
            largest = max(self.cache, key=(lambda x: self.cache[x].size))
            size1 -= self.cache[largest].size
            del self.cache[largest]
        self.cache[file.serial_id] = file