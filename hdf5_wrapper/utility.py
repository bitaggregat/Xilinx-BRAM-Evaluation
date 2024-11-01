"""
This module contains smaller functions/structures that didn't fit in otherwhere
"""

import subprocess
import h5py


def add_commit_to_hdf5_group(parent: h5py.Group) -> None:
    """
    Gets hash of latest commit of repository.
    Note: Expects python interpreter to be executed from a repository path
    """
    commit_hash = subprocess.check_output(["git", "rev-parse", "HEAD"])
    parent.attrs["git commit hash"] = commit_hash
