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
    ret = host.run("echo welcome to detcord")
    # You can pass a script to be piped into the process
    ret = host.run("bash", "echo this is valid\nThis is an error\n")
    # You can run a command as root
    ret = host.run("whoami", sudo=True)
    # Display will print the results nicely
    display(ret)
    # Run commands locally
    ret = host.local("whoami")
