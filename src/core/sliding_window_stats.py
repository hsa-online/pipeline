"""
Sliding Window statistics calculator.

"""

from typing import List

class SlidingWindowStats:
    """
    This class supports the Sliding Window based "average value" statistics computation. 
    """
    def __init__(self, window_size = 100, modifications_before_fix = 100000000):
        assert window_size > 1, \
            f"window size should be greater than 1, got: {window_size}"
        assert modifications_before_fix > 1, \
            f"modifications count should be greater than 1, got: {modifications_before_fix}"

        self.__window_size = window_size
        self.__modifications_before_fix = modifications_before_fix 

        self.__values = []
        self.__total = 0.0
        self.__total_is_valid = True
        self.__count_modifications = 0
        self.__count_values_handled = 0

    @property
    def count_values_handled(self) -> int:
        return self.__count_values_handled

    @property
    def average(self) -> float:
        if len(self.__values) == 0:
            return 0.0
        if not self.__total_is_valid:
            self.__compute_total()
        return self.__total / len(self.__values)

    def add_value(self, value: float) -> float:
        self.__count_values_handled += 1

        self.__ensure_place_available()
        self.__values.append(value)
        self.__value_is_added(value)

    def __ensure_place_available(self):
        if len(self.__values) == self.__window_size:
            self.__remove_oldest_value()

    def __remove_oldest_value(self):
        assert len(self.__values) > 0, "unable to remove from the empty sliding window"
        value_removed = self.__values.pop(0)
        self.__value_is_removed(value_removed)

    def __value_is_removed(self, value_removed: float):
        self.__total -= value_removed

    def __value_is_added(self, value_added: float):
        if self.__count_modifications == self.__modifications_before_fix:
            self.__modifications_limit_reached()
        else:
            self.__total += value_added
            self.__count_modifications += 1
 
    def __modifications_limit_reached(self):
        self.__total_is_valid = False

    def __compute_total(self):
        self.__total = 0.0
        for value in self.__values:
            self.__total += value

        self.__count_modifications = 0
        self.__total_is_valid = True
