"""
Module contains functions that create diagrams and other visuals that are
resused by different Statistic classes.
Most of them are wrappers around matplotlib functions/objects.
Usages of diagrams, that are specific to a single Statistic type (in other
words code that is not generic in any way), will not be included in this module
"""

from pathlib import Path
import matplotlib

matplotlib.use("agg")
import matplotlib.colors
import matplotlib.pyplot as plt
import matplotlib.figure as pltf
import numpy.typing as npt
import numpy as np
import matplotlib.path as mpath
import matplotlib.patches as mpatches
import time
import gc
from .utility import (
    HeatmapBitDisplaySetting,
    combine_data_and_parity_bits,
    ColorPresets,
)
from typing import Type


def clear_plt(fig: pltf.Figure) -> None:
    """
    Tries to close a given figure and clears everything
    This is necessary because we create multiple plots successively and
    appearently figures are not closed when leaving the scope

    Arguments:
        fig: pltf.Figure that will be closed
    """
    plt.clf()
    gc.collect()


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

    fig, ax = plt.subplots(num=1, clear=True)
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
    use_log: bool = False,
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
        use_log: Puts all values through log n (useful if values are
                    very unbalancedly distributed)
    """
    if use_log:
        x_values = [np.log(i) if i != 0 else 0 for i in range(len(bit_stats))]
    else:
        x_values = [i for i in range(len(bit_stats))]

    plt.xlim(0, len(bit_stats))
    fig, ax = plt.subplots(num=1, clear=True)

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
    fig, ax = plt.subplots(num=1, clear=True)

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
        bit_stats_per_xlabel: dict[Name of np.array: np.array of float]
        path: Path where diagram will be saved (filextension not included)
        ylabel: Label of y-axis of diagram
        title: Title of diagram
    """
    fig, ax = plt.subplots(num=1, clear=True)
    xlabels = [xlabel for xlabel in bit_stats_per_xlabel]
    data = [bit_stats_per_xlabel[xlabel] for xlabel in xlabels]
    ax.boxplot(data)
    ax.set(ylabel=ylabel, )#title=title)
    ax.set_xticklabels(xlabels, fontsize=8)
    fig.savefig(Path(path, f"{title}.png"), format="png",
                dpi=900)
    clear_plt(fig=fig)


