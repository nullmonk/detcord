'''
detcord : Action execution on hosts

Micah Martin - knif3
'''

from detcord.actions import ActionGroup
env = {}
env['pass'] = 'micah'
env['user'] = 'micah'

def main(host):
    group = ActionGroup(
        host,
        user = env['user'],
        password = env['pass']
    )
    ret = group.script("bash", "echo this is valid\nThis is an error")
    group.display(ret)
    stdout, stderr = group.script("bash", "whoami")
    group.display(stdout, stderr)

main("192.168.3.29")
