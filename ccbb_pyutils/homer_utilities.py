import os

from ccbb_pyutils.subprocess_summary import call_subprocess

from ccbb_pyutils.files_and_paths import get_file_name_pieces, transform_path

MAKE_TAG_DIR_CMD = "makeTagDirectory"
PEAKS_FILE_SUFFIX = "_peaks.txt"
ANNOTATED_PEAKS_FILE_SUFFIX = "_peaks_annotated.txt"


def make_tag_dir(fp_for_tag_dirs, input_sam_fp):
    # example call:
    # makeTagDirectory DKP1 DKP1.sam_unique -format sam

    _, sam_base, _ = get_file_name_pieces(input_sam_fp)
    output_dir = os.path.join(fp_for_tag_dirs, sam_base)

    call_args = [MAKE_TAG_DIR_CMD]
    call_args.append(output_dir)
    call_args.append(input_sam_fp)
    call_args.extend(["-format", "sam"])
    call_subprocess(call_args)
    return output_dir


def combine_tag_dirs(fp_for_tag_dirs, list_of_dir_names):
    # NB: list_of_dir_names are the names within the tag directory, like "sample1" or "DKP1",
    # not the dir paths like "~/myproject/tagdirs/sample1/", etc

    # example call:
    # makeTagDirectory All/ -d CTR1/ DKP1/

    combined_dir_paths = [os.path.join(fp_for_tag_dirs, x) for x in list_of_dir_names]
    combined_dir_name = "_".join(list_of_dir_names)
    output_dir = os.path.join(fp_for_tag_dirs, combined_dir_name)

    call_args = [MAKE_TAG_DIR_CMD]
    call_args.append(output_dir)
    call_args.append("-d")
    call_args.extend(combined_dir_paths)
    call_subprocess(call_args)
    return combined_dir_name, output_dir


def find_peaks_for_tag_dir(output_dir, tag_dir_name, tag_dir_path, size, min_dist):
    # example calls:
    # findPeaks DKP1/ -size 200 -minDist 500 > DKP1_200_500.txt

    output_filename = "{0}_size{1}_mindist{2}{3}".format(tag_dir_name, size, min_dist, PEAKS_FILE_SUFFIX)
    output_fp = os.path.join(output_dir, output_filename)

    call_args = ["findPeaks"]
    call_args.append(tag_dir_path)
    call_args.extend(["-size", size])
    call_args.extend(["-minDist", min_dist])
    call_subprocess(call_args, stdout_fp=output_fp)
    return output_fp


def make_bed_for_peaks(output_dir, peaks_for_tag_dir_fp):
    # example calls:
    # pos2bed.pl DKP1_200_500.txt >DKP1_200_500.bed

    output_fp = transform_path(peaks_for_tag_dir_fp, output_dir, ".bed")

    call_args = ["pos2bed.pl"]
    call_args.append(peaks_for_tag_dir_fp)
    call_subprocess(call_args, stdout_fp=output_fp)
    return output_fp


def find_peaks_and_make_bed_for_tag_dir(output_dir, tag_dir_name, tag_dir_path, size, min_dist):
    peaks_for_tag_dir_fp = find_peaks_for_tag_dir(output_dir, tag_dir_name, tag_dir_path, size, min_dist)
    peaks_bed_fp = make_bed_for_peaks(output_dir, peaks_for_tag_dir_fp)
    return peaks_for_tag_dir_fp, peaks_bed_fp


def find_peaks_and_make_beds(parent_dir, output_dir, size, min_dist):
    result = []
    dir_entries = os.scandir(parent_dir)
    for curr_entry in dir_entries:
        if curr_entry.is_dir():
            curr_result = find_peaks_and_make_bed_for_tag_dir(output_dir, curr_entry.name, curr_entry.path, size,
                                                              min_dist)
            result.append(curr_result)

    return result


def run_annotate_peaks(output_dir, installed_genome_id, size, included_tag_dir_paths_list, peak_file_fp):
    # NB: list_of_dir_names are the names within the tag directory, like "sample1" or "DKP1",
    # not the dir paths like "~/myproject/tagdirs/sample1/", etc

    # example call:
    # annotatePeaks.pl All_200_500.txt mm10 -size 300 -raw -d CTR1/ DKP1/ > All_peak_heights.txt

    output_fp = transform_path(peak_file_fp, output_dir, ANNOTATED_PEAKS_FILE_SUFFIX,
                               input_suffix_to_replace=PEAKS_FILE_SUFFIX)

    call_args = ["annotatePeaks.pl"]
    call_args.append(peak_file_fp)
    call_args.append(installed_genome_id)
    call_args.extend(["-size", size])
    call_args.append("-raw")
    call_args.append("-d")
    call_args.extend(included_tag_dir_paths_list)
    call_subprocess(call_args, stdout_fp=output_fp)
    return output_fp


def annotate_peaks(output_dir, fp_for_tag_dirs, installed_genome_id, find_peaks_size, list_of_dir_names, peak_file_fp,
    peak_expansion_factor):

    relevant_tag_dir_paths_list = [os.path.join(fp_for_tag_dirs, x) for x in list_of_dir_names]
    expanded_size = peak_expansion_factor*find_peaks_size
    result = run_annotate_peaks(output_dir, installed_genome_id, expanded_size,
                                relevant_tag_dir_paths_list, peak_file_fp)
    return result