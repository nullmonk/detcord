"""
The primary module for detcord
"""

import functools
# Work around to avoid cryptography warning
import warnings
warnings.filterwarnings(action='ignore',module='.*paramiko.*')

from .manager import Manager
from .exceptions import *
import __main__

# Create a host and connection manager
CONNECTION_MANAGER = Manager()


# Create a decorator for the action functions
def action(function):
    """
    A decorator that marks functions as detcord actions and calls the callbacks whenever they are run
    """
    @functools.wraps(function)
    def wrapper(host):
        E = None
        try:
            retval = function(host)
        except Exception as Ex:
            E = Ex
            pass
        
        # Call the appropriate callback
        if isinstance(E, Exception):
            try:
                __main__.on_detcord_action_fail(
                    host=host.host,
                    action=function.__name__,
                    exception=E
                )
            except (AttributeError, TypeError) as _:
                pass
            # Hey pylint, I clearly make sure this is an exception. Learn to read
            raise E # pylint: disable=raising-bad-type
        else:
            try:
                __main__.on_detcord_action(
                    host=host.host,
                    action=function.__name__,
                    return_value=retval
                )
            except (AttributeError, TypeError) as _:
                pass
            return retval
    wrapper.detcord_action = True
    return wrapper

#def action(actionf):
#    actionf.detcord_action = True
#    return actionf

# Simple display function for pretty printing
def display(obj, **kwargs):
    """
    Pretty print the output of an action
    """
    host = obj.get('host', "")
    for line in obj['stdout'].strip().split('\n'):
        if line:
            print("[{}] [+]:".format(host), line, **kwargs)
    for line in obj['stderr'].strip().split('\n'):
        if line:
            print("[{}] [-]:".format(host), line, **kwargs)

