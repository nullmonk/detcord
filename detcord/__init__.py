"""
The primary module for detcord
"""
from .manager import Manager

# Create a host and connection manager
CONNECTION_MANAGER = Manager()


# Create a decorator for the action functions
def action(actionf):
    actionf.detcord_action = True
    return actionf

# Simple display function for pretty printing
def display(obj, **kwargs):
    """
    Pretty print the output of an action
    """
    host = obj.get('host', "")
    for line in obj['stdout'].strip().split('\n'):
        if line:
            print("[{}]".format(host), line, **kwargs)
    for line in obj['stderr'].strip().split('\n'):
        if line:
            print("[{}] ERROR".format(host), line, **kwargs)

