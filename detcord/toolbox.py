"""
Various tools that can be importe and used by detfiles
"""
import datetime
import re
# pylint: disable=unused-import
from urllib.request import urlretrieve as wget


def strip_colors(string: str) -> str:
    """Remove all the ANSI escape sequences from the given string.
    This will strip all color from output.

    Args:
        string: The string to remove the data from

    Returns:
        str: The new string without all the ANSI escapes
    """
    ansicodes = re.compile(r'\x1B\[[0-?]*[ -/]*[@-~]')
    return ansicodes.sub('', string)


def save_results(path, result):
    """Write the output of a command to the given filename.
    The file contains the stdin, stdout and timestamp of the result

    Args:
        path (str): the filename to save to
        result (dict): the result of a `script` or `run` command

    Returns:
        bool: whether or not the save was successful


    """
    try:
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(path, 'a') as outf:
            outf.write(now+"\n")
            outf.write(result.get('stdout', ''))
            outf.write("\n-- Stderr --\n")
            outf.write(result.get('stderr', ''))
        return True
    except IOError as exception:
        print(exception)
        return False

def log_action(action, host=""):
    '''Write a log to a logfile
    '''
    try:
        now = datetime.datetime.now().strftime("%H:%M:%S")
        with open("logs/actions.log", 'a') as outf:
            outf.write("{}: [{}] {}\n".format(now, host, action))
        return True
    except IOError:
        return False
