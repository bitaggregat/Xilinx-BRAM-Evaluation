from typing import Tuple, Dict, List
from pathlib import Path
from enum import Enum
from dataclasses import dataclass
from scipy.stats import chi2_contingency
from scipy.stats.contingency import odds_ratio
import argparse
import numpy as np
import h5py


from hdf5_wrapper import Experiment, ReadSession, Read

@dataclass
class ContingencyTable:
    variables: List[str]
    zero_count_list: List[int]
    one_count_list: List[int]

    def to_list(self) -> List[List[int]]:
        return [self.zero_count_list, self.one_count_list]
    
    def percentage_flipped_dict(self) -> Dict[str, float]:
        variable_to_percentage_dict = dict()
        for zero_count, one_count, variable in zip(self.zero_count_list, self.one_count_list, self.variables):
            variable_to_percentage_dict[variable] = one_count/(zero_count + one_count)
        return variable_to_percentage_dict
    
    def contingency_odds(self) -> float:
        if len(self.variables) > 2:
            raise Exception("Can't calculate contingency odds on more than 2 values")
        return odds_ratio(self.to_list()).statistic


def unpack_from_hdf5(path: Path) -> Experiment:
    '''
    Opens hdf5 and converts it to Experiment hdf5 wrapper class
    '''
    with h5py.File(path, "r") as f:
        experiment = Experiment.from_hdf5(f, f.attrs["commit"])

    return experiment

def normalize_frequency_lists(zero_count_list: List[int], one_count_list: List[int]) -> Tuple[List[int], List[int]]:
    # TODO Review this solution to observed 0 frequency
    new_zero_count_list = []
    new_one_count_list = []
    for idx in range(len(zero_count_list)):
        if zero_count_list[idx] == 0:
            new_zero_count_list.append(1)
            new_one_count_list.append(one_count_list[idx]-1)
        elif one_count_list[idx] == 0:
            new_zero_count_list.append(zero_count_list[idx]-1)
            new_one_count_list.append(1)
        else:
            new_zero_count_list.append(zero_count_list[idx])
            new_one_count_list.append(one_count_list[idx])

    return new_zero_count_list, new_one_count_list


def contingency_table_list(read_sessions: Dict[str, ReadSession], bit_type: str, normalize: bool) -> List[ContingencyTable]:
    """
    bit_type: either "parity_reads" or "data_reads"
    """

    contingency_table_list = list()
    for byte_idx in range(len(
        getattr(read_sessions[list(read_sessions.keys())[0]], bit_type)[0].bits
        )):
        
        for bit_idx in range(8):
            variables = list()
            zero_count_list = list()
            one_count_list = list()

            for variable_name, read_session in read_sessions.items():
                variables.append(variable_name)
                one_count = sum([
                    read.bits[byte_idx][bit_idx] 
                    for read in getattr(read_session, bit_type)
                ])
                zero_count = len(getattr(read_session, bit_type)) - one_count
                
                zero_count_list.append(zero_count)
                one_count_list.append(one_count)
            
            # TODO Review this solution to observed 0 frequency
            if normalize:
                zero_count_list, one_count_list = normalize_frequency_lists(zero_count_list, one_count_list)
                    
            contingency_table_list.append(ContingencyTable(
                variables=variables,
                zero_count_list=zero_count_list,
                one_count_list=one_count_list
            ))
    return contingency_table_list

def chi2_result_list(contingency_tables: List[ContingencyTable]) -> list:
    chi2_results = list()
    for contingency_table in contingency_tables:
        chi2_result = chi2_contingency(np.array(contingency_table.to_list()))
        chi2_results.append(chi2_result)
    return chi2_results

def chi2_pvalue_percentage_pass(alpha: float, chi2_results: list) -> float:
    return len(
        [
            data.pvalue for data in chi2_results
            if data.pvalue <= alpha
        ])/len([
            data.pvalue for data in chi2_results
            ]
            )

def add_percentages_to_bit_group(parent: h5py._hl.group.Group, contingency_tables: List[ContingencyTable]) -> None:
    
    percentages_per_variable = {
        variable_name: list()
        for variable_name in contingency_tables[0].variables
    }

    for contingency_table in contingency_tables:
        percentage_flipped_dict = contingency_table.percentage_flipped_dict()
        for variable_name, value in percentage_flipped_dict.items():
            percentages_per_variable[variable_name].append(value)
    
    for variable_name, percentage_list in percentages_per_variable.items():
        parent.create_dataset(
            f"{variable_name}_percentage_of_bits_flipped_to_1",
            (len(percentage_list),),
            dtype="f",
            data=percentage_list
        )

        unstable_bits_flip_percent = [percent for percent in percentage_list if percent != 1 and percent != 0]
        # Meta Data
        parent.attrs[f"{variable_name}_stable_bits_percentage"] = 1 - len(unstable_bits_flip_percent)/len(percentage_list)
        parent.attrs[f"{variable_name}_unstable_bits_flip_chance_mean"] = sum(unstable_bits_flip_percent)/len(unstable_bits_flip_percent)
        parent.attrs[f"{variable_name}_unstable_bits_flip_chance_variance"] = np.var(unstable_bits_flip_percent)
    


def add_bit_type_group(parent: h5py._hl.group.Group, read_sessions: Dict[str, ReadSession], bit_type: str) -> None:
    contingency_tables = contingency_table_list(read_sessions, bit_type, normalize=False)
    normalized_contingency_tables = contingency_table_list(read_sessions, bit_type, normalize=True)

    bit_chi2_results = chi2_result_list(normalized_contingency_tables)

    bit_group = parent.create_group(bit_type)
    add_percentages_to_bit_group(bit_group, contingency_tables)
    bit_group.create_dataset(
        "pvalues",
        (len(bit_chi2_results),),
        dtype="f",
        data=[result.pvalue for result in bit_chi2_results]
    )

    bit_group.attrs["percentage_of_pvalues_passing_alpha_0.05"] = chi2_pvalue_percentage_pass(0.05, bit_chi2_results)
    bit_group.attrs["percentage_of_pvalues_passing_alpha_0.1"] = chi2_pvalue_percentage_pass(0.1, bit_chi2_results)

def chi2_result_to_hdf5(outpath: Path, read_sessions: Dict[str, ReadSession]) -> None:

    with h5py.File(outpath, "w") as f:
        add_bit_type_group(f, read_sessions, "parity_reads")
        add_bit_type_group(f, read_sessions, "data_reads")

parser = argparse.ArgumentParser(
    "Script that takes BRAM experiment hdf5 file, unpacks the latter and does a chi squared test over the data\n"
    "The goal is to prove that certain variables do not influence bitflips in the bram"
)
parser.add_argument(
    "--read_hdf5",
    required=True,
    help="Path to hdf5 file containing bram reads"
)
parser.add_argument(
    "--out_hdf5",
    required=True,
    help="Path where result hdf5 shall be written"
)

def main():
    args = parser.parse_args()
    arg_dict = vars(args)

    experiment = unpack_from_hdf5(arg_dict["read_hdf5"])
    bram_block = list(
        list(
            list(
                experiment.boards.values()
            )[0]
            .pblocks.values()
        )[0]
        .bram_blocks.values()
    )[0] # We just assume that the experiment was only performed on a single bram for this script
    chi2_result_to_hdf5(arg_dict["out_hdf5"], bram_block.read_sessions)

if __name__ == "__main__":
    main()