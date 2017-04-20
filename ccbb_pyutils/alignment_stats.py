# standard libraries
import enum
import glob
import os
import warnings
import zipfile

# third-party libraries
import matplotlib.pyplot as plt
import pandas


def get_align_count_pipelines():
    return enum.Enum('align_count_pipeline', 'STAR_HTSeq Kallisto')  # SAMstats')


# Below is the complete list of labels in the summary file
def get_fastqc_summary_labels():
    return ["Basic Statistics", "Per base sequence quality",
                  "Per tile sequence quality",
                  "Per sequence quality scores",
                  "Per base sequence content", "Per sequence GC content",
                  "Per base N content", "Sequence Length Distribution",
                  "Sequence Duplication Levels",
                  "Overrepresented sequences", "Adapter Content",
                  "Kmer Content"]


def get_sample_from_filename(filename):
    return filename.replace(".fastq.gz", "").strip()


def get_fastqc_and_alignment_summary_stats(align_count_pipeline_val, pipeline_output_dir, num_total_threshold=None,
                                           labels_of_interest=get_fastqc_summary_labels(), num_aligned_threshold=None,
                                           num_unique_aligned_threshold=None, percent_aligned_threshold=None,
                                           percent_unique_aligned_threshold=None):

    fastqc_results_df = _get_fastqc_results_without_msgs(pipeline_output_dir, labels_of_interest)
    alignment_stats_df = get_alignments_stats_df(align_count_pipeline_val, pipeline_output_dir,
                                                 num_total_threshold, num_aligned_threshold,
                                                 num_unique_aligned_threshold,
                                                 percent_aligned_threshold,
                                                 percent_unique_aligned_threshold)

    result = _combine_fastqc_and_alignment_stats(fastqc_results_df, alignment_stats_df, num_total_threshold)

    return result


def _get_default_fail_msg():
    return "CHECK"


def get_fastqc_results(fastqc_results_dir, labels_of_interest, count_fail_threshold, fail_msg=_get_default_fail_msg()):
    total_seqs_df = _get_fastqc_total_seqs(fastqc_results_dir)
    statuses_df = _get_fastqc_statuses(fastqc_results_dir, labels_of_interest)
    result = pandas.merge(statuses_df, total_seqs_df, on=_get_name_str(), how="outer")
    result = result[[_get_name_str(), _get_fastqc_statuses_str(), _get_total_str()]]

    total_fail_msg = _get_thresh_fail_msgs(count_fail_threshold, result, _get_total_str())
    result = _combine_msgs_and_decide_status(result, fail_msg, total_fail_msg, result[_get_fastqc_statuses_str()])
    result = result.drop(_get_fastqc_statuses_str(), axis=1)

    if result.empty:
        warnings.warn("No fastqc results were found in directory '{0}'".format(fastqc_results_dir))

    return result


def _get_fastqc_results_without_msgs(fastqc_results_dir, labels_of_interest):
    total_seqs_df = _get_fastqc_total_seqs(fastqc_results_dir)
    statuses_df = _get_fastqc_statuses(fastqc_results_dir, labels_of_interest)
    result = pandas.merge(statuses_df, total_seqs_df, on=_get_name_str(), how="outer")
    result = result[[_get_name_str(), _get_fastqc_statuses_str(), _get_total_str()]]
    return result


def get_alignments_stats_df(align_count_pipeline_val, pipeline_output_dir, num_total_threshold=None,
                            num_aligned_threshold=None, num_unique_aligned_threshold=None,
                            percent_aligned_threshold=None, percent_unique_aligned_threshold=None):
    parse_stats_func = _get_parser_for_pipeline(align_count_pipeline_val)
    basic_stats_df = parse_stats_func(pipeline_output_dir)
    if basic_stats_df.empty:
        warnings.warn("No alignment statistics were found in directory '{0}'".format(pipeline_output_dir))

    result = _annotate_stats(basic_stats_df, num_total_threshold, num_aligned_threshold, num_unique_aligned_threshold,
                             percent_aligned_threshold, percent_unique_aligned_threshold)
    return result


def make_aligned_reads_plot(summary_stats_df):
    #Barplot of number of aligned reads per sample
    plt.figure(figsize=(10,10))
    ax = plt.subplot(111)
    summary_stats_df[[_get_name_str(), _get_total_str(),
        _get_percent_unique_aligned_str()]].plot(ax=ax, kind='bar', title='# of Reads')
    #ax.axis(x='off')
    ax.axhline(y=10000000, linewidth=2, color='Red', zorder=0)
    xTickMarks = [x for x in summary_stats_df.Sample.tolist()]
    xtickNames = ax.set_xticklabels(xTickMarks)
    plt.setp(xtickNames, rotation=45, ha='right', fontsize=10)


