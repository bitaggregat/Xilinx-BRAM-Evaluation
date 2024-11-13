import random
import numpy as np
import numpy.typing as npt
from scipy.spatial.distance import hamming
from .experiment_hdf5 import Read


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
    k = int(min(k, (len(reads) ** 2 - len(reads) / 2)))

    return np.fromiter(
        (
            hamming(
                *[
                    read.bits_flattened
                    for read in tuple(random.choices(reads, k=2))
                ]
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

    return np.fromiter(map(hamming, self_choices, other_choices))


def bit_stabilization_count_over_time(
    reads: list[Read], stable_after_n_reads: int = 100
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
        did_not_change_since_read, 
        return_counts=True
    )

    last_relevant_idx = reads_count - stable_after_n_reads
    for bit_idx, count in zip(bit_indices, counts):
        if bit_idx > last_relevant_idx:
            break
        stable_bits_per_time_step[bit_idx] = count

    return stable_bits_per_time_step
