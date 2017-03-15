# standard libraries
import subprocess

# standard libraries
import logging

def strip_and_append_non_empty(an_input, output_list):
    if isinstance(an_input, bytes):
        an_input = an_input.decode("utf-8")
    stripped_input = an_input.strip()
    if stripped_input != "":
        output_list.append(stripped_input)    

        
def basic_summarizer(err, output, results=None, curr_key=None):
    summary_pieces = []
    strip_and_append_non_empty(err, summary_pieces)
    strip_and_append_non_empty(output, summary_pieces)
    return "\n".join(summary_pieces)


def summarize_subprocess(err, output, results=None, curr_key=None, 
                         summarizer_function=basic_summarizer):      
    summary = summarizer_function(err, output, results, curr_key)

    if curr_key is not None:
        logging.info(curr_key + ":")
    logging.info(summary)
    logging.info("----------------")


def call_subprocess(call_args, stdout_fp=None):
    str_call_args = [str(x) for x in call_args]
    str_output_location = "" if stdout_fp is None else " to {0}".format(stdout_fp)
    logging_msg = "Running {0}{1}".format(" ".join(str_call_args), str_output_location)
    logging.info(logging_msg)

    if stdout_fp is not None:
        stdout_f = open(stdout_fp, 'w')
    else:
        stdout_f = subprocess.PIPE

    process = subprocess.Popen(str_call_args, shell=False, stdout=stdout_f, stderr=subprocess.PIPE)
    output, err = process.communicate()

    if stdout_fp is not None:
        stdout_f.close()
        output = ""

    summarize_subprocess(err, output)