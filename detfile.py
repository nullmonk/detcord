'''
detcord : Action execution on hosts

Micah Martin - knif3
'''

from detcord.actions import ActionGroup


env = {}
env['pass'] = 'micah'
env['user'] = 'micah'
env['hosts'] = ['192.168.177.161']

def test(Action):
    '''
    A test action for the detcord project

    Showcases the commands that can be run
    '''
    # You can pass a script to be piped into another program
    ret = Action.script("bash", "echo this is valid\nThis is an error")
    # Display can handle the direct output of a command
    Action.display(ret)
    # You can call simple actions on the remote host
    # You can pull out the direct stdout and stderr
    ret = Action.local("whoami")
    # Display can handle stdout and stderr
    Action.display(ret)
    # Put and push files to/from the server
    #Action.put("README.md", "/tmp/README")
    #Action.get("/tmp/README", "test.swp")
