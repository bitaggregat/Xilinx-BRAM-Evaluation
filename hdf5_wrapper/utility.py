"""
This module contains smaller functions/structures that didn't fit in otherwhere
"""

import subprocess
import numpy as np
import numpy.typing as npt
import h5py
from dataclasses import dataclass
from enum import Enum, auto
from pathlib import Path
from typing import Self


class ColorPresets:
    """
    Enum that contains color default settings for specific use cases.

    Attributes:
        default: default default
        one_flipping_bit: default color for bits that flip to 1
        zero_flipping_bit: default color for bits that flip to 0
    """
    default = "Greys"
    one_flipping_bit = "hot"
    zero_flipping_bit = "cool"


def add_commit_to_hdf5_group(parent: h5py.Group) -> None:
    """
    Gets hash of latest commit of repository.
    Note: Expects python interpreter to be executed from a repository path
    """
    commit_hash = subprocess.check_output(["git", "rev-parse", "HEAD"])
    parent.attrs["git commit hash"] = commit_hash


def combine_data_and_parity_bits(
    data_bits: npt.NDArray[np.float64], parity_bits: npt.NDArray[np.float64]
) -> npt.NDArray[np.float64]:
    """
    Combines data and parity bits in a specific order.
    (The order is our assumption of the physical order of the grid in the bram)

    Arguments:
        data_bits: Some stat values indexed by data bit indices
        parity_bits: Some stat values indexed by parity bit indices

    Returns:
        data and parity bits combined according to our assumption of the grid
    """
    if len(data_bits) != 64 * 512 or len(parity_bits) != 64 * 64:
        raise ValueError(
            "Length of either parity or data bits is incorrect "
            f"({len(data_bits)}, {len(parity_bits)})"
        )
    else:
        #parity_bits = np.roll(parity_bits, -8)
        return np.array(
            [
                np.append(
                    data_bits[parity_idx * 32: (parity_idx + 1) * 32],
                    parity_bits[(parity_idx)* 4: (parity_idx+1) * 4]
                )
                for parity_idx in range(0, 1024)
            ],
            np.float64,
        ).flatten()


class HeatmapBitDisplaySetting(Enum):
    """
    Heatmaps are created to give an overview of of values per bit.
    This Enum handles the settting that decides how parity and data bits shall
    be displayed in heat map(s)

    Attributes:
        MERGE: Display data and parity bits in a single heatmap (512 x 72),
                where the first 64 bits of a row are data bits and
                the last 8 bits are parity bits
        SEPARATE: Display parity and data bits in separate heatmap files
                    (512 x 64) and (64 x 64)
        BOTH: Create graphics of MERGE and SEPARATE (will take longer)
    """

    MERGE = auto()
    SEPARATE = auto()
    BOTH = auto()


class BitFlipType(Enum):
    """
    Sets values that can be used for settings of functions or plots.
    Some stat function will care about the direction that a bit flips.
    """
    ONE = auto()
    ZERO = auto()
    BOTH = auto()
    UNSTABLE = auto()
    VERY_UNSTABLE = auto()
    RANDOM = auto()


@dataclass
class PlotSettings:
    """
    Class that saves general settings for plots
    (currently only the path is saved)

    Attributes:
        path: Path where diagrams shall be saved
        active: True if plots shall be generated, else False
        heat_map_bit_display_setting: See HeatMapBitDisplaySetting Enum class
        heatmap_cmap: name of color map that will be used for heatmaps
    """

    path: Path
    active: bool
    heatmap_bit_display_setting: HeatmapBitDisplaySetting
    heatmap_cmap: str = ColorPresets.default
    bram_count: int = None
    title: str = None
    entity_name: str = None

    def with_expanded_path(self, path_expansion: str) -> Self:
        """
        Creates new PlotSettings object with expanded path

        Arguments:
            path_expansion: Directory or file name that is appended to path of
                            new object.
        """
        new_path = Path(self.path, path_expansion)
        new_path.mkdir(parents=True, exist_ok=True)
        return PlotSettings(
            new_path,
            self.active,
            heatmap_bit_display_setting=self.heatmap_bit_display_setting,
            heatmap_cmap=self.heatmap_cmap,
            bram_count=self.bram_count,
            entity_name=self.entity_name,
            title=self.title
        )
