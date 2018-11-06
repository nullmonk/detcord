'''
detcord : Action execution on hosts

Micah Martin - knif3
'''

from detcord import action, display

env = {}  # pylint: disable=invalid-name
env['user'] = 'root'
env['password'] = 'toor'

@action
def test(host):
    '''
    A test action for the detcord project

    Showcases the commands that can be run
    '''
    # You can run simple commands
    ret = host.run("head -n 1 /tmp/README")
    # You can pass a script to be piped into the process
    # Display will print the results nicely
    display(ret)
