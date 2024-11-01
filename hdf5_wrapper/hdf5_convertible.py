from abc import ABC, abstractmethod
import h5py


class HDF5Convertible(ABC):
    """
    Alot of the HDF5 conversion/write code is repetitive
    This class provides functions for typical cases of conversion to hdf5,
        in order to reduce code duplicates
    Note: This class may be replaceable by functions (TODO debate)
    """

    _hdf5_group_name: str = None

    @abstractmethod
    def add_to_hdf5_group(self, parent: h5py.Group) -> None:
        pass

    @property
    def hdf5_group_name(self) -> str:
        """
        Getter for _hdf5_group_name
        - checks whether or not attribute has been correctly checked by subclass
        """
        if self._hdf5_group_name is None:
            raise Exception("Missing hdf5 group name")
        else:
            return self._hdf5_group_name
