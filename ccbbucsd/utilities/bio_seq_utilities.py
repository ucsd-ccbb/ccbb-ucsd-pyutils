# standard libraries
import logging
import os
import shutil

# ccbb libraries
from ccbbucsd.utilities.files_and_paths import get_filepaths_from_wildcard, get_wild_path, group_files, make_file_path

__author__ = "Amanda Birmingham"
__maintainer__ = "Amanda Birmingham"
__email__ = "abirmingham@ucsd.edu"
__status__ = "prototype"


def rev_comp_canonical_dna_seq(dna_seq):
    complement_dict = {"A": "T",
                       "C": "G",
                       "G": "C",
                       "T": "A",
                       "a": "t",
                       "c": "g",
                       "g": "c",
                       "t": "a"}
    reversed_seq = dna_seq[::-1]
    rev_complement_chars = [complement_dict[x] if x in complement_dict else x for x in reversed_seq]
    return "".join(rev_complement_chars)


def expand_possible_mismatches(perfect_seq, position_alphabet, include_perfect=False):
    result = []
    if include_perfect:
        result.append(perfect_seq)

    perfect_seq_chars = perfect_seq.split()
    for curr_position in range(0, len(perfect_seq_chars)):
        perfect_seq_char = perfect_seq_chars[curr_position]
        for possible_char in position_alphabet:
            if possible_char != perfect_seq_char:
                mismatch_seq_chars = list(perfect_seq_chars)
                mismatch_seq_chars[curr_position] = possible_char
                result.append("".join(mismatch_seq_chars))

    return result


def pair_hiseq_read_files(fastq_filepaths):
    paired_fastqs_by_base = group_files(fastq_filepaths, "_R\d_", "_")

    num_expected = 2
    failure_msgs = []
    for curr_key in paired_fastqs_by_base:
        num_paths = len(paired_fastqs_by_base[curr_key])

        if num_paths != num_expected:
            failure_msgs.append(
                "{0} has {1} read files instead of {2}".format(curr_key, num_paths, num_expected))

    if len(failure_msgs) == 0:
        failure_msgs = None
    else:
        failure_msgs = "\n".join(failure_msgs)

    return paired_fastqs_by_base, failure_msgs


def trim_seq(input_seq, retain_len, retain_5p_end):
    if len(input_seq) < retain_len:
        raise ValueError(
            "input sequence {0} has length {1}, shorter than retain length {2}".format(input_seq, len(input_seq),
                                                                                       retain_len))

    if retain_5p_end:
        return input_seq[:retain_len]
    else:
        return input_seq[-retain_len:]


def merge_igm_files_by_lane_read_set(input_files_dir, output_files_dir, file_suffix):
    read_direction_identifiers = ["_R1_", "_R2_"]
    for curr_direction_id in read_direction_identifiers:
        wildpath = "{0}*{1}".format(curr_direction_id, file_suffix)
        relevant_filepaths = get_filepaths_from_wildcard(input_files_dir, wildpath)

        direction_regex = "_L\d\d\d{0}\d\d\d".format(curr_direction_id)
        merge_files_grouped_by_regex(relevant_filepaths, direction_regex, output_files_dir, file_suffix)


def merge_files_grouped_by_regex(relevant_filepaths, relevant_regex, output_files_dir, file_suffix):
    fps_by_base = group_files(relevant_filepaths, relevant_regex, replacement="")
    for curr_base in fps_by_base:
        output_fp = make_file_path(output_files_dir, curr_base, file_suffix)
        if os.path.isfile(output_fp):
            raise ValueError("Output file '{0}' already exists.".format(output_fp))

        with open(output_fp, 'wb') as output_f:
            for input_fp in fps_by_base[curr_base]:
                with open(input_fp, 'rb') as input_f:
                    logging.info("Adding {0} to {1}".format(input_fp, output_fp))
                    shutil.copyfileobj(input_f, output_f)
