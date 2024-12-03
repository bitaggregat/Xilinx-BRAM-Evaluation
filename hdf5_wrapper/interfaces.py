from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
import h5py
from .utility import PlotSettings


class HDF5Convertible(ABC):
    """
    Alot of the HDF5 conversion/write code is repetitive
    This class provides functions for typical cases of conversion to hdf5,
        in order to reduce code duplicates
    Note: This class may be replaceable by functions (TODO debate)

    Attributes:
        _hdf5_group_name: Name that shall be used for hdf5 subpath
    """

    _hdf5_group_name: str = None

    @abstractmethod
    def add_to_hdf5_group(self, parent: h5py.Group) -> None:
        pass

    @property
    def hdf5_group_name(self) -> str:
        """
        Getter for _hdf5_group_name
        - checks whether or not attribute has been
          correctly checked by subclass
        """
        if self._hdf5_group_name is None:
            raise Exception("Missing hdf5 group name")
        else:
            return self._hdf5_group_name


@dataclass
class Plottable(ABC):
    """
    Abstract class for objects that can create plots from their data
    - e.g. a EntropyStatistic obj should create a box plot
    - e.g. a MetaStats obj should create a latex table in their plot method

    Attributes:
        plot_settings: Object that contains settings (e.g. path) for plotting
    """

    plot_settings: PlotSettings

    def plot(self) -> None:
        """
        This method is not supposed to be overwritten
        Only _plot shall be overwritten by inherited classes
        """
        if self.plot_settings.active:
            if isinstance(self.plot_settings.path, Path):
                self._plot()
            else:
                raise Exception(
                    "No viable plot was given.\n"
                    "Make sure to pass a path as argument if "
                    " plots are activated."
                )

    @abstractmethod
    def _plot(self) -> None:
        raise NotImplementedError
