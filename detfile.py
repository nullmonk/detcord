'''
detcord : Action execution on hosts

Micah Martin - knif3
'''

from detcord.commands import action, run, local, put, get, display, script


env = {}
env['pass'] = 'root'
env['user'] = 'toor'
env['hosts'] = ['192.168.177.161']

@action
def test():
    '''
    A test action for the detcord project

    Showcases the commands that can be run
    '''
    # You can pass a script to be piped into another program
    ret = script("bash", "echo this is valid\nThis is an error")

    # Display can handle the direct output of a command
    display(ret)
    # You can call simple actions on the remote host
    # You can pull out the direct stdout and stderr
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
