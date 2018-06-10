#!/usr/bin/env python3
"""
Load and run detcord actions
Can be called by a server

Used by the detonate program as well
"""
from . import commands as COMS
from .actiongroup import ActionGroup


def is_valid_action(action):
    """Return whether or not the action function is a valid
    detcord action

    Args:
        action (function): the function to check

    Returns:
        bool: Whether or not the action is valid
    """
    return getattr(action, 'detcord_action', False) != False


def run_action(action, host, username, password):
    """Run the given action on the host with the username and password
    If the action is not valid, return False

    Args:
        action (function): the action function to run on the host
        host (str): The host to run the action on
        username (str): The username to login with
        password (str): The password to login with

    Returns
        bool: Whether or not the action ran
    """
    action_group = ActionGroup(
        host=host,
        user=username,
        password=password
    )
    if not is_valid_action(action):
        # not a valid action
        return False
    # Inject the action object into the commands library
    COMS.Action = action_group
    # Call the action
    action()
    # Close the new action object
    action_group.close()
    return True
