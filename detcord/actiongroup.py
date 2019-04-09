"""
Actions that you can run against a host
"""
# pylint: disable=too-many-arguments,fixme
import socket
import logging
import time
from subprocess import Popen, PIPE
from . import CONNECTION_MANAGER
from .exceptions import HostNotFound, NoConnection


class ActionGroup(object):
    """
    Create an action group to run against a host
    """
    def __init__(self, host, port=22, user=None, password=None, env={}):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.connection = None
        self.logger = logging.getLogger("detcord")

    def get_connection(self):
        """Get an SSH connection from the manager, if one doesn't exist,
        then create a new connection and return that. If a connection can not
        be made then raise an exception.

        Returns:
            paramiko.SSHClient: The paramiko connection that we will work with

        Raises:
            NoConnection: Raised when a connection can not be made after
            several tries
        TODO: Convert into paramiko transports instead of SSHConnections
        """
        connection = None
        for _ in range(2):
            try:
                connection = CONNECTION_MANAGER.get_ssh_connection(self.host)
            except HostNotFound:
                CONNECTION_MANAGER.add_host(self.host, self.port, self.user, self.password)
                continue
            break
        if not connection:
            raise NoConnection("Cannot create a connection for " + self.host)
        return connection


    def build_return(self, host="", stdout="", stderr="", status=0, command=""):
        """Build a dictionary to be returned as the result of a command.
        This dictionary is meant to be the output of all "command" like functions

        Args:
            host    (str, optional): The host that the command ran on. Defaults to self.host
            stdout  (str, optional): The stdout of the command run. Defaults to blank.
            stderr  (str, optional): The stderr of the command run. Defaults to blank.
            status  (int, optional): The return status of the command. Defaults to 0
            command (str, optional): The name of the command that was run. Defaults to blank

        Returns:
            dict: Returns a dictionary object containing the information.
                {
                    'host': host,
                    'stdout': stdout,
                    'stderr': stderr,
                    'status': status,
                    'command': command
                }
        """
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

    def run(self, command: str, stdin=None, sudo=False, silent=True, interactive=False,
            connection=None, shell=False) -> dict:
        """Run a program on the remote host. stdin can be passed into the program for scripts
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
            connection  (paramiko.SSHClient, optional): The connection to use for the interaction
            shell       (bool, optional): Whether to invoke a shell or not. May be required for commands
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
        def send_sudo(channel, command, password):
            """Upgrade the command to sudo using the given password.

            Args:
                channel (paramiko.channel): The channel to send the connection over
                command (str): The command to run on the remote host
                password (str): The password to use for sudo

            Return:
                bool: Whether or not the sudo worked
            """
            channel.exec_command("sudo -kSp 'detprompt' " + command)
            channel.settimeout(1)
            try:
                # Sleep here so that we receive all the sudo prompt data
                # When sudo lectures the user, the 'detprompt' might not come
                # in fast enough cause sudo to fail.
                time.sleep(0.25)
                stderr = channel.recv_stderr(3000).decode('utf-8')
                if "detprompt" in stderr:
                    channel.sendall(password + "\n")
                return True
            except socket.timeout:
                # Timeout means no prompt which means root
                return True
            except Exception as exception:  # pylint: disable=broad-except
                print(exception)
                return False
        # Get the connection from the connection manager
        if self.connection is None:
            connection = self.get_connection()
        else:
            connection = self.connection
        transport = connection.get_transport()
        
        channel = transport.open_channel("session")
        if shell:
            channel.get_pty()
            #channel.invoke_shell()
        # Keep track of all our buffers
        retval = {
            'host': self.host,
            'stdout': "",
            'stderr': "",
            'status': 0,
            'command': command
        }
        # Use sudo if asked, pass in the correct password to the sudo binary
        if sudo:
            if not send_sudo(channel, command, self.password):
                print("[!] Cannot run as sudo")
        else:
            channel.exec_command(command)

        # If we are given stdin, pass all the data into the process
        if stdin:
            channel.sendall(stdin)
        # If we are in interactive mode, don't shutdown stdin until later
        if not interactive:
            channel.shutdown_write()
        # Wait for the process to close or errors to happen
        channel.settimeout(1)

        # Start reading data until the process dies
        while not channel.exit_status_ready():
            # pylint: disable=undefined-variable
            stdout, stderr = ActionGroup._read_buffers(channel)
            retval['stdout'] += stdout
            retval['stderr'] += stderr
            # Print the lines if we can
            if not silent and stdout:
                print("[{}] [+]:".format(self.host), str(stdout.strip()))
            if not silent and stderr:
                print("[{}] [-]:".format(self.host), str(stderr.strip()))
        # Wait for the process to die
        retval['status'] = channel.recv_exit_status()
        # Process all data that came through after the proc died
        while channel.recv_ready() or channel.recv_stderr_ready():
            # pylint: disable=undefined-variable
            stdout, stderr = ActionGroup._read_buffers(channel)
            retval['stdout'] += stdout
            retval['stderr'] += stderr
            # Print the lines if we can
            if not silent and stdout:
                print("[{}] [+]:".format(self.host), str(stdout.strip()))
            if not silent and stderr:
                print("[{}] [-]:".format(self.host), str(stderr.strip()))
        # Close the channel
        channel.close()
        return retval

    def put(self, local, remote, sudo=False, tmp=None):
        """
        Put a local file onto the remote host

        Args:
            local (str): the local file path to send
            remote (str): the remote location to store the file
            sudo (bool, optional): Whether to copy the file into a priviledged location
            tmp (str, optional): if using sudo, the temporary location to write to, needs to be
                                 accessable to the unprivledged user
        """
        # If sudo, then move it into a temporary area
        if sudo:
            if not tmp:
                tmp = "/tmp/det_tmp_file"
            command = "mv {} {}".format(tmp, remote)
            remote = tmp # The new upload loc. is tmp

        connection = self.get_connection()
        connection = connection.open_sftp()
        connection.put(local, remote)
        #If we are using sudo, move the staged file to another location
        if sudo:
            self.run(command, sudo=True)
        return self.build_return("", "", "", 0, "put")

    def get(self, remote, local):
        """
        Get a remote file and save it locally
        """
        connection = self.get_connection()
        connection = connection.open_sftp()
        connection.get(remote, local)
        return self.build_return("", "", "", 0, "get")


    def local(self, command, stdin=None, sudo=False):
        """
        Execute a command. Shove stdin into it if requested
        """
        proc = Popen(command, shell=True, stdout=PIPE, stderr=PIPE, stdin=PIPE,
                     close_fds=True)
        if stdin:
            stdout, stderr = proc.communicate(stdin)
        else:
            stdout, stderr = proc.communicate()
        if sudo:
            logging.warn("sudo on local command not implemented")
        stdout = stdout.decode("utf-8")
        stderr = stderr.decode("utf-8")
        status = proc.wait()
        return self.build_return("localhost", stdout, stderr, status, "local")

    @staticmethod
    def _read_buffers(channel):
        """
        Read a line of stdout and stderr from the channel.
        Return the stdin and stdout as strings

        Args:
            channel (paramiko.Channel): The channel to read from

        Returns:
            tuple: A tuple containing the stdout and stderr
        """
        stdout = b''
        stderr = b''
        char = None
        # Loop until there is nothing to get or we hit a newline
        out_ready = channel.recv_ready()
        while out_ready and char != b'\n':
            char = channel.recv(1)
            stdout += char
            out_ready = channel.recv_ready()
        # Do the same for stderr
        err_ready = channel.recv_stderr_ready()
        while err_ready and char != b'\n':
            char = channel.recv_stderr(1)
            stderr += char
            err_ready = channel.recv_stderr_ready()
        return stdout.decode('utf-8'), stderr.decode('utf-8')


    def close(self):
        """What to do when closing the object?
        """
        pass
