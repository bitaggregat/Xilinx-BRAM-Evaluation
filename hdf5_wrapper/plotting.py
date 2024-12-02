"""
Module contains functions that create diagrams and other visuals that are 
resused by different Statistic classes.
Most of them are wrappers around matplotlib functions/objects.
Usages of diagrams, that are specific to a single Statistic type (in other
words code that is not generic in any way), will not be included in this module
"""

from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.figure as pltf
import numpy.typing as npt
import numpy as np


def clear_plt(fig: pltf.Figure) -> None:
    """
    Tries to close a given figure and clears everything
    This is necessary because we create multiple plots successively and
    appearently figures are not closed when leaving the scope

    Arguments:
        fig: pltf.Figure that will be closed
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
    Creates a step plot of stable bits over time/reads.

    Arguments:
        bit_stats: np.array where each index represents a bit idx in the bram
                    and the value at each index describes when a given bit
                    stabilized.
        bit_type: Either "Parity or Data". Will be inserted into diagram
                    description.
        path: Path where diagram will be saved (file extension not included)
        stable_after_n_reads: Number of reads that a bit has to not change
                                in order to be classified as "stable"
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
    We don't use plt.hist here because we already have our bins precalculated.
    plt.hist would try to recalculate the bins, which would be a waste of time

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
    """
    Wrapper around plt.boxplot.

    Arguments:
        bit_stats: np.array of floats that will be used for boxplot
        path: Path where diagram will be saved (file extension not included)
        ylabel: Label of y-axis of diagram
        title: Title of diagram
    """
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
    """
    Creates box plot with multiple boxes. Boxes are created from a dict of
    numpy arrays, indexed by a str indentifier (name).

    Arguments:
        bit_stats_per_xlabel: dict[Description/Name of np.array: np.array of float]
        path: Path where diagram will be saved (filextension not included)
        ylabel: Label of y-axis of diagram
        title: Title of diagram
    """
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
    """
    Wrapper around plt.hist.

    Arguments:
        bit_stats: Numpy array of float that will be sorted into bins
        xlabel: Label of the x-axis in the diagram
        ylabel: Label of the y-axis in the diagram
        title: Title of the diagram
        path: Path where diagram will be saved (file type not included)
        bins: Number of bins (int) or predefined bin estimation method as str
    """
    fig, ax = plt.subplots()

    ax.hist(bit_stats, bins=bins, edgecolor="black", linewidth=1.2)
    ax.set(xlabel=xlabel, ylabel=ylabel, title=title)
    fig.savefig(path.with_suffix(".svg"), format="svg")
    clear_plt(fig=fig)
