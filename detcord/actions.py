'''
Actions that you can run against a host
'''
from . import MainManager
from .exceptions import *
import socket

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
        stdout = stdout.read().decode('utf-8')
        stderr = stderr.read().decode('utf-8')
        return stdout, stderr

    def script(self, command, stdin=None):
        connection = None
        for i in range(2):
            try:
                connection = MainManager.getSSHConnection(self.host)
            except HostNotFound:
                MainManager.addHost(self.host, self.port, self.user, self.password)
                continue
            break
        if not connection:
            raise Exception("No Connection")

        transport = connection.get_transport()
        channel = transport.open_channel("session")
        channel.exec_command(command)
        if stdin:
            channel.sendall(stdin)
        channel.shutdown_write()
        BUFF = 8096
        channel.settimeout(1)
        try:
            stdout = channel.recv(BUFF)
        except socket.timeout:
            stdout = b''
        try:
            stderr = channel.recv_stderr(BUFF)
        except socket.timeout:
            stderr = b''
        stdout = stdout.decode('utf-8')
        stderr = stderr.decode('utf-8')
        return stdout, stderr

    def put(self, local, remote):
        '''
        Put a local file onto the remote host
        '''
        connection = None
        for i in range(2):
            try:
                connection = MainManager.getSSHConnection(self.host)
            except HostNotFound:
                MainManager.addHost(self.host, self.port, self.user, self.password)
                continue
            break
        if not connection:
            raise Exception("No Connection")
        connection = connection.open_sftp()
        connection.put(local, remote)

    def get(self, remote, local):
        '''
        Get a remote file and save it locally
        '''
        connection = None
        for i in range(2):
            try:
                connection = MainManager.getSSHConnection(self.host)
            except HostNotFound:
                MainManager.addHost(self.host, self.port, self.user, self.password)
                continue
            break
        if not connection:
            raise Exception("No Connection")
        connection = connection.open_sftp()
        connection.get(remote, local)


    def display(self, stdout, stderr=()):
        if not isinstance(stdout, str):
            obj = stdout
            stdout = obj[0]
            if len(obj) > 1:
                stderr = obj[1]
        for line in stdout.strip().split('\n'):
            if line:
                print("[{}]".format(self.host),line)
        for line in stderr.strip().split('\n'):
            if line:
                print("[{}] ERROR".format(self.host),line)

    def close(self):
        pass
