'''
detcord : Action execution on hosts

Micah Martin - knif3
'''

import sys
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
    main()
