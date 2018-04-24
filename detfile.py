from detcord.actions import action, run, display

env = {}
env['hosts'] = ['192.168.177.161']
env['user'] = 'micah'
env['pass'] = 'micah'

@action
def HelloWorld():
    ret = run("whoami")
    display(ret)
