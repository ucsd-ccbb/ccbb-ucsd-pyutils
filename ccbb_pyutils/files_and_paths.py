# standard libraries
import fnmatch
import glob
import logging
import os
import re

__author__ = "Amanda Birmingham"
__maintainer__ = "Amanda Birmingham"
__email__ = "abirmingham@ucsd.edu"
__status__ = "prototype"


def transform_path(input_fp, output_dir, output_ext, input_suffix_to_replace=None):
    if input_suffix_to_replace is not None:
        input_fp = input_fp.replace(input_suffix_to_replace, "")
    _, input_base, _ = get_file_name_pieces(input_fp)
    result = make_file_path(output_dir, input_base, output_ext)
    return result


def get_file_name_pieces(file_path):
    """
    Split input file path into the path, the file name without extension, and the extension, and return as a tuple.

    Example:
        Inputting "/Users/Me/python/src/my_file.py" returns ("/Users/Me/python/src", "my_file", ".py").

    Args:
        file_path (str): A file name, either with or without a path. Examples: my_file.py, ./src/my_file.py,
            /Users/Me/python/src/my_file.py .

    Returns:
        tuple(str, str, str): A tuple containing first the path to the input file, then the file name without
            extension, then the extension.

    """
    file_dir, filename = os.path.split(file_path)
    file_base, file_ext = os.path.splitext(filename)
    return file_dir, file_base, file_ext


def make_file_path(file_dir, file_base, file_suffix):
    """Assemble a file path from a path, a base file name without extension, and a suffix including the extension.

    The file_ext argument may be any string that ends with an extension.

    Examples:
        Inputting "/Users/Me/python/src", "my_file", ".py" returns "/Users/Me/python/src/my_file.py".
        Inputting "/Users/Me/python/src", "my_file", "_modified.py" returns "/Users/Me/python/src/my_file_modified.py".

    Args:
        file_dir (str): A path.
        file_base (str): The base name of the file to be produced.
        file_suffix (str): A suffix to be applied to the file_base to produce the final file name.  Must include an
            extension.

    Returns:
        str: A file path.

    """
    filename = file_base + file_suffix
    return os.path.join(file_dir, filename)


def build_multipart_fp(working_dir, name_pieces, delimiter="_"):
    filename = delimiter.join(name_pieces)
    output_fp = os.path.join(working_dir, filename)
    return output_fp


def get_wild_path(directory, wildcard_filename, prefix_asterisk=True):
    wildcard_filename = ("*" + wildcard_filename) if prefix_asterisk else wildcard_filename
    return os.path.join(directory, wildcard_filename)


def get_basename_fps_tuples(parent_dir, wildcard_filename, subdirs_are_basename, prefix_asterisk=True):
    relevant_fps = get_filepaths_from_wildcard(parent_dir, wildcard_filename,
                                               prefix_asterisk, subdirs_are_basename)

    result = []
    for curr_fp in relevant_fps:
        if subdirs_are_basename:
            curr_path, _ = os.path.split(curr_fp)
            basename = os.path.basename(os.path.normpath(curr_path))
        else:
            _, basename, _ = get_file_name_pieces(curr_fp)
            basename = basename.split(".")[0]  # because sometimes there are multiple extensions: .sam.samstats.html

        result.append((basename, curr_fp))

    return result


def get_filepaths_from_wildcard(directory, wildcard_filename, prefix_asterisk=True, all_subdirs=False):
    """Identify all file paths in the input directory that match the input wildcard.

    Example:
        Inputting "/Users/Me/data/", "_aligned.fa" could return ["/Users/Me/data/experiment12_aligned.fa",
            "/Users/Me/data/experiment13_aligned.fa"]

    Args:
        directory (str): The path to the directory of interest.
        wildcard_filename (str): The fixed, shared part of the filenames of interest. Examples: "_aligned.fa",
            "experiment12_*".
        prefix_asterisk (Optional[bool]):  True if an asterisk should be added as the first character of the
            wildcard_filename, False if the wildcard_filename should be used unmodified.  Default is True.

    Returns:
        list(str): A list of all file paths in the input directory that match the wildcard_filename.

    """
    wildcard_filename = (("*" + wildcard_filename) if prefix_asterisk
                         else wildcard_filename)
    if all_subdirs:
        result = _recursively_get_filepaths_from_wildcard(directory, wildcard_filename)
    else:
        wildpath = os.path.join(directory, wildcard_filename)
        # as of python 3.5 glob has a recursive option, so could do all_subdirs case too, but I'm not yet
        # willing to commit to always using 3.5 or above
        result = [x for x in glob.glob(wildpath)]
    return result