def histogram(
    bit_stats: npt.NDArray[np.float64],
    xlabel: str,
    ylabel: str,
    title: str,
    path: Path,
    bins: int | str,
    log: bool = False,
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
        log: Sets whether or not values should be scaled by log n
    """
    fig, ax = plt.subplots(num=1, clear=True)

    ax.hist(
        bit_stats,
        bins=range(bins + 1),
        edgecolor="black",
        linewidth=1.2,
        log=log,
    )
    ax.set(xlabel=xlabel, ylabel=ylabel, title=title)
    fig.tight_layout()
    fig.savefig(path.with_suffix(".svg"), format="svg")
    clear_plt(fig=fig)


def add_label_band(ax, top, bottom, label, *, spine_pos=-0.05, tip_pos=-0.02):
    """
    ##################################################
    SOURCED FROM: https://stackoverflow.com/a/67237650
    ##################################################
    Helper function to add bracket around y-tick labels.

    Arguments
    ----------
    ax : matplotlib.Axes
        The axes to add the bracket to

    top, bottom : floats
        The positions in *data* space to bracket on the y-axis

    label : str
        The label to add to the bracket

    spine_pos, tip_pos : float, optional
        The position in *axes fraction* of the spine and tips of the bracket.
        These will typically be negative

    Returns
    -------
    bracket : matplotlib.patches.PathPatch
        The "bracket" Aritst.  Modify this Artist to change the color etc of
        the bracket from the defaults.

    txt : matplotlib.text.Text
        The label Artist.  Modify this to change the color etc of the label
        from the defaults.

    """
    # grab the yaxis blended transform
    transform = ax.get_yaxis_transform()

    # add the bracket
    bracket = mpatches.PathPatch(
        mpath.Path(
            [
                [tip_pos, top],
                [spine_pos, top],
                [spine_pos, bottom],
                [tip_pos, bottom],
            ]
        ),
        transform=transform,
        clip_on=False,
        facecolor="none",
        edgecolor="k",
        linewidth=2,
    )
    ax.add_artist(bracket)

    # add the label
    txt = ax.text(
        spine_pos,
        (top + bottom) / 2,
        label,
        ha="right",
        va="center",
        rotation="vertical",
        clip_on=False,
        transform=transform,
    )

    return bracket, txt


def heatmap_per_bit(
    bit_stats: npt.NDArray[np.float64],
    metric: str,
    bits_per_column: int,
    cmap: str,
    norm: matplotlib.colors.Normalize = None,
) -> tuple[plt.figure, plt.axes]:
    """
    Creates (incomplete) heatmap figure of bits for some BitwiseStatistic.
    Incomplete because colorbar and saving has to be handled by other function

    Arguments:
        bit_stats: Stats with one value per bit idx
        metric: Name of Statistic metric (will be inserted in diagram)
        bits_per_column: Height of heatmap/assumption of dimension of bram grid
        cmap: Name of matplot color map that shall be used

    Returns:
        Figure and axes of (incomplete) heatmap
    """

    two_d_array = np.split(bit_stats, bits_per_column)
    fig, ax = plt.subplots(num=1, clear=True)
    im = ax.imshow(two_d_array, cmap=cmap, norm=norm)
    ax.tick_params(
        axis="both",
        which="both",
        bottom=True,
        top=False,
        left=True,
        labelbottom=True,
        labelleft=True,
        labelsize=6,
        width=0.4,
        length=2,
    )
    # ax.spines[:].set_visible(False)
    ax.set_xticks(
        ticks=np.arange(0, 512, 32), labels=[str(i) for i in range(0, 512, 32)]
    )
    ax.set_yticks(
        ticks=np.arange(0, 64, 32), labels=[str(i) for i in range(0, 64, 32)]
    )

    [x.set_linewidth(0.175) for x in ax.spines.values()]
    cbar = ax.figure.colorbar(im, ax=ax)
    cbar.ax.set_ylabel(metric, rotation=-90, va="bottom")
    plt.tight_layout()
    return fig, ax


def heatmap_per_bit_inplace(
    ax,
    bit_stats: npt.NDArray[np.float64],
    metric: str,
    bits_per_column: int,
    cmap: str,
    norm: matplotlib.colors.Normalize = None,
    title: str = "",
) -> tuple[plt.figure, plt.axes]:
    """
    Creates (incomplete) heatmap figure of bits for some BitwiseStatistic.
    Incomplete because colorbar and saving has to be handled by other function

    Arguments:
        bit_stats: Stats with one value per bit idx
        metric: Name of Statistic metric (will be inserted in diagram)
        bits_per_column: Height of heatmap/assumption of dimension of bram grid
        cmap: Name of matplot color map that shall be used

    Returns:
        Figure and axes of (incomplete) heatmap
    """

    two_d_array = np.split(bit_stats, bits_per_column)
    im = ax.imshow(two_d_array, cmap=cmap, norm=norm)
    ax.tick_params(
        axis="both",
        which="both",
        bottom=True,
        top=False,
        left=True,
        labelbottom=True,
        labelleft=True,
        labelsize=6,
        width=0.4,
        length=2,
    )
    ax.invert_yaxis()
    print(title)
    ax.set_title(title, fontsize=8)
    # ax.spines[:].set_visible(False)
    ax.set_xticks(
        ticks=np.arange(0, 512, 32), labels=[str(i) for i in range(0, 512, 32)]
    )
    ax.set_yticks(
        ticks=np.arange(0, 64, 32), labels=[str(i) for i in range(0, 64, 32)]
    )

    [x.set_linewidth(0.175) for x in ax.spines.values()]


def bit_heatmaps(
    data_bit_stats: npt.NDArray[np.float64],
    parity_bit_stats: npt.NDArray[np.float64],
    bit_display_setting: HeatmapBitDisplaySetting,
    metric: str,
    path: Path,
    cmap: str = ColorPresets.default,
) -> None:
    """
    Wrapper around heatmap_per_bit.
    Handles saving of figure, arrangement of bits of different type and
    colorbar

    Arguments:
        data_bit_stats: Stats of data bits ordered by bit idx
        parity_bit_stats: Stats of parity bits ordered by bit idx
        bit_display_setting: See HeatmapBitDisplaySetting Enum
        metric: Name of Statistic metric (will be inserted in diagram)
        path: Path where diagram(s) shall be saved
        cmap: Name of matplot color map that shall be used
    """

    if (
        bit_display_setting == HeatmapBitDisplaySetting.BOTH
        or bit_display_setting == HeatmapBitDisplaySetting.MERGE
    ):
        fig, ax = heatmap_per_bit(
            combine_data_and_parity_bits(data_bit_stats, parity_bit_stats),
            metric=metric,
            bits_per_column=64,
            cmap=cmap,
        )
        # add_label_band(ax=ax, top=0, bottom=32, label="data bits")
        # add_label_band(ax=ax, top=33, bottom=36, label="parity bits")
        fig.savefig(
            Path(path, "heat_map_parity_and_data_bits_combined").with_suffix(
                ".png"
            ),
            format="png",
            dpi=900,
        )
        clear_plt(fig)
    if (
        bit_display_setting == HeatmapBitDisplaySetting.BOTH
        or bit_display_setting == HeatmapBitDisplaySetting.SEPARATE
    ):
        for bit_type, bit_stats, column_size in [
            ("data", data_bit_stats, 64),
            ("parity", parity_bit_stats, 64),
        ]:
            fig, ax = heatmap_per_bit(
                bit_stats=bit_stats,
                metric=metric,
                bits_per_column=column_size,
                cmap=cmap,
            )
            fig.savefig(
                Path(path, f"heat_map_{bit_type}").with_suffix(".png"),
                format="png",
                dpi=900,
            )

            clear_plt(fig)


def single_value_to_file(
    value: np.float64, path: Path, description: str
) -> None:
    with open(Path(path, description).with_suffix(".txt"), mode="w") as f:
        f.write(str(value))


def multi_bit_heatmap(
    bit_stats: dict,
    path: Path,
    cmap: str = ColorPresets.default,
    entity_name: str = "",
) -> None:
    base_fig, base_ax = plt.subplots(layout="constrained")
    axs = base_fig.subplots(len(bit_stats), 1)
    vmin = 1
    vmax = 0
    plt.rcParams["figure.constrained_layout.use"] = True
    # Find min and max for norm
    for bit_stat in bit_stats.values():
        vmin = min(min(bit_stat), vmin)
        vmax = max(max(bit_stat), vmax)
    norm = matplotlib.colors.Normalize(vmin, vmax)

    for idx, board in enumerate(bit_stats):
        temp_ax = axs[idx]
        heatmap_per_bit_inplace(
            ax=temp_ax,
            bit_stats=bit_stats[board],
            metric="Count of bit at bit index",
            bits_per_column=64,
            cmap=cmap,
            norm=norm,
            title=board,
        )

    base_ax.spines[:].set_visible(False)
    base_ax.tick_params(
        bottom=False, top=False, left=False, labelbottom=False, labelleft=False
    )
    #base_fig.suptitle(f"Frequency of Bit types on BRAMs of {entity_name}")
    cbar = base_fig.colorbar(matplotlib.cm.ScalarMappable(norm, cmap), ax=axs)
    cbar.ax.set_ylabel(
        f"Bit-aliasing (%)",
        rotation=-90,
        va="bottom",
    )
    base_fig.savefig(
        Path(path, f"heat_map_bit-aliasing_multi_device_datastats").with_suffix(".png"),
        format="png",
        dpi=900,
    )

def multi_bit_heatmap2(
    bit_stats: dict,
    path: Path,
    cmap: str = ColorPresets.default,
    entity_name: str = "",
) -> None:
    base_fig, base_ax = plt.subplots(layout="constrained")
    axs = base_fig.subplots(len(bit_stats), 1)
    vmin = 1
    vmax = 0
    plt.rcParams["figure.constrained_layout.use"] = True
    # Find min and max for norm
    for bit_stat in bit_stats.values():
        vmin = min(min(bit_stat), vmin)
        vmax = max(max(bit_stat), vmax)
    norm = matplotlib.colors.Normalize(vmin, vmax)

    for idx, board in enumerate(bit_stats):
        temp_ax = axs[idx]
        heatmap_per_bit_inplace(
            ax=temp_ax,
            bit_stats=bit_stats[board],
            metric="Count of bit at bit index",
            bits_per_column=64,
            cmap=cmap,
            norm=norm,
            title=board,
        )

    base_ax.spines[:].set_visible(False)
    base_ax.tick_params(
        bottom=False, top=False, left=False, labelbottom=False, labelleft=False
    )
    #base_fig.suptitle(f"Frequency of Bit types on BRAMs of {entity_name}")
    cbar = base_fig.colorbar(matplotlib.cm.ScalarMappable(norm, cmap), ax=axs)
    cbar.ax.set_ylabel(
        f"Bit-aliasing (%)",
        rotation=-90,
        va="bottom",
    )
    base_fig.savefig(
        Path(path, f"heat_map_bit-aliasing_multi_device_datastats").with_suffix(".png"),
        format="png",
        dpi=900,
    )

def single_value_bar_plot(
    values: dict[str, list[np.float64]],
    labels: list[str],
    title: str,
    path: Path,
) -> None:
    # values = {
    #    'initial value 00': (38.79, 48.83, 47.50),
    #    'initial value ff': (18.35, 18.43, 14.98),
    #    'after 9000 intializations': (189.95, 195.82, 217.19),
    # }

    x = np.arange(len(labels))  # the label locations
    width = 1/7  # the width of the bars
    multiplier = 0

    fig, ax = plt.subplots(layout="constrained")

    for attribute, measurement in values.items():
        offset = width * multiplier
        rects = ax.bar(x + offset, measurement, width, label=attribute)
        ax.bar_label(rects, padding=6)
        multiplier += 1

    # Add some text for labels, title and custom x-axis tick labels, etc.
    ax.set_ylabel("Reliability (%)")
    ax.set_title(title)
    ax.set_xticks(x + width * 2.5, labels)
    ax.legend()#loc="upper left", ncols=len(values))
    ax.set_ylim(90, 94)

    fig.savefig(path.with_suffix(".png"),
        format="png",
        dpi=900,
    )
    clear_plt(fig)