def parse_star_alignment_stats(pipeline_output_dir):
    # Look for each stats file in each relevant subdirectory of the results directory
    summary_wildpath = os.path.join(pipeline_output_dir, '*/', "Log.final.out")
    summary_filepaths = [x for x in glob.glob(summary_wildpath)]

    alignment_stats = pandas.DataFrame()
    for curr_summary_path in summary_filepaths:
        filename = curr_summary_path.replace(pipeline_output_dir + "/", "")
        filename2 = filename.replace("/Log.final.out", "")
        p = _parse_star_log_final_out(filename2, curr_summary_path)
        alignment_stats = alignment_stats.append(p)
    return alignment_stats


def _parse_star_log_final_out(sample_name, curr_summary_path):
    df = pandas.read_csv(curr_summary_path, sep="\t", header=None)
    raw_reads = df.iloc[[4]]
    y = raw_reads[1].to_frame()
    aligned_reads = df.iloc[[7]]
    z = aligned_reads[1].to_frame()
    d = {_get_name_str(): pandas.Series(sample_name),
         _get_total_str(): pandas.Series(float(y[1])),
         _get_uniquely_aligned_str(): pandas.Series(float(z[1]))}
    p = pandas.DataFrame(data=d)
    return p


def parse_kallisto_alignment_stats(pipeline_output_dir):
    counts_wildpath = os.path.join(pipeline_output_dir, "*_counts.txt")
    counts_fps = [x for x in glob.glob(counts_wildpath)]

    sample_stats = []

    for count_fp in counts_fps:
        _, count_filename = os.path.split(count_fp)
        if count_filename == "all_gene_counts.txt": continue

        df = pandas.read_csv(count_fp, sep="\t")

        long_sample_name = df.columns.values[-1]
        short_sample_name = long_sample_name.split("/")[-1]

        no_nan_df = df.dropna(subset=["gene"])  # NaN in first col
        counts_series = no_nan_df.ix[:, 3]
        total_aligned_counts = counts_series.sum()

        sample_stats.append({_get_name_str(): short_sample_name, _get_percent_align_str(): total_aligned_counts})

    alignment_stats = pandas.DataFrame(sample_stats)
    return alignment_stats


def _get_parser_for_pipeline(align_count_pipeline_val):
    pipelines = get_align_count_pipelines()

    if align_count_pipeline_val.name == pipelines.Kallisto.name:
        result_func = parse_kallisto_alignment_stats
    elif align_count_pipeline_val.name == pipelines.STAR_HTSeq.name:
        result_func = parse_star_alignment_stats
    # elif align_count_pipeline_val == ALIGN_COUNT_PIPELINES.SAMstats:
    #    result_func = parse_samstats_alignment_stats
    else:
        raise ValueError(("Unrecognized alignment and counting "
                          "pipeline specified: '{0}'").format(align_count_pipeline_val.name))

    return result_func


def _get_name_str():
    return "Sample"


def _get_total_str():
    return "Total Reads"


def _get_align_str():
    return "Aligned Reads"


def _get_percent_align_str():
    return "Percent Aligned"


def _get_uniquely_aligned_str():
    return "Uniquely Aligned Reads"


def _get_percent_unique_aligned_str():
    return "Percent Uniquely Aligned"


def _get_status_str():
    return "Status"


def _get_notes_str():
    return "Notes"


def _get_unknown_str():
    return "Unavailable"


def _get_fastqc_statuses_str():
    return "FASTQC Messages"


def _get_fastqc_total_seqs(fastqc_results_dir, *func_args):
    result = _loop_over_fastqc_files(fastqc_results_dir,
                                     "fastqc_data.txt", _find_total_seqs_from_fastqc, *func_args)
    return result


def _get_fastqc_statuses(fastqc_results_dir, *func_args):
    result = _loop_over_fastqc_files(fastqc_results_dir,
                                     "summary.txt", _find_fastqc_statuses_from_fastqc, *func_args)

    temp_fastqc_statuses = [", ".join(filter(None, x)) for x in result[_get_fastqc_statuses_str()]]
    result[_get_fastqc_statuses_str()] = temp_fastqc_statuses
    return result


