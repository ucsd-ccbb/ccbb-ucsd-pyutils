# standard libraries
import enum
import glob
import matplotlib.pyplot as plt
import os.path
import sys

# third-party libraries
import pandas

# ccbb libraries
from ccbbucsd.utilities.files_and_paths import get_basename_fps_tuples

ALIGN_COUNT_PIPELINES = enum.Enum('align_count_pipeline', 'STAR_HTSeq Kallisto')  # SAMstats')

NAME_STR = "Sample"
TOTAL_STR = "Total Reads"
ALIGN_STR = "Aligned Reads"
PERCENT_ALIGN_STR = "Percent Aligned"
UNIQUE_ALIGN_STR = "Uniquely Aligned Reads"
PERCENT_UNIQUE_ALIGN_STR = "Percent Uniquely Aligned"
STATUS_STR = "Notes"
UNKNOWN_STR = "Unavailable"


# # Below is the complete list of labels in the summary file
# g_fastqc_summary_labels = ["Basic Statistics", "Per base sequence quality",
#                   "Per tile sequence quality",
#                   "Per sequence quality scores",
#                   "Per base sequence content", "Per sequence GC content",
#                   "Per base N content", "Sequence Length Distribution",
#                   "Sequence Duplication Levels",
#                   "Overrepresented sequences", "Adapter Content",
#                   "Kmer Content"]
#
#
#
# def make_aligned_reads_plot(summary_stats_df):
#     #Barplot of number of aligned reads per sample
#     plt.figure(figsize=(10,10))
#     ax = plt.subplot(111)
#     summary_stats_df[[NAME_STR, TOTAL_STR,
#         PERCENT_ALIGN_STR]].plot(ax=ax, kind='bar', title='# of Reads')
#     #ax.axis(x='off')
#     ax.axhline(y=10000000, linewidth=2, color='Red', zorder=0)
#     xTickMarks = [x for x in summary_stats_df.Sample.tolist()]
#     xtickNames = ax.set_xticklabels(xTickMarks)
#     plt.setp(xtickNames, rotation=45, ha='right', fontsize=10)
#
#
# def parse_star_alignment_stats(pipeline_output_dir):
#     # Look for each stats file in each relevant subdirectory of the results directory
#     summary_wildpath = os.path.join(pipeline_output_dir, '*/', "Log.final.out")
#     summary_filepaths = [x for x in glob.glob(summary_wildpath)]
#
#     alignment_stats = pandas.DataFrame()
#     for curr_summary_path in summary_filepaths:
#         filename = curr_summary_path.replace(pipeline_output_dir + "/", "")
#         filename2 = filename.replace("/Log.final.out", "")
#         df = pandas.read_csv(curr_summary_path, sep="\t", header=None)
#         raw_reads = df.iloc[[4]]
#         y = raw_reads[1].to_frame()
#         aligned_reads = df.iloc[[7]]
#         z = aligned_reads[1].to_frame()
#         percent_aligned = df.iloc[[8]]
#
#         # print percent_aligned
#         a = percent_aligned[1]
#         b = a.to_string()
#         c = b.replace("%", "")
#         c1 = c.replace("8    ", "")
#         e = float(c1)
#         d = {NAME_STR: pandas.Series(filename2),  # "Raw Reads": pandas.Series(float(y[1])),
#              PERCENT_ALIGN_STR: pandas.Series(float(z[1]))}  # ,
#         # PERCENT_ALIGN_STR: pandas.Series(e)}
#         p = pandas.DataFrame(data=d)
#         alignment_stats = alignment_stats.append(p)
#     return alignment_stats
#
#
# def parse_kallisto_alignment_stats(pipeline_output_dir):
#     counts_wildpath = os.path.join(pipeline_output_dir, "*_counts.txt")
#     counts_fps = [x for x in glob.glob(counts_wildpath)]
#
#     sample_stats = []
#
#     for count_fp in counts_fps:
#         _, count_filename = os.path.split(count_fp)
#         if count_filename == "all_gene_counts.txt": continue
#
#         df = pandas.read_csv(count_fp, sep="\t")
#
#         long_sample_name = df.columns.values[-1]
#         short_sample_name = long_sample_name.split("/")[-1]
#
#         no_nan_df = df.dropna(subset=["gene"])  # NaN in first col
#         counts_series = no_nan_df.ix[:, 3]
#         total_aligned_counts = counts_series.sum()
#
#         sample_stats.append({NAME_STR: short_sample_name, PERCENT_ALIGN_STR: total_aligned_counts})
#
#     alignment_stats = pandas.DataFrame(sample_stats)
#     return alignment_stats
#
#
# def _get_parser_for_pipeline(align_count_pipeline_val):
#     result_func = None
#
#     if align_count_pipeline_val == ALIGN_COUNT_PIPELINES.Kallisto:
#         result_func = parse_kallisto_alignment_stats
#     elif align_count_pipeline_val == ALIGN_COUNT_PIPELINES.STAR_HTSeq:
#         result_func = parse_star_alignment_stats
#     # elif align_count_pipeline_val == ALIGN_COUNT_PIPELINES.SAMstats:
#     #    result_func = parse_samstats_alignment_stats
#     else:
#         raise ValueError(("Unrecognized alignment and counting "
#                           "pipeline specified: '{0}'").format(align_count_pipeline_val))
#
#     return result_func
#
#
# def combine_fastqc_and_alignment_stats(pipeline_output_dir,
#                                        fastqc_stats_df, percent_threshold,
#                                        parser_func=parse_star_alignment_stats):
#     alignment_stats = parser_func(pipeline_output_dir)
#
#     result = pandas.merge(fastqc_stats_df,
#                           alignment_stats, on=NAME_STR)
#     result[PERCENT_ALIGN_STR] = result[PERCENT_ALIGN_STR] / result[
#         TOTAL_STR] * 100
#
#     result = result[[NAME_STR, g_issues_str,
#                      TOTAL_STR, PERCENT_ALIGN_STR, PERCENT_ALIGN_STR, STATUS_STR]]
#
#     fail_mask = (result[STATUS_STR] == g_fail_msg) | (result[
#                                                         PERCENT_ALIGN_STR] < percent_threshold)
#     result[STATUS_STR] = [g_fail_msg if x else '' for x in fail_mask]
#     return (result)
#
#
# def get_fastqc_and_alignment_summary_stats(pipeline_output_dir,
#                                            min_num_total_reads, min_percent_aligned, align_count_pipeline_val):
#     fastqc_results_df = get_fastqc_results(pipeline_output_dir,
#                                            min_num_total_reads)
#
#     parse_stats_func = _get_parser_for_pipeline(align_count_pipeline_val)
#
#     combined_summary_df = combine_fastqc_and_alignment_stats(
#         pipeline_output_dir, fastqc_results_df,
#         min_percent_aligned, parse_stats_func)
#
#     return combined_summary_df
#
#
# def get_fastqc_results(fastqc_results_dir, count_fail_threshold):
#     total_seqs_df = get_fastqc_total_seqs(fastqc_results_dir)
#     statuses_df = get_fastqc_statuses(fastqc_results_dir)
#     result = pandas.merge(statuses_df, total_seqs_df, on=NAME_STR, how="outer")
#     result = result[[NAME_STR, g_issues_str, TOTAL_STR]]
#
#     fail_mask = (result[g_issues_str] != "") | (result[TOTAL_STR] < count_fail_threshold)
#     result[STATUS_STR] = [g_fail_msg if x else '' for x in fail_mask]
#     return (result)
#
#
# def get_fastqc_total_seqs(fastqc_results_dir):
#     result = _loop_over_fastqc_files(fastqc_results_dir,
#                                      "fastqc_data.txt", _find_total_seqs_from_fastqc)
#     return result
#
#
# def get_fastqc_statuses(fastqc_results_dir):
#     result = _loop_over_fastqc_files(fastqc_results_dir,
#                                      "summary.txt", _find_statuses_from_fastqc)
#     return result
#
#
# def get_sample_from_filename(filename):
#     return filename.replace(".fastq.gz", "").strip()
#
#
# def _find_statuses_from_fastqc(line, curr_record):
#     if line.startswith("FAIL") or line.startswith("WARN"):
#         fields = line.split("\t")
#
#         if not NAME_STR in curr_record:
#             sample_name = get_sample_from_filename(fields[2])
#             curr_record = {NAME_STR: sample_name, NAME_STR: ""}
#
#         if fields[1] in g_fastqc_labels_of_interest:
#             if not curr_record[g_issues_str]:
#                 curr_record[g_issues_str] = []
#             curr_record[g_issues_str].append(fields[0] + ": " + fields[1])
#
#     return curr_record
#
#
# def _find_total_seqs_from_fastqc(line, curr_record):
#     filename_str = "Filename"
#
#     if line.startswith(filename_str):
#         temp = line.replace(filename_str, "").strip()
#         curr_record[NAME_STR] = get_sample_from_filename(temp)
#
#     if line.startswith(TOTAL_STR):
#         num_str = line.replace(TOTAL_STR, "").strip()
#         num = int(num_str)
#         curr_record[TOTAL_STR] = float(num)
#
#     return curr_record
#
#
# def _loop_over_fastqc_files(fastqc_results_dir, file_suffix, parse_func):
#     rows_list = []
#
#     for root, dirnames, filenames in os.walk(fastqc_results_dir):
#         for dirname in dirnames:
#             if dirname.endswith("_fastqc"):
#                 file_fp = os.path.join(root, dirname, file_suffix)
#                 with open(file_fp, "r") as file_handle:
#                     curr_record = {}
#
#                     for line in file_handle:
#                         curr_record = parse_func(line, curr_record)
#
#                     if len(curr_record) > 0:
#                         rows_list.append(curr_record)
#
#     outputDf = pandas.DataFrame(rows_list)
#     return outputDf
#
#

