"""
This module contains smaller functions/structures that didn't fit in otherwhere
"""

import subprocess
import h5py
from dataclasses import dataclass
from pathlib import Path
from typing import Self


def add_commit_to_hdf5_group(parent: h5py.Group) -> None:
    """
    Gets hash of latest commit of repository.
    Note: Expects python interpreter to be executed from a repository path
    """
    commit_hash = subprocess.check_output(["git", "rev-parse", "HEAD"])
    parent.attrs["git commit hash"] = commit_hash


@dataclass(frozen=True)
class PlotSettings:
    """
    Class that saves general settings for plots 
    (currently only the path is saved)

    Attributes:
        path: Path where diagrams shall be saved
        active: True if plots shall be generated, else False
    """
    path: Path
    active: bool

    def with_expanded_path(self, path_expansion: str) -> Self:
        """
        Creates new PlotSettings object with expanded path
        
        Arguments:
            path_expansion: Directory or file name that is appended to path of 
                            new object.
        """
        new_path = Path(self.path, path_expansion)
        new_path.mkdir(parents=True, exist_ok=True)
        return PlotSettings(new_path, self.active)
