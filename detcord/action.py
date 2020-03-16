"""
The definitions for an action function
"""
import sys
import functools
from io import StringIO

import __main__


# Create a decorator for the action functions
def action(function):
    """
    A decorator that marks functions as detcord actions and calls the callbacks whenever they are run
    """

    @functools.wraps(function)
    def wrapper(host):
        E = None
        retval = None  # By default, actions return nothing

        # Hook stdout and error so that functions dont print. If this is wrapped, the
        # return value of the function is the result
        if host.__dict__.get("env", {}).get("silent", False):
            retval = StringIO()  # If silent is true, the retval is now set
            sys.stdout = retval
            sys.stderr = retval

        # Call the function
        try:
            function(host)
        except Exception as Ex:
            E = Ex
            pass
        # Set stderr and out back to normal
        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__

        # Call the appropriate callback. If error, call the fail callback
        if isinstance(E, Exception):
            try:
                __main__.on_detcord_action_fail(
                    host=host.host, action=function.__name__, exception=E
                )
            except (AttributeError, TypeError) as _:
                pass
            # Hey pylint, I clearly make sure this is an exception. Learn to read
            raise E  # pylint: disable=raising-bad-type
        else:
            try:
                # If all the output was sent to the new output
                if isinstance(retval, StringIO):
                    retval = retval.getvalue()

                __main__.on_detcord_action(
                    host=host.host, action=function.__name__, return_value=retval
                )
            except (AttributeError, TypeError) as _:
                pass
            return

    wrapper.detcord_action = True
    return wrapper
