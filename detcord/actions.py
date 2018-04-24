'''
Actions that you can run against a host
'''
from . import MainManager
from .exceptions import *

class ActionGroup(object):
    '''
    Create an action group to run against a host
    '''
    def __init__(self, host, port=22, user=None, password=None):
        self.host = host
        self.port = port
        self.user = user
        self.password = password

    def run(self, command):
        stderr, stdout = None, None
        connection = None
        for i in range(3):
            try:
                connection = MainManager.getSSHConnection(self.host)
            except HostNotFound:
                MainManager.addHost(self.host, self.port, self.user, self.password)
                continue
            break
        if not connection:
            raise Exception("No Connection")
        stdin, stdout, stderr = connection.exec_command(command)
        return stdout.read().decode("utf-8"), stderr.read().decode("utf-8")
