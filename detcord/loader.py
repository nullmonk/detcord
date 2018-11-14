#!/usr/bin/env python3
"""
Load and run detcord actions
Can be called by a server

Used by the detonate program as well
"""
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


def run_action(action, host):
    """Run the given action on the host with the username and password
    If the action is not valid, return False

    Args:
        action (function): the action function to run on the host
        host (dict): The host to run the action on
    Returns
        bool: Whether or not the action ran
    """
    action_group = ActionGroup(
        host=host['ip'],
        user=host['user'],
        password=host['password']
    )
    if not is_valid_action(action):
        # not a valid action
        return False
    # Call the action
    action(action_group)
    # Close the new action object
    action_group.close()
    return True
