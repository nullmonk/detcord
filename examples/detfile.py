'''
detcord : Action execution on hosts

Micah Martin - knif3
'''

from detcord import action, display

env = {}  # pylint: disable=invalid-name
env['user'] = 'root'
env['pass'] = 'toor'
env['hosts'] = ['192.168.177.161']
env['threading'] = False  # threading defaults to false

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
    # Display can handle the direct output of a command
    display(ret)
    # Run commands locally
    ret = host.local("whoami")
    # Display can handle stdout and stderr
    display(ret)
    # Put and push files to/from the server
    host.put("README.md", "/tmp/README")
    host.get("/tmp/README", "test.swp")


def support_action():
    '''
    This function is not a detfile action and cannot be called with det
    '''
    pass
