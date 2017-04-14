# standard libraries
import os
import tempfile
import unittest
import warnings

# library under test
import ccbb_pyutils.files_and_paths as ns_test


class TestFunctions(unittest.TestCase):
    def test_check_file_presence_pass(self):
        test_prefix = "myrun"
        test_suffix = "_test.txt"
        temp_test_file = tempfile.NamedTemporaryFile(prefix=test_prefix, suffix=test_suffix)
        temp_dir_name = os.path.dirname(temp_test_file.name)

        real_output = ns_test.check_file_presence(temp_dir_name, test_prefix, test_suffix, all_subdirs=False,
                                                  check_failure_msg=None, just_warn=False)
        self.assertEqual(os.path.basename(temp_test_file.name), real_output)

    def test_check_file_presence_pass_multiple(self):
        test_prefix = "myrun"
        test_suffix = "_test.txt"
        temp_test_file1 = tempfile.NamedTemporaryFile(prefix=test_prefix, suffix=test_suffix)
        temp_dir_name = os.path.dirname(temp_test_file1.name)
        temp_test_file2 = tempfile.NamedTemporaryFile(dir=temp_dir_name, prefix=test_prefix, suffix=test_suffix)

        real_output = ns_test.check_file_presence(temp_dir_name, test_prefix, test_suffix, all_subdirs=False,
                                                  check_failure_msg=None, just_warn=False)
        temp_file_names = [os.path.basename(temp_test_file1.name), os.path.basename(temp_test_file2.name)]
        expected_output = "\n".join(sorted(temp_file_names))
        self.assertEqual(expected_output, real_output)

    def test_check_file_presence_warn(self):
        test_prefix = "myrun"
        test_suffix = "_test.txt"
        temp_file_dir = tempfile.TemporaryDirectory()

        with warnings.catch_warnings(record=True) as warnings_list:
            # Cause all warnings to always be triggered.
            warnings.simplefilter("always")

            real_output = ns_test.check_file_presence(temp_file_dir.name, test_prefix, test_suffix, all_subdirs=False,
                                                      check_failure_msg=None, just_warn=True)

            assert len(warnings_list) == 1
            assert "No files with names beginning with 'myrun' and ending with '_test.txt' were found in " \
                   "directory" in str(warnings_list[-1].message)
            self.assertEqual(0, len(real_output))

    def test_check_file_presence_error_no_custom_msg(self):
        test_prefix = "myrun"
        test_suffix = "_test.txt"
        temp_file_dir = tempfile.TemporaryDirectory()

        with self.assertRaises(RuntimeError) as found_error:
            ns_test.check_file_presence(temp_file_dir.name, test_prefix, test_suffix, all_subdirs=False,
                                                      check_failure_msg=None, just_warn=False)
        self.assertTrue("No files with names beginning with 'myrun' and ending with '_test.txt' were found in "
                        "directory" in str(found_error.exception))

    def test_check_file_presence_error_custom_msg(self):
        custom_msg = "There is a problem!"
        test_prefix = "myrun"
        test_suffix = "_test.txt"
        temp_file_dir = tempfile.TemporaryDirectory()

        with self.assertRaises(RuntimeError) as found_error:
            ns_test.check_file_presence(temp_file_dir.name, test_prefix, test_suffix, all_subdirs=False,
                                                      check_failure_msg=custom_msg, just_warn=False)
        self.assertTrue("There is a problem! No files with names beginning with 'myrun' and ending with '_test.txt' "
                        "were found in directory" in str(found_error.exception))

    def test_expand_path_home_and_var(self):
        home_dir = os.environ['HOME']
        expected_dir = os.path.join(home_dir, "myfile.txt")

        self.assertEqual(expected_dir, ns_test.expand_path("~/myfile.txt"))
        self.assertEqual(expected_dir, ns_test.expand_path("$HOME/myfile.txt"))

    def test_expand_path_abs(self):
        expected_dir = os.path.join(os.getcwd(), "myfile.txt")
        self.assertEqual(expected_dir, ns_test.expand_path("myfile.txt"))


