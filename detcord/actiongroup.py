'''
Actions that you can run against a host
'''
from subprocess import Popen, PIPE
import shlex
import socket
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

    def build_return(self, host="", stdout="", stderr="", status=0, command=""):
        '''
        Build a dictionary to be returned as the result
        '''
        if host == "":
            host = self.host
        ret = {
            'host': host,
            'stdout': stdout,
            'stderr': stderr,
            'status': status,
            'command': command
        }
        return ret

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
        return self.build_return("", stdout, stderr, 0, "run")

    def script(self, command, stdin=None, sudo = False):
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
        # Send data into sudo if required
        if sudo:
            print("Running as sudo")
            channel.exec_command("sudo -Sp 'detprompt' " + command)
            channel.settimeout(1)
            try:
                stderr = channel.recv_stderr(3000).decode('utf-8')
                if stderr == "detprompt":
                    channel.sendall(self.password + "\n")
            except:
                pass
        else:
            channel.exec_command(command)
        if stdin:
            channel.sendall(stdin)
        channel.shutdown_write()
        BUFF = 8096
        # Wait for the process to close or errors to happen
        exitstatus = channel.recv_exit_status()
        channel.settimeout(1)
        stdout = b''
        stderr = b''
        # Start reading data until we dont have anything to read
        outr = channel.recv_ready()
        errr = channel.recv_stderr_ready()
        while outr or errr:
            if outr:
                stdout += channel.recv(BUFF)
            if errr:
                stderr += channel.recv_stderr(BUFF)
            outr = channel.recv_ready()
            errr = channel.recv_stderr_ready()
        # Get the return value ready to go
        stdout = stdout.decode('utf-8')
        stderr = stderr.decode('utf-8')
        return self.build_return("", stdout, stderr, exitstatus, "script")

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
        return self.build_return("", "", "", 0, "put")

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
        return self.build_return("", "", "", 0, "get")


    def local(self, command, stdin=None):
        '''
        Execute a command. Shove stdin into it if requested
        '''
        proc = Popen(shlex.split(command), shell=True, stdout=PIPE, stderr=PIPE, stdin=PIPE,
                     close_fds=True)
        if stdin:
            proc.write(stdin)
        stdout = proc.stdout.read().decode("utf-8")
        stderr = proc.stderr.read().decode("utf-8")
        status = proc.wait()
        return self.build_return("localhost", stdout, stderr, status, "local")


    def display(self, obj):
        '''
        Pretty print the output of an action
        '''
        host = obj.get('host', "")
        for line in obj['stdout'].strip().split('\n'):
            if line:
                print("[{}]".format(host),line)
        for line in obj['stderr'].strip().split('\n'):
            if line:
                print("[{}] ERROR".format(host),line)


    def close(self):
        pass
