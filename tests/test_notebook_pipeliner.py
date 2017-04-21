# standard libraries
import os
import tempfile
import unittest

import ccbb_pyutils.notebook_runner as ns_runner

import ccbb_pyutils.notebook_pipeliner as ns_test


class TestFunctions(unittest.TestCase):
    # no tests for _get_methods_folder_name because it is so simple

    # no tests for _execute_run because it is high-level and thus a pain to test, but is made up of just calls
    # to tested functions (_add_run_prefix_and_dir_to_params, _create_run_and_methods_dirs, _run_and_output_notebook)

    @staticmethod
    def write_temp_nb_file(get_str_1=True, parent_dir=None):
        input_nb_obj = tempfile.NamedTemporaryFile(dir=parent_dir, suffix=".ipynb")
        return TestFunctions.write_nb_str_to_file_obj(input_nb_obj, get_str_1)

    @staticmethod
    def get_temp_nb_str(get_str_1):
        nb_str_1 = """{
 "cells": [
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "A non-code cell"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {
    "collapsed": true
   },
   "outputs": [],
   "source": [
    "x = 5\\n",
    "y = \\"blue\\""
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {
    "collapsed": false
   },
   "outputs": [],
   "source": [
    "print(\\"x is {0} and y is {1}\\".format(x, y))"
   ]
  }
 ],
 "metadata": {
  "kernelspec": {
   "display_name": "Python 3",
   "language": "python",
   "name": "python3"
  },
  "language_info": {
   "codemirror_mode": {
    "name": "ipython",
    "version": 3
   },
   "file_extension": ".py",
   "mimetype": "text/x-python",
   "name": "python",
   "nbconvert_exporter": "python",
   "pygments_lexer": "ipython3",
   "version": "3.4.5"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 1
}
"""
        nb_str_2 = """{
 "cells": [
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "A non-code cell"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {
    "collapsed": true
   },
   "outputs": [],
   "source": [
    "x = 5\\n",
    "g_run_prefix = \\"blue\\""
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {
    "collapsed": false
   },
   "outputs": [],
   "source": [
    "print(\\"x is {0} and g_run_prefix is {1}\\".format(x, g_run_prefix))"
   ]
  }
 ],
 "metadata": {
  "kernelspec": {
   "display_name": "Python 3",
   "language": "python",
   "name": "python3"
  },
  "language_info": {
   "codemirror_mode": {
    "name": "ipython",
    "version": 3
   },
   "file_extension": ".py",
   "mimetype": "text/x-python",
   "name": "python",
   "nbconvert_exporter": "python",
   "pygments_lexer": "ipython3",
   "version": "3.4.5"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 1
}
"""
        return nb_str_1 if get_str_1 else nb_str_2

    @staticmethod
    def write_nb_str_to_file_obj(input_nb_obj, get_str_1=True):
        input_nb_str = TestFunctions.get_temp_nb_str(get_str_1)
        input_nb_obj.write(bytes(input_nb_str, 'utf-8'))
        input_nb_obj.seek(0)
        return input_nb_obj

    @staticmethod
    def get_html_subset(subset_name):

        updated_subset_1 = """<div class="output_subarea output_stream output_stdout output_text">
<pre>x is 6 and y is blue
</pre>
"""

        updated_subset_2 = """<div class="output_subarea output_stream output_stdout output_text">
<pre>x is 5 and g_run_prefix is faked_run_prefix
</pre>
"""

        if subset_name == "updated_1":
            result = updated_subset_1
        elif subset_name == "updated_2":
            result = updated_subset_2
        else:
            raise ValueError("Unrecognized subset_name '{0}'".format(subset_name))

        return result


    def test_execute_run_from_full_params(self):
        temp_notebook_dir = tempfile.TemporaryDirectory()
        temp_project_dir = tempfile.TemporaryDirectory()

        nb_1_filename = "nb1.ipynb"
        nb_1_fp = os.path.join(temp_notebook_dir.name, nb_1_filename)
        with open(nb_1_fp, 'w+b') as nb1:
            TestFunctions.write_nb_str_to_file_obj(nb1, get_str_1=True)

        nb_2_filename = "nb2.ipynb"
        nb_2_fp = os.path.join(temp_notebook_dir.name, nb_2_filename)
        with open(nb_2_fp, 'w+b') as nb2:
            TestFunctions.write_nb_str_to_file_obj(nb2, get_str_1=False)
        notebooks_list = [nb_1_filename, nb_2_filename]

        input_params = {"x": 6,
                        "z": "red",
                        "notebook_dir": temp_notebook_dir.name,
                        "notebook_basenames_list": notebooks_list,
                        "processed_data_dir": temp_project_dir.name}

        preprocessing_func = lambda x: {"g_" + k: v for k, v in x.items()}
        faked_run_prefix = "faked_run_prefix"

        ns_test.execute_run_from_full_params(input_params, params_preprocess_func=preprocessing_func,
                                             test_val=faked_run_prefix)

        methods_dir_name = os.path.join(temp_project_dir.name, faked_run_prefix, "methods")
        output_nb_1_fp = os.path.join(methods_dir_name, faked_run_prefix + "_" + nb_1_filename)
        output_nb_1 = ns_runner.read_in_notebook(output_nb_1_fp)
        self.assertEqual("x is 5 and y is blue\n", output_nb_1.cells[2].outputs[0]["text"])
        output_nb_1_html_fp = output_nb_1_fp.replace("ipynb", "html")
        with open(output_nb_1_html_fp) as f:
            real_html = f.read()
        self.assertTrue("x is 5 and y is blue\n" in real_html)

        output_nb_2_fp = os.path.join(methods_dir_name, faked_run_prefix + "_" + nb_2_filename)
        output_nb_2 = ns_runner.read_in_notebook(output_nb_2_fp)
        self.assertEqual("x is 5 and g_run_prefix is faked_run_prefix\n", output_nb_2.cells[2].outputs[0]["text"])
        output_nb_2_html_fp = output_nb_2_fp.replace("ipynb", "html")
        with open(output_nb_2_html_fp) as f:
            real_html = f.read()
        self.assertTrue(TestFunctions.get_html_subset("updated_2") in real_html)

    def test__mangle_notebook_name(self):
        real_output = ns_test._mangle_notebook_name("   Simple Test Notebook.ipynb ", "20170000000000_testData")
        # Note that the original notebook name is lower-cased and that all interior whitespace is replaced with
        # underscores, while leading/trailing whitespace is stripped
        self.assertEqual("20170000000000_testData_simple_test_notebook", real_output)

    def test__get_output_fp(self):
        input_notebook_fp = "/my/notebook_dir/Simple Test Notebook.ipynb"
        input_methods_dir = "/my/project_dir/methods_dir/"
        real_output = ns_test._get_output_fp(input_notebook_fp, "20170000000000_testData",
                                             input_methods_dir, ".html")
        self.assertEqual("/my/project_dir/methods_dir/20170000000000_testData_simple_test_notebook.html",
                         real_output)

    # region _create_run_and_methods_dirs
    def test__create_run_and_methods_dirs_new(self):
        temp_project_dir = tempfile.TemporaryDirectory()
        run_dir = os.path.join(temp_project_dir.name, "false_run_prefix")
        expected_output_fp = os.path.join(run_dir, "methods")
        self.assertFalse(os.path.exists(expected_output_fp))
        output_fp = ns_test._create_run_and_methods_dirs(run_dir)
        self.assertEqual(expected_output_fp, output_fp)
        self.assertTrue(os.path.exists(output_fp))

    def test__create_run_and_methods_dirs_existing_partial(self):
        temp_project_dir = tempfile.TemporaryDirectory()
        run_dir = os.path.join(temp_project_dir.name, "false_run_prefix")
        expected_output_fp = os.path.join(run_dir, "methods")
        self.assertFalse(os.path.exists(run_dir))
        os.mkdir(run_dir)
        self.assertTrue(os.path.exists(run_dir))
        output_fp = ns_test._create_run_and_methods_dirs(run_dir)
        self.assertEqual(expected_output_fp, output_fp)
        self.assertTrue(os.path.exists(output_fp))

    def test__create_run_and_methods_dirs_existing_all(self):
        temp_project_dir = tempfile.TemporaryDirectory()
        run_dir = os.path.join(temp_project_dir.name, "false_run_prefix")
        expected_output_fp = os.path.join(run_dir, "methods")
        self.assertFalse(os.path.exists(expected_output_fp))
        os.mkdir(run_dir)
        os.mkdir(expected_output_fp)
        self.assertTrue(os.path.exists(expected_output_fp))
        output_fp = ns_test._create_run_and_methods_dirs(run_dir)
        self.assertEqual(expected_output_fp, output_fp)
        self.assertTrue(os.path.exists(output_fp))

    # end region

    def test__run_and_output_notebook(self):
        input_dict = {"x": 6,
                      "z": "red"}

        temp_methods_dir = tempfile.TemporaryDirectory()
        temp_notebook_file_obj = TestFunctions.write_temp_nb_file()
        input_nb_dir, input_nb_filename = os.path.split(temp_notebook_file_obj.name)

        output_notebook_fp, output_html_fp = ns_test._run_and_output_notebook(input_nb_dir, input_nb_filename,
                                                                              input_dict, "fake_run_prefix",
                                                                              temp_methods_dir.name)

        output_nb = ns_runner.read_in_notebook(output_notebook_fp)
        # test that the new variable has been correctly inserted and used to generate output in subsequent code cells
        self.assertEqual("x is 6 and y is blue\n", output_nb.cells[2].outputs[0]["text"])

        with open(output_html_fp) as f:
            real_html = f.read()
        self.assertTrue(TestFunctions.get_html_subset("updated_1") in real_html)

    # region _add_run_prefix_and_dir_to_params
    def test__add_run_prefix_and_dir_to_params_minimal_inputs(self):
        input_dict = {"x": 6,
                      "z": "red"}
        faked_run_prefix = "faked_run_prefix"
        expected_run_dir = "/my/project_dir/" + faked_run_prefix
        expected_run_params = {"x": 6,
                                "z": "red",
                                "run_prefix": faked_run_prefix,
                                "run_dir": expected_run_dir}
        run_prefix, run_dir, run_params = ns_test._add_run_prefix_and_dir_to_params("/my/project_dir/", input_dict,
                                                                                    test_val=faked_run_prefix)
        self.assertEqual(faked_run_prefix, run_prefix)
        self.assertEqual(expected_run_dir, run_dir)
        self.assertEqual(expected_run_params, run_params)

    def test__add_run_prefix_and_dir_to_params_w_run_prefix(self):
        faked_run_prefix = "preexisting_run_prefix"
        input_dict = {"x": 6,
                      "z": "red",
                      "run_prefix": faked_run_prefix}
        expected_run_dir = "/my/project_dir/" + faked_run_prefix
        expected_run_params = {"x": 6,
                                "z": "red",
                                "run_prefix": faked_run_prefix,
                                "run_dir": expected_run_dir}
        run_prefix, run_dir, run_params = ns_test._add_run_prefix_and_dir_to_params("/my/project_dir/", input_dict)
        self.assertEqual(faked_run_prefix, run_prefix)
        self.assertEqual(expected_run_dir, run_dir)
        self.assertEqual(expected_run_params, run_params)

    def test__add_run_prefix_and_dir_to_params_w_run_dir(self):
        faked_run_prefix = "faked_run_prefix"
        expected_run_dir = "/my/project_dir/" + faked_run_prefix
        input_dict = {"x": 6,
                      "z": "red",
                      "run_dir": expected_run_dir}
        expected_run_params = {"x": 6,
                                "z": "red",
                                "run_prefix": faked_run_prefix,
                                "run_dir": expected_run_dir}
        run_prefix, run_dir, run_params = ns_test._add_run_prefix_and_dir_to_params("/my/project_dir/", input_dict,
                                                                                    test_val=faked_run_prefix)
        self.assertEqual(faked_run_prefix, run_prefix)
        self.assertEqual(expected_run_dir, run_dir)
        self.assertEqual(expected_run_params, run_params)

    def test__add_run_prefix_and_dir_to_params_w_all_inputs(self):
        faked_run_prefix = "preexisting_run_prefix"
        expected_run_dir = "/my/project_dir/" + faked_run_prefix
        input_dict = {"x": 6,
                      "z": "red",
                      "run_prefix": faked_run_prefix,
                      "run_dir": expected_run_dir}
        expected_run_params = {"g_x": 6,
                                "g_z": "red",
                                "g_run_prefix": faked_run_prefix,
                                "g_run_dir": expected_run_dir}
        preprocessing_func = lambda x: {"g_"+k:v for k,v in x.items()}

        run_prefix, run_dir, run_params = ns_test._add_run_prefix_and_dir_to_params("/my/project_dir/", input_dict,
                                                                                    preprocessing_func)
        self.assertEqual(faked_run_prefix, run_prefix)
        self.assertEqual(expected_run_dir, run_dir)
        self.assertEqual(expected_run_params, run_params)

    # end region