# def get_alignments_stats_df(align_count_pipeline_val, pipeline_output_dir, samples_in_subdirs,
#                             min_num_total_reads=None, min_aligned_reads=None, min_percent_unique_aligned=None):
#     parse_stats_func = _get_parser_for_pipeline(align_count_pipeline_val)
#     basic_stats_df = parse_stats_func(pipeline_output_dir, samples_in_subdirs)
#     result = _annotate_stats(basic_stats_df,
#                              min_num_total_reads, min_aligned_reads, min_percent_unique_aligned)
# 
#     return result
# 
# 
# def _get_parser_for_pipeline(align_count_pipeline_val):
#     result_func = None
# 
#     if align_count_pipeline_val == ALIGN_COUNT_PIPELINES.SAMstats:
#         result_func = parse_samstats_alignment_stats
#     else:
#         raise ValueError(("Unrecognized alignment and counting "
#                           "pipeline specified: '{0}'").format(align_count_pipeline_val))
# 
#     return result_func
# 
# 
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
# 
# 
# def _annotate_stats(stats_df, total_threshold=None, aligned_threshold=None, percent_unique_threshold=None):
#     # add percentages
# 
#     calc_percentage = lambda numerator, denominator: UNKNOWN_STR if (
#         numerator == UNKNOWN_STR or denominator == UNKNOWN_STR) else numerator / denominator * 100
# 
#     stats_df[PERCENT_ALIGN_STR] = calc_percentage(stats_df[ALIGN_STR], stats_df[TOTAL_STR])
#     stats_df[PERCENT_UNIQUE_ALIGN_STR] = calc_percentage(stats_df[UNIQUE_ALIGN_STR], stats_df[TOTAL_STR])
# 
#     # add failure msgs as necessary
#     no_fail_msg = ["" for x in stats_df[NAME_STR]]
# 
#     def get_msg(thresh, field):
#         result = no_fail_msg
#         if stats_df[field,0] != UNKNOWN_STR:
#             if thresh is not None:
#                 fail_mask = stats_df[field] < thresh
#                 result = ["Below {0} threshold".format(field) if x else "" for x in fail_mask]
#         return result
# 
#     total_fail_msg = get_msg(total_threshold, TOTAL_STR)
#     aligned_fail_msg = get_msg(aligned_threshold, ALIGN_STR)
#     percent_fail_msg = get_msg(percent_unique_threshold, PERCENT_ALIGN_STR)
#     stats_df[STATUS_STR] = [", ".join(filter(None, x)) for x in zip(total_fail_msg, aligned_fail_msg, percent_fail_msg)]
# 
#     # reorder columns
#     stats_df = stats_df[[NAME_STR, TOTAL_STR, ALIGN_STR, UNIQUE_ALIGN_STR,
#                          PERCENT_ALIGN_STR, PERCENT_UNIQUE_ALIGN_STR, STATUS_STR]]
#     return stats_df


