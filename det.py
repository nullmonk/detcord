'''
detcord : Action execution on hosts

Micah Martin - knif3
'''

import os.path
import sys
from detcord.exceptions import DetfileNotFound

if not os.path.exists("detfile.py"):
    raise DetfileNotFound("Missing detfile in the current directory")

from inspect import getmembers, isfunction
import detfile
from detcord.actions import ActionGroup

def main():
    env = detfile.env
    if env.get('hosts', False) and len(sys.argv) > 1:
        for host in env['hosts']:
            env['current_host'] = host
            Action = ActionGroup(
                host = host,
                user = env['user'],
                password = env['pass']
            )
            getattr(detfile, sys.argv[1])(Action)
            Action.close()

if __name__ == '__main__':
    # Parse the inputs
    valid_function = [o for o in getmembers(detfile) if isfunction(o[1])]
    if len(sys.argv) < 2:
        # Print valid functions that the detfile has
        print("USAGE: {} <action>[..<action>]")
        func_strings = []
        for function in valid_function:
            docstring = function[1].__doc__
            if docstring:
                docstring = docstring.strip().split('\n')[0].strip()
            else:
                docstring = "No description"
            func_strings += ["{} - {}".format(function[0], docstring)]
        print("Valid actions for this detfile are:\n\t{}".format("\n\t".join(func_strings)))
        quit()

    for action in sys.argv[1:]:
        if action not in [f[0] for f in valid_function]:
            raise Exception("Not a valid action in the detfile: {}".format(action))
    # Actually run the actions
    main()