def _recursively_get_filepaths_from_wildcard(directory, wildcard_filename):
    # code from https://stackoverflow.com/questions/2186525/use-a-glob-to-find-files-recursively-in-python
    matching_fps = []
    for root, dirnames, filenames in os.walk(directory):
        for filename in fnmatch.filter(filenames, wildcard_filename):
            matching_fps.append(os.path.join(root, filename))
    return matching_fps


def get_filepaths_by_prefix_and_suffix(directory, prefix, suffix, all_subdirs=False):
    suffix_fps = get_filepaths_from_wildcard(directory, suffix, all_subdirs=all_subdirs)
    if prefix is not None and prefix is not "":
        prefix_and_suffix_fps = [x for x in suffix_fps if prefix in x]
    else:
        prefix_and_suffix_fps = suffix_fps
    return prefix_and_suffix_fps


def group_files(filepaths, regex, replacement=""):
    filepaths.sort()  # ensure always combined in same order
    filepaths_by_bases = {}

    for curr_fp in filepaths:
        _, file_base, _ = get_file_name_pieces(curr_fp)  
        condensed_file_base = re.sub(regex, replacement, file_base, 1)
        
        if not condensed_file_base in filepaths_by_bases:
            filepaths_by_bases[condensed_file_base] = [curr_fp]
        else:
            filepaths_by_bases[condensed_file_base].append(curr_fp)  
    
    return filepaths_by_bases


def summarize_filenames_for_prefix_and_suffix(directory, run_prefix, counts_suffix, all_subdirs=False):
    prefix_and_suffix_fps = get_filepaths_by_prefix_and_suffix(directory, run_prefix, counts_suffix,
                                                               all_subdirs=all_subdirs)
    filenames = []
    for curr_fp in prefix_and_suffix_fps:
        _, filename = os.path.split(curr_fp)
        filenames.append(filename)
    filenames.sort()  # sort so order is reproducible
    return "\n".join(filenames)


def verify_or_make_dir(dir_path):
    # makedirs differs from mkdir in that it will make intermediate directories that don't already exist
    os.makedirs(dir_path, exist_ok=True)  # True = is OK if path already exists


def gunzip_wildpath(directory, name_match, keep_gzs=False, do_recursive=False):
    # gunzip the gzipped files; do this from shell because doing through
    # python gzip module is slow
    matching_fps = get_filepaths_from_wildcard(directory, name_match, all_subdirs=do_recursive)
    # note that the -k or --keep switch is only supported in gzip 1.6 or later!
    keep_switch = "-k " if keep_gzs else ""
    for curr_fp in matching_fps:
        gunzip_cmd = "gunzip {0}{1}".format(keep_switch, curr_fp)
        os.system(gunzip_cmd)


def move_to_dir_and_flatten(source_dir, target_dir, name_match):
    matching_fps = get_filepaths_from_wildcard(source_dir, name_match, all_subdirs=True)
    for curr_fp in matching_fps:
        curr_dir, curr_fname = os.path.split(curr_fp)
        if curr_dir != target_dir:
            os.rename(curr_fp, os.path.join(target_dir, curr_fname))


def unzip_and_flatten_files(top_fastqs_dir, ext_name, gzip_ext_name, keep_gzs):
    # first, recursively unzip all <ext_name><gzip_ext_name> (e.g., .fastq.gz) files anywhere under the input dir
    gunzip_wildpath(top_fastqs_dir, ext_name + gzip_ext_name, keep_gzs, True)  # True = do recursive
    # now move all fastqs to top-level directory so don't have to work recursively in future
    move_to_dir_and_flatten(top_fastqs_dir, top_fastqs_dir, ext_name)


def list_and_unzip_files(fastq_top_dir, ext_name, keep_gzs):
    gzip_ext_name = ".gz"

    # examine the existing compressed files
    logging.info("{0}{1} files:".format(ext_name, gzip_ext_name))
    logging.info(summarize_filenames_for_prefix_and_suffix(fastq_top_dir, "",
                                                           "{0}{1}".format(ext_name, gzip_ext_name),
                                                           all_subdirs=True))

    # uncompress them and move them to the top directory
    unzip_and_flatten_files(fastq_top_dir, ext_name, gzip_ext_name, keep_gzs)

    # examine the existing uncompressed files
    logging.info("\n{0} files:".format(ext_name))
    logging.info(summarize_filenames_for_prefix_and_suffix(fastq_top_dir, "", ext_name))
