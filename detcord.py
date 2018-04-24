'''
detcord : Action execution on hosts

Micah Martin - knif3
'''

from detcord.actions import ActionGroup
env = {}
env['pass'] = 'mich'
env['user'] = 'micah'

def main(host):
    group = ActionGroup(
        host,
        user = env['user'],
        password = env['pass']
    )
    stdout, stderr = group.run("whoami")
    print("[{}]".format(host), stdout.strip(), stderr.strip())

main("192.168.177.161")
