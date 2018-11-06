#/usr/bin/env python3
'''
deploy commands to a competition network

Micah Martin - knif3
'''

from inspect import getmembers
import os.path
import sys
import json
from json.decoder import JSONDecodeError as DecodeError

import ipaddress

from detcord.loader import is_valid_action, run_action
from detcord.exceptions import InvalidDetfile
from detcord.threader import Threader

from detcord import CONNECTION_MANAGER


global detfile
detfile = None

class Hosts(object):
    def __init__(self):
        self.ips = {}
        self.aliases = {}

    def add_host(self, ip, value):
        self.ips[ip] = value

    def add_alias(self, alias, ip):
        self.aliases[alias] = ip

    def lookup(self, term):
        if term not in self.ips:
            if term in self.aliases:
                term = self.aliases[term]
        try:
            return self.ips.get(term)
        except KeyError:
            return None

def loop_actions_and_hosts(hosts, action_functions, threading=True):
    """Loop through all the actions in the given function array
    and all the hosts in the env

    Args:
        env (dict): A dictionary that is imported from the detfile
        action_function (list): A list of action functions to run

    Returns:
        None
    """
    if threading:
        threader = Threader(CONNECTION_MANAGER)
    else:
        threader = False
    for host in hosts.ips.values():
        for action in action_functions:
            # Run the action on the host
            env = {}
            func = getattr(detfile, action)
            if threader:
                threader.run_action(func, host['ip'],
                                    host['user'], host['password'])
            else:
                run_action(func, host, env['user'], env['pass'])

def update_hosts(hosts, topology):
    """List all the valid hosts in the topology file
    """
    for network in topology.get("networks", []):
        for team in topology.get('teams', []):
            for host in network.get("hosts", []):
                data = {}
                ip = network.get('ip').replace('x', str(team))
                ip += "." + host.get('ip')
                alias = host.get("name", False)
                data['ip'] = ip
                data['port'] = host.get('port', env.get('port', 22))
                data['user'] = host.get('user', env.get('user', 'root'))
                data['password'] = host.get('password',
                                            env.get('password', 'changeme'))
                hosts.add_host(ip, data)
                if alias:
                    hosts.add_alias(alias, ip)

            

def get_functions(module):
    """Get the valid detcord action in the file that we can
    execute on remote boxes
    """
    # Parse the actions that we can run
    action_functions = []
    for func in getmembers(module):
        # Make sure the function is decorated as an action
        if is_valid_action(func[1]):
            action_functions += [func]

    # If we have no runnable action, error out
    if not action_functions:
        raise InvalidDetfile("No runnable actions in detfile.py")
    return action_functions

def usage():
    # Print valid functions that the detfile has with the docstring
    print("USAGE: {} <topology> <detfile> <action>[..<action>]".format(sys.argv[0]))

def valid_actions(actions):
    func_strings = []
    for function in actions:
        docstring = function[1].__doc__
        if docstring:
            docstring = docstring.strip().split('\n')[0].strip()
        else:
            docstring = "No description"
        func_strings += ["{} - {}".format(function[0], docstring)]
    print("Valid actions for this detfile are:\n\t{}".format("\n\t".join(func_strings)))


def main():
    """Load a detfile and run the given actions
    Error if there is no valid detfile, error.
    If there is a detfile but no valid actions to run, print the
    available actions
    """
    if len(sys.argv) < 3:
        usage()
        quit()
    # Check if the playbook exists
    try:
        with open(sys.argv[1]) as fil:
            topo = json.load(fil)
    except (FileNotFoundError, DecodeError, Exception) as E:
        #print(E, type(E))
        print("Please give a valid topplogy")
        usage()
        quit()
    if not os.path.exists(sys.argv[2]):
        print("Please give a valid detfile")
        usage()
        quit()
    # Import the detfile that we are trying to load
    path = os.path.dirname(os.path.abspath(sys.argv[2]))
    name = os.path.splitext(os.path.basename(sys.argv[2]))[0]
    sys.path.insert(0, path)
    global detfile
    detfile = __import__(name)
    action_functions = get_functions(detfile)
    if len(sys.argv) < 4:
        "Please give atleast one valid action"
        usage()
        valid_actions(action_functions)
    # Make sure we are calling a valid action
    actions = sys.argv[3:]
    for action in actions:
        if action not in [f[0] for f in action_functions]:
            raise InvalidDetfile("Not a valid action in the detfile: {}".format(action))
    # get/set the environment for the detfile
    global env
    try:
        env = detfile.env
    except AttributeError:
        env = {
            'user': 'root',
            'password': 'changme',
            'port': 22
        }
        detfile.env = env
    global hosts
    hosts = Hosts()
    update_hosts(hosts, topo)
    # Make sure we have set hosts for the detfile
    # Actually run the actions
    loop_actions_and_hosts(hosts, actions)



if __name__ == '__main__':
    main()
