"""
A thread management object
"""
import threading
from queue import Queue
from .actiongroup import ActionGroup

THREAD_TIMEOUT = 1

class Threader(object):
    def __init__(self, connection_manager):
        self.threads = []
        self.queues = {}
        self.conman = connection_manager

    def run_action(self, action, host, username, password):
        actiongroup = ActionGroup(
            host=host,
            user=username,
            password=password
        )
        host = host.lower()
        if host not in self.queues:
            # Create a queue for the host
            self.queues[host] = Queue()
            # make sure the host is in the connection manager
            self.conman.add_host(
                actiongroup.host,
                actiongroup.port,
                actiongroup.user,
                actiongroup.password
            )
            # Get an ssh connection for the thread to use
            connection = self.conman.get_ssh_connection(host)
            thread = threading.Thread(
                target=action_runner,
                args=(connection, self.queues[host])
            )
            self.threads.append(thread)
            thread.start()
        self.queues[host].put((action, actiongroup))

    def close(self):
        self.conman.close()

def action_runner(connection, queue):
    while True:
        try:
            action, actiongroup = queue.get(timeout=THREAD_TIMEOUT)
        except:
            queue.task_done()
            return False
        actiongroup.connection = connection
        action(actiongroup)
    return True
