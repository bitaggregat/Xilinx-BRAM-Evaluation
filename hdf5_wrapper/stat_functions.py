import random
import numpy as np
import numpy.typing as npt
from scipy.spatial.distance import hamming
from .experiment_hdf5 import Read, ReadSession
from .utility import BitFlipType


def entropy_list(reads: list[Read]) -> npt.NDArray[np.float64]:
    """
    Produces list of entropy values (one for each Read object)
    """
    return np.fromiter((read.entropy for read in reads), np.float64)


def intradistance(reads: list[Read]) -> npt.NDArray[np.float64]:
    """
    Produces ((k+1)*k)/2 intradistance values
    (Each Read is compared with each other Read of the list)
    """
    reads_length = len(reads)
    return np.fromiter(
        (
            hamming(reads[i].bits_flattened, reads[j].bits_flattened)
            for i in range(len(reads_length))
            for j in range(i, len(reads_length))
        ),
        np.float64,
    )


def intradistance_bootstrap(
    reads: list[Read], k: int = 10000
) -> npt.NDArray[np.float64]:
    """
    Produces k intradistance values or the maximum, if the maximum of
    possible values (without pair duplicates) is smaller than k

    Pairs of values are chosen pseudo randomly.
    Duplicates can occur

    Less compute time expensive alternative to "intradistance"
    """
    k = int(min(k, ((len(reads) ** 2 - len(reads)) / 2)))
    return np.fromiter(
        (
            hamming(
                *(
                    read.bits_flattened
                    for read in tuple(random.sample(reads, k=2))
                )
            )
            for _ in range(k)
        ),
        np.float64,
    )


def interdistance(
    reads: list[Read], other_reads: list[Read]
) -> npt.NDArray[np.float64]:
    """
    Produces l*m interdistance values,
    where l, m are the lengths of "reads" and "other_reads"

    Can be used for Uniquess
    """
    return np.fromiter(
        (
            hamming(read_x.bits_flattened, read_y.bits_flattened)
            for read_x in reads
            for read_y in other_reads
        ),
        np.float64,
    )


def interdistance_bootstrap(
    reads: list[Read], other_reads: list[Read], k: int = 1000
) -> npt.NDArray[np.float64]:
    """
    Produces k interdistance values
    Choses pairs of values from "reads" and "other_reads" pseudo randomly.

    Duplicates can occur

    Less computing tome expensive alternative to "interdistance"
    """
    self_choices = [
        choice.bits_flattened for choice in random.choices(reads, k=k)
    ]
    other_choices = [
        choice.bits_flattened for choice in random.choices(other_reads, k=k)
    ]

    return np.fromiter(
        map(hamming, self_choices, other_choices), dtype=np.float64
    )


def bit_stabilization_count_over_time(
    reads: list[Read], stable_after_n_reads: int = 1000
) -> npt.NDArray[np.float64]:
    """
    Goes backwards through Read's.
    (Expectes Read's to be in chronological order)
    Tracks index/time from which a Bits value did not change anymore
    Bits that have been unchanged til the last read
    and for atleast "stable_after_n_reads" Read's are seen as stable
    """

    length_of_read = len(reads[0].bits_flattened)
    reads_count = len(reads)
    did_not_change_since_read = np.full((length_of_read,), 0)
    # Could also theoretically be called "next_bram_value",
    # because we go through the list backwards
    previous_bram_value = reads[-1].bits_flattened

    for inversed_idx, read in enumerate(reversed(reads)):
        bit_changed_list = np.bitwise_xor(
            previous_bram_value, read.bits_flattened
        )
        for bit_idx, bit_changed in enumerate(bit_changed_list):
            if bit_changed == 1 and did_not_change_since_read[bit_idx] == 0:
                did_not_change_since_read[bit_idx] = reads_count - inversed_idx
        previous_bram_value = read.bits_flattened

    stable_bits_per_time_step = np.zeros(reads_count)
    bit_indices, counts = np.unique(
        did_not_change_since_read, return_counts=True
    )

    last_relevant_idx = reads_count - stable_after_n_reads
    for bit_idx, count in zip(bit_indices, counts):
        if bit_idx > last_relevant_idx:
            break
        stable_bits_per_time_step[bit_idx] = count

    return stable_bits_per_time_step


def bit_flip_chance(
    reads: list[Read], only_use_first_element: bool = False
) -> npt.NDArray[np.float64]:
    """
    Determinates over a given list of Reads the probability to flip to 1 for
    each bit.
    This function can also be used to generate a Bit Aliasing Statistic

    Arguments:
        reads: list of Read's of SUV's from bram

    Returns:
        List of floats. Percentage for each bit to flip to 1.
        Values are indexed the same way as the input read values.
    """
    if only_use_first_element:
        reads = reads[:1]
    flip_total_vector = np.zeros(len(reads[0].bits_flattened), dtype=np.uint64)
    for read in reads:
        flip_total_vector = np.add(flip_total_vector, read.bits_flattened)

    return flip_total_vector / len(reads)


def stable_bits_per_idxs(
    reads: list[Read], bit_flip_type: BitFlipType
) -> npt.NDArray[np.float64]:
    wsks_per_bit = bit_flip_chance(reads)
    return np.fromiter(
        (
            1
            if (
                (
                    bit_flip_type == BitFlipType.BOTH
                    and (flip_prob == 0.0 or flip_prob == 1.0)
                )
                or (bit_flip_type == BitFlipType.ONE and flip_prob == 1.0)
                or (bit_flip_type == BitFlipType.ZERO and flip_prob == 0.0)
            )
            else 0
            for flip_prob in wsks_per_bit
        ),
        np.int64,
    )


def reliability(reads: list[Read]) -> np.float64:
    """
    Calculates reliability according to:
        "A Systematic Method to Evaluate and Compare
         the Performance of Physical Unclonable Functions"

    Where r_i/r_i,k,l will be compared to all other read samples.
    We choose reads[0] as r_i, because we assume the first read to be the
    "least influenced by aging"

    Arguments:
        reads: list of Read samples from a BRAM block

    Returns: Reliability score v: 0 <= v <= 1.0, with 1.0 being the best
                possible reliability
    """
    r_i = reads[0].bits_flattened
    intradistance_sum = sum(
        [hamming(r_i, other_read.bits_flattened) for other_read in reads[1:]]
    )
    normalized_avg_intradistance = intradistance_sum / (len(reads) - 1)
    return 1 - normalized_avg_intradistance


def hamming_weight(
    reads: list[Read], only_use_first_element: bool = False
) -> npt.NDArray[np.float64]:
    """
    Computes hamming weight over bits of each read.
    This can be used to compute the Uniformity of BRAMs SUVs

    Arguments:
        reads: list of Read samples

    Returns:
        One hamming weight value per Read
    """
    if only_use_first_element:
        reads = reads[:1]
    return np.fromiter(
        (
            np.sum(read.bits_flattened) / len(read.bits_flattened)
            for read in reads
        ),
        np.float64,
    )
