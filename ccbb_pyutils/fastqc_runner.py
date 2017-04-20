# standard libraries
import os

from ccbb_pyutils.parallel_process_fastqs import parallel_process_files
from ccbb_pyutils.subprocess_summary import call_subprocess

from ccbb_pyutils.files_and_paths import verify_or_make_dir

__author__ = 'Amanda Birmingham'
__maintainer__ = "Amanda Birmingham"
__email__ = "abirmingham@ucsd.edu"
__status__ = "prototype"


def run_fastqc(top_output_dir, fastqc_filepath, ext_name, fastq_fp):
    results_dir = "{0}/fastqc_results".format(top_output_dir)    
    verify_or_make_dir(results_dir)
    
    call_args = [fastqc_filepath]
    call_args.append(fastq_fp)
    call_args.extend(["--extract", "--outdir={0}".format(results_dir)])
    call_subprocess(call_args)


def run_parallel_fastqc(input_dir, output_dir, num_processors,
    fastqc_fp="fastqc", seq_file_ext_name=".fastq"):

    results = parallel_process_files(input_dir, seq_file_ext_name, num_processors,
                run_fastqc,
                [output_dir, fastqc_fp, seq_file_ext_name])
    return results


def run_multiqc(fastqc_results_wildpath=".", output_dir=".", multiqc_fp="multiqc"):
    call_args = _generate_multiqc_args(fastqc_results_wildpath, output_dir, multiqc_fp)
    call_subprocess(call_args)

    output_fp = os.path.join(fastqc_output_dir, "multiqc_report.html")
    result = os.path.relpath(output_fp)
    return result


def _generate_multiqc_args(input_wildpath, fastqc_output_dir, multiqc_fp="multiqc"):
    call_args = [multiqc_fp]
    call_args.append(input_wildpath)
    call_args.extend(["--outdir={0}".format(fastqc_output_dir)])
    return call_args

