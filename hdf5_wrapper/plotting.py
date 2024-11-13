from pathlib import Path
import matplotlib.pyplot as plt
import numpy.typing as npt
import numpy as np
from hdf5_wrapper.experiment_hdf5 import Read
from hdf5_wrapper.stats_base import MetaStatistic


def stable_bit_per_read_step_plot(
    bit_stats: npt.NDArray[np.float64], bit_type: str, path: Path
) -> None:
    """
    Creates a step plot of stable bits over time/reads
    """

    # Create a plot data and parity bits:
    # TODO bit type list
    bits_over_time = np.cumsum(bit_stats)

    fig, ax = plt.subplots()
    x = np.arange(1, len(bit_stats) + 1)
    y = bits_over_time

    ax.step(x, y, where="post", label="post")
    ax.plot(x, y, "o--", color="grey", alpha=0.3)
    ax.set(
        xlabel="Bram readout procedure",
        ylabel="# of stable bits",
        title=f"Increase of # of {bit_type} stable bits "
        "over multiple bram readout procedures",
    )
    fig.savefig(
        Path(path, f"{bit_type}_stable_bits_over_reads.svg"), format="svg"
    )


def flip_chance_to_1_per_bit_idx_plot(
    bit_stats: npt.NDArray[np.float64], bit_type: str, path: Path
) -> None:
    """ """
    fig, ax = plt.subplots()

    ax.hist(bit_stats, bins=len(bit_stats), edgecolor="black", linewidth=1.2)
    ax.set(
        xlabel="Bit indices",
        ylabel="Relative frequency of bit flipping to 1",
        title="Relative frequency of bit flip "
        f"per bit idx in {bit_type} bits",
    )
    fig.savefig(
        Path(path, f"{bit_type}_stable_bits_over_reads.svg"), format="svg"
    )


def box_plot(
    bit_stats: npt.NDArray[np.float64], path: Path, ylabel: str, title: str
) -> None:
    fig, ax = plt.subplots()

    ax.boxplot(bit_stats)
    ax.set(ylabel=ylabel, title=title)
    fig.savefig(Path(path, f"{title}.svg"), format="svg")


def multi_boxplot(
    bit_stats_per_xlabel: dict[str, npt.NDArray[np.float64]],
    path: Path,
    ylabel: str,
    title: str,
) -> None:
    fig, ax = plt.subplots()
    xlabels = [xlabel for xlabel in bit_stats_per_xlabel]
    data = [bit_stats_per_xlabel[xlabel] for xlabel in xlabels]
    ax.boxplot(data)
    ax.set(ylabel=ylabel, title=title)
    ax.set_xticklabels(xlabels, rotation=45, fontsize=8)
    fig.savefig(Path(path, f"{title}.svg"), format="svg")


def distribution_histogram(
    bit_stats: npt.NDArray[np.float64],
    path: Path,
    xlabel: str,
    ylabel: str,
    title: str,
) -> None:
    fig, ax = plt.subplots()

    ax.hist(bit_stats, bins="sturges", edgecolor="black", linewidth=1.2)
    ax.set(xlabel=xlabel, ylabel=ylabel, title=title)
    fig.savefig(Path(path, f"{title}.svg"), format="svg")

