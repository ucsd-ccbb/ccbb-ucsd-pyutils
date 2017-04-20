# standard libraries
import os
import unittest

# library under test
import ccbb_pyutils.fastqc_runner as ns_test


class TestFunctions(unittest.TestCase):
    def test_run_multiqc(self):
        # with path defaults
        real_output = ns_test.run_multiqc(multiqc_fp="echo")
        self.assertEqual("multiqc_report.html", real_output)

        # with specified paths
        expected_output = os.path.relpath(os.path.join(os.environ["HOME"], "multiqc_report.html"))
        input_wildpath = os.path.join(os.environ["HOME"], "*_fastqc.zip")
        real_output2 = ns_test.run_multiqc(input_wildpath, multiqc_fp="echo")
        self.assertEqual(expected_output, real_output2)

    def test__generate_multiqc_args(self):
        # with default
        expected_output = ['multiqc', '/my/input_dir', '--outdir=/your/output_dir']
        real_output = ns_test._generate_multiqc_args("/my/input_dir", "/your/output_dir")
        self.assertListEqual(expected_output, real_output)

        # with all specified
        expected_output2 = ['echo', '/my/input_dir', '--outdir=/your/output_dir']
        real_output2 = ns_test._generate_multiqc_args("/my/input_dir", "/your/output_dir", "echo")
        self.assertListEqual(expected_output2, real_output2)