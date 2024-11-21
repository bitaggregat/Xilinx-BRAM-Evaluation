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
    path: Path
    active: bool


    def with_expanded_path(self, path_expansion: str) -> Self:
        new_path = Path(self.path, path_expansion)
        new_path.mkdir(parents=True, exist_ok=True)
        return PlotSettings(new_path, self.active)