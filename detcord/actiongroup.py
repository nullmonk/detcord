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

    def script(self, command: str, stdin=None, sudo=False, silent=False, interactive=False) -> dict:
        """Run a program on the remote host. stdin can be passed into the program for script
        execution. Interactive mode does not shutdown stdin until the status has closed, do not use
        interactive with commands that read from stdin constantly (e.x. 'bash').

        Args:
            command     (str):  The command to run on the remote host
            stdin       (str, optional):  The stdin to be passed into the running process
            sudo        (bool, optional): Whether or not the command should be run as sudo.
                                          Defaults to False.
            silent      (bool, optional): Whether or not to print the output coming from the hosts.
                                          Defaults to False.
            interactive (bool, optional): Whether or not the program requires further interaction.
                                          Defaults to False.
        Returns:
            dict: Returns a dictionary object containing information about the command
            including the host, stdout, stderr, status code, and the command run on the
            remote host.
                {
                    'host': host,
                    'stdout': stdout,
                    'stderr': stderr,
                    'status': status,
                    'command': command
                }
        """
        def printlive(value: str) -> None:
            """Print out the line to the console

            Args:
                value: The text to write

            Returns:
                None
            """
            print("[{}] live:".format(self.host), str(value.decode('utf-8').strip()))
        # Get the connection from the connection manager
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
        # Use sudo if asked, pass in the correct password to the sudo binary
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

        # If we are given stdin, pass all the data into the process
        if stdin:
            channel.sendall(stdin)
        # If we are in interactive mode, don't shutdown stdin until later
        if not interactive:
            channel.shutdown_write()
        # Read the output a single byte at a time
        BUFF = 1
        # Wait for the process to close or errors to happen
        channel.settimeout(1)
        # If output if not silenced, create tmp strings for the printed output
        if not silent:
            tmp_stdout = b''
            tmp_stderr = b''
        stdout = b''
        stderr = b''
        # Start reading data until the process dies
        while not channel.exit_status_ready():
            # Check if the processes can read data
            outr = channel.recv_ready()
            if outr:
                val = channel.recv(BUFF)
                stdout += val
                # If we are live printing, print each new line
                if not silent and val == b'\n':
                    printlive(tmp_stdout)
                    tmp_stdout = b''
                else:
                    tmp_stdout += val
            errr = channel.recv_stderr_ready()
            if errr:
                val = channel.recv_stderr(BUFF)
                stderr += val
                if not silent and val == b'\n':
                    printlive(tmp_stderr)
                    tmp_stderr = b''
                else:
                    tmp_stderr += val
        # Wait for the process to die
        exitstatus = channel.recv_exit_status()
        # Process all data that came through after the proc died
        outr = channel.recv_ready()
        errr = channel.recv_stderr_ready()
        # Read until there is no more
        while outr or errr:
            if outr:
                val = channel.recv(BUFF)
                stdout += val
                # If we are live printing, print each new line
                if not silent and val == b'\n':
                    printlive(tmp_stdout)
                    tmp_stdout = b''
                else:
                    tmp_stdout += val
            if errr:
                val = channel.recv_stderr(BUFF)
                stderr += val
                if not silent and val == b'\n':
                    printlive(tmp_stderr)
                    tmp_stderr = b''
                else:
                    tmp_stderr += val
            outr = channel.recv_ready()
            errr = channel.recv_stderr_ready()
        # Get the final output ready to go
        stdout = stdout.decode('utf-8')
        stderr = stderr.decode('utf-8')
        return self.build_return("", stdout, stderr, exitstatus, command.strip())

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
