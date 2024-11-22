from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.figure as pltf
import numpy.typing as npt
import numpy as np
from .experiment_hdf5 import Read
from .stats_base import MetaStatistic


def clear_plt(fig: pltf.Figure) -> None:
    """
    Tries to close a given figure and clears everything
    This is necessary because we create multiple plots successively
    """
    plt.close(fig=fig)
    plt.clf()
    plt.cla()


def stable_bit_per_read_step_plot(
    bit_stats: npt.NDArray[np.float64],
    bit_type: str,
    path: Path,
    stable_after_n_reads: int = 1000,
) -> None:
    """
    Creates a step plot of stable bits over time/reads
    """

    # Create a plot data and parity bits:
    # TODO bit type list
    bits_over_time = np.cumsum(bit_stats)

    fig, ax = plt.subplots()
    x = np.arange(1, len(bit_stats) + 1 - stable_after_n_reads)
    y = bits_over_time[:-stable_after_n_reads]

    ax.step(x, y, where="post", label="post")
    # ax.plot(x, y, "o--", color="grey", alpha=0.3)
    ax.set(
        xlabel="Bram readout procedure",
        ylabel="# of stable bits",
        title=f"Increase of # of {bit_type} stable bits "
        "over multiple bram readout procedures",
    )
    fig.savefig(
        Path(path, f"{bit_type}_stable_bits_over_reads.svg"), format="svg"
    )
    clear_plt(fig=fig)


def per_bit_idx_histogram(
    bit_stats: npt.NDArray[np.float64],
    xlabel: str,
    ylabel: str,
    title: str,
    path: Path,
) -> None:
    """
    Creates a histogram with one bar per bit index.
    Expects an numpy array where each value represents one bit index of a bram.
    We don't use plt.hist here because we already have our bins and plt.hist
    would try to recalculate bins

    Arguments:
        bit_stats: Numpy array of stat values where numpy array index==bit idx
        xlabel: Label of abscissa
        ylabel: Label of ordinate
        title: Title of plot
        path: Path of figure
    """
    x_values = [i for i in range(len(bit_stats))]

    plt.xlim(0, len(bit_stats))
    fig, ax = plt.subplots()

    ax.bar(x_values, bit_stats, color="g")
    ax.set(xlabel=xlabel, ylabel=ylabel, title=title)
    fig.savefig(path.with_suffix(".svg"), format="svg")
    clear_plt(fig=fig)


def box_plot(
    bit_stats: npt.NDArray[np.float64], path: Path, ylabel: str, title: str
) -> None:
    fig, ax = plt.subplots()

    ax.boxplot(bit_stats)
    ax.set(ylabel=ylabel, title=title)
    fig.savefig(Path(path, f"{title}.svg"), format="svg")
    clear_plt(fig=fig)


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
    clear_plt(fig=fig)


def histogram(
    bit_stats: npt.NDArray[np.float64],
    xlabel: str,
    ylabel: str,
    title: str,
    path: Path,
    bins: int | str
) -> None:
    fig, ax = plt.subplots()

    ax.hist(bit_stats, bins=bins, edgecolor="black", linewidth=1.2)
    ax.set(xlabel=xlabel, ylabel=ylabel, title=title)
    fig.savefig(path.with_suffix(".svg"), format="svg")
    clear_plt(fig=fig)
