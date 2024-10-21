import random
import statistics
from scipy.spatial.distance import hamming
from .experiment_hdf5 import Read



class StatisticMethod:
    """
    Makes it easier to iterate over all relevant stat methods,
    without using a singleton dict
    """
    statistic_methods = {
        "Mean": statistics.mean,
        "Median": statistics.median,
        "Variance": statistics.variance,
        "StdDeviation": statistics.stdev,
        "Minimum": min,
        "Maximum": max
    }

def entropy_list(reads: list[Read]) -> list[float]:
    # TODO Test
    return [read.entropy for read in reads]

def intradistance_bootstrap(reads: list[Read]) -> list[float]:
    # TODO Test
    distance_values = list()
    for _ in range(len(reads)):
        idx1 = random.randrange(0, len(reads))
        while (idx2 := random.randrange(0, len(reads))) == idx1:
            idx2 = random.randrange(0, len(reads))
        distance_values.append(hamming(reads[idx1].bits_flatted, reads[idx2].bits_flatted))
    return distance_values

def interdistance_bootstrap(reads: list[Read], other_reads: list[Read], k: int) -> list[float]:
    # TODO Test
    self_choices = [
        choice.bits_flatted for choice in
        random.choices(reads, k=k)
    ]
    other_choices =  [
        choice.bits_flatted for choice in
        random.choices(other_reads, k=k)
    ]
    return map(hamming, self_choices, other_choices)

