"""
Keep track of all credentials and connections per host
"""

import os
import paramiko
import socket
from .exceptions import HostNotFound

class Manager(object):
    """
    The manager class for all the hosts and connections needed but the
    different actiongroups
    """
    def __init__(self):
        self.manager = {}
        self.default_pass = "changeme"
        self.default_user = "root"
        try:
            self.timeout = int(os.environ.get("DETCORD_TIMEOUT"))
        except (TypeError, ValueError):
            self.timeout = 5
        

    def remove_host(self, host):
        del self.manager[host.lower().strip()]
    
    def add_host(self, host, port=22, user=None, password=None):
        """Add a host to the host manager

        Args:
            host (str): the host to add. An ip or hostname
            port (int, optional): the port to connect on, default to 22
            user (str): The user to connect with. Defaults to self.default_user
            password (str): The password to connect with. Defaults to default_pass
        """
        if not user:
            user = self.default_user
        if not password:
            password = self.default_pass
        host = host.lower().strip()
        try:
            port = int(port)
        except ValueError:
            raise ValueError("[{}] Invalid option for port. Must be integer: {}".format(host, port))

        if host not in self.manager:
            self.manager[host] = {}
        self.manager[host].update({
            'port': port,
            'user': user,
            'pass': password
        })

    def get_ssh_connection(self, host):
        '''Get the connection for that host or create a
        new connection if none exists
        '''
        def __con():
            """Try twice"""
            try:
                return self.connect(host)
            except paramiko.ssh_exception.SSHException as E:
                return self.connect(host)
        
        host = host.lower().strip()
        if host not in self.manager:
            raise HostNotFound("{} not in Manager".format(host))
        con = self.manager[host].get('ssh', None)
        if con is None:
            try:
                con = __con()
            except socket.gaierror as E:
                if E.errno == -2:
                    raise ValueError("{}: Invalid host given '{}'. Make sure your host is valid".format(str(E), host))
            self.manager[host]['ssh'] = con
        return con
    
    def set_ssh_connection(self, host, connection):
        '''Set a direct connection to the object passed in for the given host.

        Args:
            host (str): The IP address of the host that the connection is established to
            connection (paramiko.SSHClient): The SSHCLient connection that is already established
        Returns:
            bool: Whether or not the connection is alive and works
        Throws:
            HostNotFound: Error if the host is not in the known hosts
        '''
        host = host.lower().strip()
        if host not in self.manager:
            raise HostNotFound("{} not in Manager".format(host))
        if connection is None:
            return False
        
        self.manager[host]['ssh'] = connection
        return True

    def connect(self, host):
        """Create an SSH connection using the given data

        Args:
            host (str): the host to connect to

        Returns:
            paramiko.SSHClient: The new ssh client
        """
        port = self.manager[host]['port']
        user = self.manager[host]['user']
        passwd = self.manager[host]['pass']
        con = paramiko.SSHClient()
        con.set_missing_host_key_policy(SilentTreatmentPolicy())
        #con.load_system_host_keys()
        con.get_host_keys().clear()
        con.connect(timeout=self.timeout, hostname=host, port=port, username=user, password=passwd, look_for_keys=False,
                    allow_agent=False)
        return con

    def close(self):
        for host in self.manager:
            con = host.get("ssh", False)
            if con:
                con.close()

class SilentTreatmentPolicy(paramiko.MissingHostKeyPolicy):
    """Do nothing when we face keys"""
    def missing_host_key(self, *args):
        pass
