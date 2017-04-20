# standard libraries
import enum
import io
import unittest

# third-party libraries
import pandas

# library under test
import ccbb_pyutils.alignment_stats as ns_test


class TestFunctions(unittest.TestCase):
    def _get_fastqc_test_data_dir(self):
        return "test_data/fastqc_data/"

    # region _find_total_seqs_from_fastqc
    def test__find_total_seqs_from_fastqc_ignore(self):
        line = "##FastQC	0.11.3"
        input_record = {"not much": "you"}
        expected_record = input_record.copy()
        real_output = ns_test._find_total_seqs_from_fastqc(line, input_record)
        self.assertEqual(expected_record, real_output)

    def test__find_total_seqs_from_fastqc_filename(self):
        line = "Filename	ARH1_S1.fastq.gz"
        input_record = {"not much": "you"}
        expected_record = {"Sample": "ARH1_S1", "not much": "you"}
        real_output = ns_test._find_total_seqs_from_fastqc(line, input_record)
        self.assertEqual(expected_record, real_output)

    def test__find_total_seqs_from_fastqc_total(self):
        line = "Total Sequences	32416013"
        input_record = {"not much": "you"}
        expected_record = {"Total Reads": 32416013.0, "not much": "you"}
        real_output = ns_test._find_total_seqs_from_fastqc(line, input_record)
        self.assertEqual(expected_record, real_output)

    # end region

    # region _find_fastqc_statuses_from_fastqc
    def test__find_fastqc_statuses_from_fastqc_ignore_passed_of_interest(self):
        line = "PASS	Basic Statistics	ARH1_S1.fastq.gz"
        input_record = {"not much": "you"}
        expected_record = {'FASTQC Messages': [], 'Sample': 'ARH1_S1', 'not much': 'you'}
        real_output = ns_test._find_fastqc_statuses_from_fastqc(line, input_record, ["Basic Statistics"])
        self.assertEqual(expected_record, real_output)

    def test__find_fastqc_statuses_from_fastqc_ignore_failed_not_of_interest(self):
        # still should put in file name
        line = "FAIL	Per tile sequence quality	ARH1_S1.fastq.gz"
        input_record = {"not much": "you"}
        expected_record = {'FASTQC Messages': [], 'Sample': 'ARH1_S1', 'not much': 'you'}
        real_output = ns_test._find_fastqc_statuses_from_fastqc(line, input_record, ["Basic Statistics"])
        self.assertEqual(expected_record, real_output)

    def test__find_fastqc_statuses_from_fastqc_ignore_failed_no_notes_has_name(self):
        line = "FAIL	Per tile sequence quality	ARH1_S1.fastq.gz"
        input_record = {'Sample': 'Tester', "not much": "you"}
        expected_record = {'FASTQC Messages': ['FAIL: Per tile sequence quality'], 'Sample': 'Tester', 'not much': 'you'}
        real_output = ns_test._find_fastqc_statuses_from_fastqc(line, input_record, ["Per tile sequence quality"])
        self.assertEqual(expected_record, real_output)

    def test__find_fastqc_statuses_from_fastqc_ignore_failed_has_notes_has_name(self):
        line = "FAIL	Per tile sequence quality	ARH1_S1.fastq.gz"
        input_record = {'FASTQC Messages': ['WARN: Per base sequence content'], 'Sample': 'Tester', 'not much': 'you'}
        expected_record = {'FASTQC Messages': ['WARN: Per base sequence content', 'FAIL: Per tile sequence quality'],
                           'Sample': 'Tester', 'not much': 'you'}
        real_output = ns_test._find_fastqc_statuses_from_fastqc(line, input_record, ["Per tile sequence quality"])
        self.assertEqual(expected_record, real_output)

    def test__find_fastqc_statuses_from_fastqc_ignore_failed_no_notes_no_name(self):
        line = "FAIL	Per tile sequence quality	ARH1_S1.fastq.gz"
        input_record = {"not much": "you"}
        expected_record = {'FASTQC Messages': ['FAIL: Per tile sequence quality'], 'Sample': 'ARH1_S1', 'not much': 'you'}
        real_output = ns_test._find_fastqc_statuses_from_fastqc(line, input_record, ["Per tile sequence quality"])
        self.assertEqual(expected_record, real_output)

    def test__find_fastqc_statuses_from_fastqc_ignore_failed_has_notes_no_name(self):
        line = "FAIL	Per tile sequence quality	ARH1_S1.fastq.gz"
        input_record = {'FASTQC Messages': ['WARN: Per base sequence content'], 'not much': 'you'}
        expected_record = {'FASTQC Messages': ['WARN: Per base sequence content', 'FAIL: Per tile sequence quality'],
                           'Sample': 'ARH1_S1', 'not much': 'you'}
        real_output = ns_test._find_fastqc_statuses_from_fastqc(line, input_record, ["Per tile sequence quality"])
        self.assertEqual(expected_record, real_output)

    # Note: didn't retest all the functionality with WARN, just one representative case based on known
    # structure of the code (whitebox, remember? :)
    def test__find_fastqc_statuses_from_fastqc_ignore_warned_has_notes_has_name(self):
        line = "WARN	Per tile sequence quality	ARH1_S1.fastq.gz"
        input_record = {'FASTQC Messages': ['WARN: Per base sequence content'], 'Sample': 'Tester', 'not much': 'you'}
        expected_record = {'FASTQC Messages': ['WARN: Per base sequence content', 'WARN: Per tile sequence quality'],
                           'Sample': 'Tester', 'not much': 'you'}
        real_output = ns_test._find_fastqc_statuses_from_fastqc(line, input_record, ["Per tile sequence quality"])
        self.assertEqual(expected_record, real_output)

    # end region

    # region _loop_over_fastqc_files
    def test__loop_over_fastqc_files_w_extra_args(self):
        expected_data = [
            {'FASTQC Messages': ['FAIL: Per tile sequence quality', 'WARN: Overrepresented sequences'], 'Sample': 'ARH1_S1'},
            {'FASTQC Messages': ['FAIL: Per tile sequence quality', 'FAIL: Per sequence quality scores',
                       'WARN: Overrepresented sequences'], 'Sample': 'ARH3_S3'}]
        expected_output = pandas.DataFrame(expected_data)

        real_output = ns_test._loop_over_fastqc_files(self._get_fastqc_test_data_dir(), "summary.txt",
                                                      ns_test._find_fastqc_statuses_from_fastqc,
                                                      ["Per base sequence quality", "Per tile sequence quality",
                                                       "Per sequence quality scores", "Overrepresented sequences"])
        self.assertTrue(expected_output.equals(real_output))

    def test__loop_over_fastqc_files_wo_extra_args(self):
        expected_data = [
            {'Total Reads': 32416013.0, 'Sample': 'ARH1_S1'},
            {'Total Reads': 37658828.0, 'Sample': 'ARH3_S3'}]
        expected_output = pandas.DataFrame(expected_data)

        real_output = ns_test._loop_over_fastqc_files(self._get_fastqc_test_data_dir(), "fastqc_data.txt",
                                                      ns_test._find_total_seqs_from_fastqc)
        self.assertTrue(expected_output.equals(real_output))

    # end region

    def test__get_fastqc_statuses(self):
        expected_data = [
            {'FASTQC Messages': 'FAIL: Per tile sequence quality, WARN: Overrepresented sequences', 'Sample': 'ARH1_S1'},
            {'FASTQC Messages':
                 'FAIL: Per tile sequence quality, FAIL: Per sequence quality scores, WARN: Overrepresented sequences',
             'Sample': 'ARH3_S3'}]
        expected_output = pandas.DataFrame(expected_data)

        real_output = ns_test._get_fastqc_statuses(self._get_fastqc_test_data_dir(),
                                                ["Per base sequence quality", "Per tile sequence quality",
                                                 "Per sequence quality scores", "Overrepresented sequences"])
        self.assertTrue(expected_output.equals(real_output))

    def test__get_fastqc_total_seqs(self):
        expected_data = [
            {'Total Reads': 32416013.00000, 'Sample': 'ARH1_S1'},
            {'Total Reads': 37658828.00000, 'Sample': 'ARH3_S3'}]
        expected_output = pandas.DataFrame(expected_data)

        real_output = ns_test._get_fastqc_total_seqs(self._get_fastqc_test_data_dir())
        real_output_rounded = real_output.round(5)

        self.assertTrue(expected_output.equals(real_output_rounded))

    def test__get_fastqc_results_without_msgs(self):
        expected_data = [
            {'FASTQC Messages': '', 'Total Reads': 32416013.0, 'Sample': 'ARH1_S1'},
            {'FASTQC Messages': '', 'Total Reads': 37658828.0, 'Sample': 'ARH3_S3'}]
        expected_output = pandas.DataFrame(expected_data)
        expected_output = expected_output[['Sample', 'FASTQC Messages', 'Total Reads']]

        real_output = ns_test._get_fastqc_results_without_msgs(self._get_fastqc_test_data_dir(),
                                                 ["Per base sequence quality"])
        self.assertTrue(expected_output.equals(real_output))

    def test_get_fastqc_results(self):
        expected_data = [
            {'Total Reads': 32416013.0, "Notes":'Below Total Reads threshold', 'Status': 'CHECK', 'Sample': 'ARH1_S1'},
            {'Total Reads': 37658828.0, 'Notes':'FAIL: Per sequence quality scores','Status': 'CHECK', 'Sample': 'ARH3_S3'}]
        expected_output = pandas.DataFrame(expected_data)
        expected_output = expected_output[['Sample', 'Total Reads', 'Notes','Status']]

        real_output = ns_test.get_fastqc_results(self._get_fastqc_test_data_dir(), ["Per sequence quality scores"],
                                                 32500000)
        self.assertTrue(expected_output.equals(real_output))

    def test__parse_star_log_final_out(self):
        input_txt = """                                 Started job on |	Apr 16 03:25:24
                             Started mapping on |	Apr 16 03:33:31
                                    Finished on |	Apr 16 03:58:18
       Mapping speed, Million of reads per hour |	78.41

                          Number of input reads |	32389200
                      Average input read length |	49
                                    UNIQUE READS:
                   Uniquely mapped reads number |	28693280
                        Uniquely mapped reads % |	88.59%
                          Average mapped length |	49.71
                       Number of splices: Total |	4838469
            Number of splices: Annotated (sjdb) |	4781275
                       Number of splices: GT/AG |	4778522
                       Number of splices: GC/AG |	40848
                       Number of splices: AT/AC |	4101
               Number of splices: Non-canonical |	14998
                      Mismatch rate per base, % |	0.54%
                         Deletion rate per base |	0.02%
                        Deletion average length |	1.73
                        Insertion rate per base |	0.01%
                       Insertion average length |	1.61
                             MULTI-MAPPING READS:
        Number of reads mapped to multiple loci |	2233606
             % of reads mapped to multiple loci |	6.90%
        Number of reads mapped to too many loci |	500365
             % of reads mapped to too many loci |	1.54%
                                  UNMAPPED READS:
       % of reads unmapped: too many mismatches |	0.00%
                 % of reads unmapped: too short |	2.47%
                     % of reads unmapped: other |	0.50%
                                  CHIMERIC READS:
                       Number of chimeric reads |	0
                            % of chimeric reads |	0.00%
"""

        input = io.StringIO(input_txt)
        expected_output_underlying = [{"Sample": "testSample",
                                       "Total Reads": 32389200.0000,
                                       "Uniquely Aligned Reads": 28693280.0000}]
        expected_output = pandas.DataFrame(expected_output_underlying)
        real_output = ns_test._parse_star_log_final_out("testSample", input)
        self.assertTrue(expected_output.equals(real_output))

    def test__annotate_stats_no_fails(self):
        input_underlying = [{"Sample": "testSample2",
                             "Total Reads": 37627298.0000,
                             "Uniquely Aligned Reads": 28792709.0000},
                            {"Sample": "testSample",
                             "Total Reads": 32389200.0000,
                             "Uniquely Aligned Reads": 28693280.0000}]
        input = pandas.DataFrame(input_underlying)
        expected_output_underlying = [{"Sample": "testSample2",
                                       "Total Reads": 37627298.00000,
                                       "Aligned Reads": "Unavailable",
                                       "Uniquely Aligned Reads": 28792709.00000,
                                       "Percent Aligned": "Unavailable",
                                       "Percent Uniquely Aligned": 76.52080,
                                       "Notes": "",
                                       "Status":""},
                                      {"Sample": "testSample",
                                       "Total Reads": 32389200.00000,
                                       "Aligned Reads": "Unavailable",
                                       "Uniquely Aligned Reads": 28693280.00000,
                                       "Percent Aligned": "Unavailable",
                                       "Percent Uniquely Aligned": 88.58904,
                                       "Notes": "",
                                       "Status":""}]
        expected_output_unordered = pandas.DataFrame(expected_output_underlying)
        expected_output = expected_output_unordered[["Sample", "Total Reads", "Aligned Reads", "Uniquely Aligned Reads",
                                                     "Percent Aligned", "Percent Uniquely Aligned", "Notes","Status"]]
        real_output = ns_test._annotate_stats(input, 'check', num_aligned_threshold=1000000,
                                              percent_aligned_threshold=60)
        rounded_real_output = real_output.round(5)
        self.assertTrue(expected_output.equals(rounded_real_output))

    def test__annotate_stats_fails(self):
        input_underlying = [{"Sample": "testSample2",
                             "Total Reads": 37627298.0000,
                             "Uniquely Aligned Reads": 28792709.0000},
                            {"Sample": "testSample",
                             "Total Reads": 32389200.0000,
                             "Uniquely Aligned Reads": 28693280.0000}]
        input = pandas.DataFrame(input_underlying)
        expected_output_underlying = [{"Sample": "testSample2",
                                       "Total Reads": 37627298.00000,
                                       "Aligned Reads": "Unavailable",
                                       "Uniquely Aligned Reads": 28792709.00000,
                                       "Percent Aligned": "Unavailable",
                                       "Percent Uniquely Aligned": 76.52080,
                                       "Notes": "Below Percent Uniquely Aligned threshold",
                                       "Status":"check"},
                                      {"Sample": "testSample",
                                       "Total Reads": 32389200.00000,
                                       "Aligned Reads": "Unavailable",
                                       "Uniquely Aligned Reads": 28693280.00000,
                                       "Percent Aligned": "Unavailable",
                                       "Percent Uniquely Aligned": 88.58904,
                                       "Notes": 'Below Total Reads threshold, Below Percent Uniquely Aligned threshold',
                                       "Status":"check"}]
        expected_output_unordered = pandas.DataFrame(expected_output_underlying)
        expected_output = expected_output_unordered[["Sample", "Total Reads", "Aligned Reads", "Uniquely Aligned Reads",
                                                     "Percent Aligned", "Percent Uniquely Aligned", "Notes", "Status"]]
        real_output = ns_test._annotate_stats(input, 'check', num_total_threshold=32500000,
                                              percent_unique_aligned_threshold=90)
        rounded_real_output = real_output.round(5)
        self.assertTrue(expected_output.equals(rounded_real_output))

    # region _calc_percentage
    def test__calc_percentage_known(self):
        input_numerator = pandas.Series([28792709.0000, 28693280.0000])
        input_denominator = pandas.Series([37627298.0000, 32389200.0000])
        expected_output_list = [76.520799, 88.589036]
        real_output = ns_test._calc_percentage(input_numerator, input_denominator)
        real_output_list = real_output.tolist()
        self.assertEqual(len(expected_output_list), len(real_output_list))
        for curr_index in range(0, len(expected_output_list)):
            self.assertAlmostEqual(expected_output_list[curr_index], real_output_list[curr_index], 4)

    def test__calc_percentage_unknown_numerator(self):
        input_numerator = pandas.Series(["Unavailable", "Unavailable"])
        input_denominator = pandas.Series([28792709.0000, 28693280.0000])
        expected_output = pandas.Series(["Unavailable", "Unavailable"])
        real_output = ns_test._calc_percentage(input_numerator, input_denominator)
        self.assertTrue(expected_output.equals(real_output))

    def test__calc_percentage_unknown_denominator(self):
        input_numerator = pandas.Series([28792709.0000, 28693280.0000])
        input_denominator = pandas.Series(["Unavailable", "Unavailable"])
        expected_output = pandas.Series(["Unavailable", "Unavailable"])
        real_output = ns_test._calc_percentage(input_numerator, input_denominator)
        self.assertTrue(expected_output.equals(real_output))

    # end region

    def test__combine_fastqc_and_alignment_stats_simple(self):
        fastqc_results_df = pandas.DataFrame([
            {'FASTQC Messages': 'Fail something, Warn something else', 'Total Reads': 32416013.0, 'Sample': 'ARH1_S1'},
            {'FASTQC Messages': '', 'Total Reads': 37658828.0, 'Sample': 'ARH3_S3'}])
        alignment_stats_df = pandas.DataFrame([{"Sample": "ARH3_S3",
                                                "Total Reads": 37627298.00000,
                                                "Aligned Reads": "Unavailable",
                                                "Uniquely Aligned Reads": 28792709.00000,
                                                "Percent Aligned": "Unavailable",
                                                "Percent Uniquely Aligned": 76.52080,
                                                "Notes": "",
                                                "Status": ""},
                                               {"Sample": "ARH1_S1",
                                                "Total Reads": 32389200.00000,
                                                "Aligned Reads": "Unavailable",
                                                "Uniquely Aligned Reads": 28693280.00000,
                                                "Percent Aligned": "Unavailable",
                                                "Percent Uniquely Aligned": 88.58904,
                                                "Notes":"Below some threshold",
                                                "Status": "CHECK"}])
        expected_output_unsorted = pandas.DataFrame([{"Sample": "ARH1_S1",
                                             "Total Reads (FASTQC)":32416013.00000,
                                             "Total Reads": 32389200.00000,
                                             "Aligned Reads": "Unavailable",
                                             "Uniquely Aligned Reads": 28693280.00000,
                                             "Percent Aligned": "Unavailable",
                                             "Percent Uniquely Aligned": 88.58904,
                                             "Notes": "Fail something, Warn something else, Below some threshold",
                                             "Status": "CHECK"},
                                            {"Sample": "ARH3_S3",
                                             "Total Reads (FASTQC)": 37658828.00000,
                                             "Total Reads": 37627298.00000,
                                             "Aligned Reads": "Unavailable",
                                             "Uniquely Aligned Reads": 28792709.00000,
                                             "Percent Aligned": "Unavailable",
                                             "Percent Uniquely Aligned": 76.52080,
                                             "Notes": "",
                                             "Status": ''}])
        expected_output = expected_output_unsorted[["Sample", "Total Reads (FASTQC)", "Total Reads", "Aligned Reads",
                                                    "Uniquely Aligned Reads", "Percent Aligned",
                                                    "Percent Uniquely Aligned", "Notes", "Status"]]
        real_output = ns_test._combine_fastqc_and_alignment_stats(fastqc_results_df, alignment_stats_df)
        real_output_rounded = real_output.round(5)
        self.assertTrue(expected_output.equals(real_output_rounded))

    def test_prune_unavailable_stats_some(self):
        input_unsorted = pandas.DataFrame([{"Sample": "ARH1_S1",
                                             "Total Reads (FASTQC)":32416013.00000,
                                             "Total Reads": 32389200.00000,
                                             "Aligned Reads": "Unavailable",
                                             "Uniquely Aligned Reads": 28693280.00000,
                                             "Percent Aligned": "Unavailable",
                                             "Percent Uniquely Aligned": 88.58904,
                                             "Notes": "Fail something, Warn something else, Below some threshold",
                                             "Status": "CHECK"},
                                            {"Sample": "ARH3_S3",
                                             "Total Reads (FASTQC)": 37658828.00000,
                                             "Total Reads": 37627298.00000,
                                             "Aligned Reads": "Unavailable",
                                             "Uniquely Aligned Reads": 28792709.00000,
                                             "Percent Aligned": "Unavailable",
                                             "Percent Uniquely Aligned": 76.52080,
                                             "Notes": "",
                                             "Status": ''}])
        input_sorted = input_unsorted[["Sample", "Total Reads (FASTQC)", "Total Reads", "Aligned Reads",
                                                    "Uniquely Aligned Reads", "Percent Aligned",
                                                    "Percent Uniquely Aligned", "Notes", "Status"]]
        expected_output = input_unsorted[["Sample", "Total Reads (FASTQC)", "Total Reads",
                                                    "Uniquely Aligned Reads",
                                                    "Percent Uniquely Aligned", "Notes", "Status"]]
        real_output = ns_test.prune_unavailable_stats(input_sorted)
        self.assertTrue(expected_output.equals(real_output))


    def test_prune_unavailable_stats_none(self):
        input_unsorted = pandas.DataFrame([{"Sample": "ARH1_S1",
                                             "Total Reads (FASTQC)":32416013.00000,
                                             "Total Reads": 32389200.00000,
                                             "Aligned Reads": 3000000.00000,
                                             "Uniquely Aligned Reads": 28693280.00000,
                                             "Percent Aligned": 9.26235,
                                             "Percent Uniquely Aligned": 88.58904,
                                             "Notes": "Fail something, Warn something else, Below some threshold",
                                             "Status": "CHECK"},
                                            {"Sample": "ARH3_S3",
                                             "Total Reads (FASTQC)": 37658828.00000,
                                             "Total Reads": 37627298.00000,
                                             "Aligned Reads": 3000000.00000,
                                             "Uniquely Aligned Reads": 28792709.00000,
                                             "Percent Aligned": 7.97293,
                                             "Percent Uniquely Aligned": 76.52080,
                                             "Notes": "",
                                             "Status": ''}])
        input_sorted = input_unsorted[["Sample", "Total Reads (FASTQC)", "Total Reads", "Aligned Reads",
                                                    "Uniquely Aligned Reads", "Percent Aligned",
                                                    "Percent Uniquely Aligned", "Notes", "Status"]]
        real_output = ns_test.prune_unavailable_stats(input_sorted)
        self.assertTrue(input_sorted.equals(real_output))

    def test_prune_unavailable_stats_all(self):
        input_sorted = pandas.DataFrame([{"Aligned Reads": "Unavailable",
                                             "Percent Aligned": "Unavailable"},
                                            {"Aligned Reads": "Unavailable",
                                             "Percent Aligned": "Unavailable"}])
        real_output = ns_test.prune_unavailable_stats(input_sorted)
        self.assertTrue(real_output.empty)

    def test__get_parser_for_pipeline_star(self):
        real_output = ns_test._get_parser_for_pipeline(ns_test.get_align_count_pipelines().STAR_HTSeq)
        self.assertEqual("parse_star_alignment_stats", real_output.__name__)

    def test__get_parser_for_pipeline_kallisto(self):
        real_output = ns_test._get_parser_for_pipeline(ns_test.get_align_count_pipelines().Kallisto)
        self.assertEqual("parse_kallisto_alignment_stats", real_output.__name__)

    def test__get_parser_for_pipeline_error(self):
        fake_enum = enum.Enum('align_count_pipeline', 'kablooie')

        with self.assertRaises(ValueError):
            ns_test._get_parser_for_pipeline(fake_enum.kablooie)