def _loop_over_fastqc_files(fastqc_results_dir, file_suffix, parse_func, *func_args):
    rows_list = []
    fastqc_suffix = "_fastqc"
    zip_suffix = ".zip"

    def collect_record(a_file_handle, *any_func_args):
        curr_record = {}

        for line in a_file_handle:
            curr_record = parse_func(line, curr_record, *any_func_args)

        if len(curr_record) > 0:
            rows_list.append(curr_record)

    fastqc_results_dir = os.path.abspath(fastqc_results_dir)
    for root, dirnames, filenames in os.walk(fastqc_results_dir):
        for dirname in dirnames:
            if dirname.endswith(fastqc_suffix):
                file_fp = os.path.join(root, dirname, file_suffix)
                with open(file_fp, "rb") as summary_file:
                    collect_record(summary_file, *func_args)

        for filename in filenames:
            if filename.endswith(fastqc_suffix + zip_suffix):
                file_fp = os.path.join(fastqc_results_dir, filename)
                with zipfile.ZipFile(file_fp) as fastqc_zip:
                    summary_name = os.path.join(filename.replace(zip_suffix, ""), file_suffix)
                    with fastqc_zip.open(summary_name, 'r') as summary_file:
                        collect_record(summary_file, *func_args)

    outputDf = pandas.DataFrame(rows_list)
    outputDf.sort_values(_get_name_str(), axis=0, inplace=True)
    outputDf.reset_index(drop=True, inplace=True)
    return outputDf


def _find_total_seqs_from_fastqc(line, curr_record):
    filename_str = "Filename"
    total_str = "Total Sequences"

    line = _decode_if_needed(line)

    if line.startswith(filename_str):
        temp = line.replace(filename_str, "").strip()
        curr_record[_get_name_str()] = get_sample_from_filename(temp)

    if line.startswith(total_str):
        num_str = line.replace(total_str, "").strip()
        num = int(num_str)
        curr_record[_get_total_str()] = float(num)

    return curr_record


def _find_fastqc_statuses_from_fastqc(line, curr_record, labels_of_interest):
    line = _decode_if_needed(line)
    fields = line.split("\t")

    if not _get_name_str() in curr_record:
        sample_name = get_sample_from_filename(fields[2])
        curr_record[_get_name_str()] = sample_name
    if not _get_fastqc_statuses_str() in curr_record:
        curr_record[_get_fastqc_statuses_str()] = []

    if line.startswith("FAIL") or line.startswith("WARN"):
        if fields[1] in labels_of_interest:
            curr_record[_get_fastqc_statuses_str()].append(fields[0] + ": " + fields[1])

    return curr_record


def _decode_if_needed(an_input, encoding="utf-8"):
    try:
        an_input.decode
    except AttributeError:
        result = an_input
    else:
        result = an_input.decode(encoding)

    return result


def _combine_fastqc_and_alignment_stats(fastqc_results_wo_msgs_df, alignment_stats_df,
                                        fail_msg=_get_default_fail_msg()):
    fastqc_input_df = fastqc_results_wo_msgs_df.copy()
    fastqc_total_str = _get_total_str() + " (FASTQC)"
    fastqc_input_df = fastqc_input_df.rename(columns={_get_total_str(): fastqc_total_str})
    result = pandas.merge(fastqc_input_df, alignment_stats_df, how='outer',
                          on=[_get_name_str()])
    if len(result.index) != len(fastqc_results_wo_msgs_df.index):
        warnings.warn("fastqc and alignment statistics cannot be merged 1:1 on sample name",
                      RuntimeWarning)
    result = _combine_msgs_and_decide_status(result, fail_msg, result[_get_fastqc_statuses_str()],
                                             result[_get_notes_str()])
    result = result.drop(_get_fastqc_statuses_str(), axis=1)

    return result[[_get_name_str(), fastqc_total_str, _get_total_str(), _get_align_str(), _get_uniquely_aligned_str(),
                  _get_percent_align_str(), _get_percent_unique_aligned_str(), _get_notes_str(), _get_status_str()]]


