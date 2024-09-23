from typing import Tuple, List, Dict
from pathlib import Path
from scipy.stats import chi2_contingency
import argparse
import numpy as np
import h5py

from hdf5_wrapper import Experiment, ReadSession

def unpack_from_hdf5(path: Path) -> Experiment:
    '''
    Opens hdf5 and converts it to Experiment hdf5 wrapper class
    '''
    with h5py.File(path, "r") as f:
        experiment = Experiment.from_hdf5(f, f.attrs["commit"])

    return experiment    

def chi2_result_list(read_sessions: Dict[str, ReadSession]) -> Tuple[list, list]:
    # Process for data bits
    data_read_chi_square_results = list()
    for byte_idx in range(len(read_sessions[list(read_sessions.keys())[0]].data_reads[0].bits)):
        
        for bit_idx in range(8):
            zero_count_list = list()
            one_count_list = list()

            for read_session in read_sessions.values():
                one_count = sum([
                    read.bits[byte_idx][bit_idx] 
                    for read in read_session.data_reads
                ])
                zero_count = len(read_session.data_reads) - one_count
                
                zero_count_list.append(zero_count)
                one_count_list.append(one_count)
            
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
            zero_count_list = new_zero_count_list
            one_count_list = new_one_count_list
                    
            temporary_contingency_table = np.array([zero_count_list, one_count_list])
            chi2_result = chi2_contingency(temporary_contingency_table)
            data_read_chi_square_results.append(chi2_result)

    # Repeat process for parity bits
    parity_read_chi_square_results = list()
    for byte_idx in range(len(read_sessions[list(read_sessions.keys())[0]].parity_reads[0].bits)):
        for bit_idx in range(8):
            zero_count_list = list()
            one_count_list = list()

            for read_session in read_sessions.values():
                one_count = sum([read.bits[byte_idx][bit_idx] for read in read_session.parity_reads])
                zero_count = len(read_session.parity_reads) - one_count

                zero_count_list.append(zero_count)
                one_count_list.append(one_count)
            
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
            zero_count_list = new_zero_count_list
            one_count_list = new_one_count_list
            
            # len([data.pvalue for data in data_read_chi_square_results if data.pvalue <= 0.1])/len([data.pvalue for data in data_read_chi_square_results])
            temporary_contingency_table = np.array([zero_count_list, one_count_list])
            chi2_result = chi2_contingency(temporary_contingency_table)
            parity_read_chi_square_results.append(chi2_result)

    return data_read_chi_square_results, parity_read_chi_square_results

parser = argparse.ArgumentParser(
    "Script that takes BRAM experiment hdf5 file, unpacks the latter and does a chi squared test over the data\n"
    "The goal is to prove that certain variables do not influence bitflips in the bram"
)
parser.add_argument(
    "--hdf5",
    required=True,
    help="Path to hdf5 file"
)

def main():
    args = parser.parse_args()
    arg_dict = vars(args)

    experiment = unpack_from_hdf5(arg_dict["hdf5"])
    bram_block = list(
        list(
            list(
                experiment.boards.values()
            )[0]
            .pblocks.values()
        )[0]
        .bram_blocks.values()
    )[0]
    # We just assume that the experiment was only performed on a single bram for this script
    data_chi2_results, parity_chi2_results = chi2_result_list(bram_block.read_sessions)
    pass

if __name__ == "__main__":
    main()