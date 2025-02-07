import itertools
import logging
import random
from dataclasses import dataclass
from typing import List

logger = logging.getLogger("Sim")


@dataclass
class File:
    serial_id: int
    size: float  # MB
    probability_val: float


class FileList:
    files: List[File]
    cumulative_weights: List[float]

    def __init__(self, files):
        FileList.files = list(map(lambda x: File(*x), files))
        FileList.cumulative_weights = list(itertools.accumulate(map(lambda f: f.probability_val, FileList.files)))
        FileList.check_probs()

    @staticmethod
    def check_probs():
        """
        Check all probabilities sum to 1
        """
        probability_val = sum(map(lambda f: f.probability_val, FileList.files))
        avg_file_size = sum(map(lambda f: f.size, FileList.files)) / len(FileList.files)

        logger.debug(f"Sum probabilties: {probability_val}")
        logger.debug(f"Average file size: {avg_file_size}")

    @staticmethod
    def avg():
        return sum(map(lambda f: f.size, FileList.files)) / len(FileList.files)

    @staticmethod
    def size():
        return sum(map(lambda f: f.size, FileList.files))

    @staticmethod
    def file_sampler() -> File:
        return random.choices(FileList.files, cum_weights=FileList.cumulative_weights, k=1)[0]