def _annotate_stats(stats_df, fail_msg=_get_default_fail_msg(), num_total_threshold=None, num_aligned_threshold=None,
                    num_unique_aligned_threshold=None, percent_aligned_threshold=None,
                    percent_unique_aligned_threshold=None):

    # add percentages
    unknown_str = _get_unknown_str()

    output_fields = [_get_name_str(), _get_total_str(), _get_align_str(), _get_uniquely_aligned_str(),
                     _get_percent_align_str(), _get_percent_unique_aligned_str(), _get_notes_str(), _get_status_str()]
    for curr_field in output_fields:
        if not curr_field in stats_df.columns.values:
            stats_df[curr_field] = unknown_str

    stats_df[_get_percent_align_str()] = _calc_percentage(stats_df[_get_align_str()], stats_df[_get_total_str()])
    stats_df[_get_percent_unique_aligned_str()] = _calc_percentage(stats_df[_get_uniquely_aligned_str()],
                                                                  stats_df[_get_total_str()])

    total_fail_msg = _get_thresh_fail_msgs(num_total_threshold, stats_df, _get_total_str())
    aligned_fail_msg = _get_thresh_fail_msgs(num_aligned_threshold, stats_df, _get_align_str())
    unique_aligned_fail_msg = _get_thresh_fail_msgs(num_unique_aligned_threshold, stats_df, _get_uniquely_aligned_str())
    percent_aligned_fail_msg = _get_thresh_fail_msgs(percent_aligned_threshold, stats_df, _get_percent_align_str())
    percent_unique_fail_msg = _get_thresh_fail_msgs(percent_unique_aligned_threshold, stats_df,
                                                    _get_percent_unique_aligned_str())
    stats_df = _combine_msgs_and_decide_status(stats_df, fail_msg, total_fail_msg, aligned_fail_msg,
                                               unique_aligned_fail_msg, percent_aligned_fail_msg,
                                               percent_unique_fail_msg)
    # reorder columns
    stats_df = stats_df[output_fields]
    return stats_df


def _calc_percentage(numerator, denominator):
    unknown_str = _get_unknown_str()
    result = pandas.Series(unknown_str, index=range(0, len(numerator)))
    known_numerator = not (unknown_str in numerator.tolist())
    known_denominator = not (unknown_str in denominator.tolist())
    if known_numerator and known_denominator:
        result = numerator / denominator * 100
    return result


def _get_thresh_fail_msgs(thresh, stats_df, field_name):
    unknown_str = _get_unknown_str()
    stat_series = stats_df[field_name]
    result = ["" for x in stat_series]

    if not (unknown_str in stat_series.tolist()):
        if thresh is not None:
            fail_mask = stat_series < thresh
            result = ["Below {0} threshold".format(field_name) if x else "" for x in fail_mask]
    return result


def _combine_msgs_and_decide_status(stats_df, fail_msg, *msgs):
    result = stats_df.copy()
    result[_get_notes_str()] = [", ".join(filter(None, x)) for x in zip( *msgs)]
    result[_get_status_str()] = [fail_msg if x else '' for x in result[_get_notes_str()]]
    return result


def prune_unavailable_stats(stats_df):
    drop_cols = []
    unknowns = pandas.Series(_get_unknown_str(), index=range(0, len(stats_df.index)))
    result = stats_df.copy()

    for curr_col_name in stats_df.columns.values:
        if stats_df[curr_col_name].equals(unknowns):
            drop_cols.append(curr_col_name)

    result = result.drop(drop_cols, axis=1)
    return result


# def parse_samstats_alignment_stats(pipeline_output_dir, samples_in_subdirs=False):
#     result = _parse_multiple_stats_files(pipeline_output_dir, "*.samstat.html",
#                                          samples_in_subdirs, _parse_single_samstats)
#     return result
#
#
# def _parse_single_samstats(samstats_report_fp):
#     all_dfs = pandas.read_html(samstats_report_fp, header=0)
#     df = all_dfs[0]
#     number_df = df["Number"]
#     aligned_reads = number_df[6]
#     uniquely_aligned_reads = number_df[0]
#     result = [UNKNOWN_STR, aligned_reads, uniquely_aligned_reads]
#     return result
#
#
# def _parse_multiple_stats_files(parent_dir, wildcard_filename, subdirs_are_basename, stats_file_parse_func):
#     basename_and_fp_tuple_list = get_basename_fps_tuples(parent_dir, wildcard_filename, subdirs_are_basename,
#                                                          prefix_asterisk=False)
#
#     cast_if_relevant = lambda x: UNKNOWN_STR if x == UNKNOWN_STR else float(x)
#
#     alignment_stats = pandas.DataFrame()
#     for curr_tuple in basename_and_fp_tuple_list:
#         curr_stats_list = stats_file_parse_func(curr_tuple[1])
#         curr_stats_dict = {NAME_STR: pandas.Series(curr_tuple[0]),
#                            TOTAL_STR: pandas.Series(cast_if_relevant(curr_stats_list[0])),
#                            ALIGN_STR: pandas.Series(cast_if_relevant(curr_stats_list[1])),
#                            UNIQUE_ALIGN_STR: pandas.Series(cast_if_relevant(curr_stats_list[2]))}
#         p = pandas.DataFrame(data=curr_stats_dict)
#         alignment_stats = alignment_stats.append(p)
#
#     return alignment_stats



