'''
detcord : Action execution on hosts

Micah Martin - knif3
'''

from detcord.commands import action, run, local, put, get, display


env = {}  # pylint: disable=invalid-name
env['pass'] = 'root'
env['user'] = 'toor'
env['hosts'] = ['192.168.177.161']

@action
def test():
    '''
    A test action for the detcord project

    Showcases the commands that can be run
    '''
    # You can run simple commands
    ret = run("echo welcome to detcord")
    # You can pass a script to be piped into the process
    ret = run("bash", "echo this is valid\nThis is an error\n")
    # You can run a command as root
    ret = run("whoami", sudo=True)
    # Display can handle the direct output of a command
    display(ret)
    # Run commands locally
    ret = local("whoami")
    # Display can handle stdout and stderr
    display(ret)
    # Put and push files to/from the server
    put("../README.md", "/tmp/README")
    get("/tmp/README", "test.swp")


def support_action():
    '''
    This function is not a detfile action and cannot be called with det
    '''
    pass
