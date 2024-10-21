import h5py
from .stats import StatisticMethod

class MultiReadSessionOwner:
    # TODO minimal test
    """
    Class that manages reads of multiple read sessions
    """
    _read_session_names: list[str] = None

    @property
    def read_session_names(self) -> list[str]:
        """
        All read_session owners need to know the names of their read sessions
        These names are used as identifiers/dict keys
        """
        if self._read_session_names is None:
            raise Exception("_read_session_names are not set.")
        else:
            return self._read_session_names
        
class HDF5Convertible(MultiReadSessionOwner):
    """
    Alot of the HDF5 conversion/write code is repetitive
    This class provides functions for typical cases of conversion to hdf5,
        in order to reduce code duplicates
    Note: This class may be replaceable by functions (TODO debate)
    """
    # Names of attributes that use ReadSessionListStat
    list_stats: list[str]
    substats: list

    def add_list_stats_to_hdf5_group(self, parent: h5py.Group) -> None:
        # TODO Test
        if self.list_stats is None:
            raise Exception("Attribute 'list_stats' has to be initialized before using this function")
        else:
            for list_stat_name in self.list_stats:
                stat_group = parent.create_group(list_stat_name)
                list_stat = getattr(self, list_stat_name)
                meta_stat_lines = list()
                meta_stat_read_session_header = []
                for read_session_name in self.read_session_names:
                    if not list_stat[read_session_name] or list_stat[read_session_name] is None:
                        continue
                    else:
                        read_session_group = stat_group.create_group(read_session_name)
                        read_session_group.create_dataset("data_bits", (len(list_stat[read_session_name].data_read_stat),), "f8", list_stat[read_session_name].data_read_stat)
                        read_session_group.create_dataset("parity_bits", (len(list_stat[read_session_name].parity_read_stat),), "f8", list_stat[read_session_name].parity_read_stat)
                        meta_stat_read_session_header.append(read_session_name)
                        meta_stat_lines.append([
                            list_stat[read_session_name].meta_stats[stat_method_name]
                            for stat_method_name in list_stat[read_session_name].meta_stats
                            ])
                if meta_stat_lines:
                    meta_stat_dataset = stat_group.create_dataset("meta_stats", (len(list_stat),len(StatisticMethod.statistic_methods) * 2), "f8", meta_stat_lines)
                    meta_stat_dataset.attrs["read_sessions"] = meta_stat_read_session_header
                    meta_stat_dataset.attrs["statistic_methods"] = [method_name for method_name in list_stat[self.read_session_names[0]].meta_stats]
                else: 
                    continue
    
    def add_stat_to_hdf5_group(self, parent: h5py.Group, name: str, stat) -> None:
        header = [read_session_name for read_session_name in self.read_session_names]
        dataset = parent.create_dataset(name, (len(stat),), "f8", [stat[read_session_name] for read_session_name in self.read_session_names])
        dataset.attrs["read_session"] = header

class StatAggregator(MultiReadSessionOwner):
    # TODO Test
    '''
    Class that provides aggregate_substats function
    '''
    substats: list = None
    # List of names of attributes that are aggregatable
    aggregatable_stats: list[str] = None

    def aggregate_substats(self) -> None:
        '''
        Class is expected to have a list of substat objects
            e.g. PblockStat has list[BramStat]
        This aggregates these substats in order gain knowledge of the stat on a meta lvl
            - e.g. we know the median entropy of each bram block,
              -> now we want to know the median entropy of ALL bram blocks combined
        '''
        if self.aggregatable_stats is None:
            raise Exception("List 'aggregatable_stats' needs to be set to use this function")
        elif self.substats is None:
            raise Exception("List 'substats' needs to be set to use this function")
        else:
            attribute_references = {
                attr_name: getattr(self, attr_name)
                for attr_name in self.aggregatable_stats
            }
                
            for read_session_name in self.read_session_names:
                attribute_temp_aggregation_lists = {
                    attr_name: list()
                    for attr_name in self.aggregatable_stats
                }

                for substat in self.substats:
                    for attr_name in self.aggregatable_stats:
                        attribute_temp_aggregation_lists[attr_name].append(
                            getattr(substat, attr_name)[read_session_name]
                        )
                
                # This uses the "+" operator on ReadSessionListStat objects,
                # which works because the ReadSessionListStat has a custom implementation of "__add__" and "__radd__"
                for attr_name in self.aggregatable_stats:
                    # List is potentially empty:
                    # - e.g. when only 1 BramBlock was measured, no interdistance can be calculated
                    if attribute_temp_aggregation_lists[attr_name][0]:
                        attribute_references[attr_name][read_session_name] = sum(attribute_temp_aggregation_lists[attr_name])
                    else:
                        attribute_references[attr_name][read_session_name] = None
