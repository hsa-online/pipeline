"""
Statistics holder.

"""

from core.singleton import Singleton
from core.sliding_window_stats import SlidingWindowStats

class ApplicationStatistics(metaclass=Singleton):
    NN_INFERENCE_TIME = "nn_inference_time"
    REQ_HANDLING_TIME = "req_handling_time"

    def __init__(self):
        self.__stats = {}

    def add_stats_holder(self, key: str, holder: SlidingWindowStats):
        if key in self.__stats:
            raise ValueError(f'statistics holder \"{key}\" already exists')

        self.__stats[key] = holder

    def get_stats_holder(self, key: str) -> SlidingWindowStats:
        if not key in self.__stats:
            raise ValueError(f'statistics holder \"{key}\" does not exist')

        return self.__stats[key]

    @staticmethod
    def setup_for_gw():
        stats = ApplicationStatistics()
        stats.add_stats_holder(ApplicationStatistics.REQ_HANDLING_TIME, SlidingWindowStats())

    @staticmethod
    def setup_for_work():
        stats = ApplicationStatistics()
        stats.add_stats_holder(ApplicationStatistics.NN_INFERENCE_TIME, SlidingWindowStats())
        stats.add_stats_holder(ApplicationStatistics.REQ_HANDLING_TIME, SlidingWindowStats())
