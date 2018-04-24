'''
detcord : Action execution on hosts

Micah Martin - knif3
'''

from inspect import getmembers, isfunction
import detfile
from detcord.actions import ActionGroup

def main():
    print(detfile.env)
    print([o for o in getmembers(detfile) if isfunction(o[1])])
    '''
    group = ActionGroup(
        host = env['curr_host'],
        user = env['user'],
        password = env['pass']
    )
    test(group)
    group.close()
    '''

if __name__ == '__main__':
    main()
