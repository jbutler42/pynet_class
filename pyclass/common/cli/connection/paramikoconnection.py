from pyclass.common.cli.connection.base.Base import connectionABC
from pyclass.common.util import parseargs
from paramiko import SSHClient
from paramiko import AutoAddPolicy


class paramikoConnection(connectionABC):

    options = [
        {'add_host_keys': True},
        {'look_for_keys': False},
        {'allow_agent': False},
        {'load_host_keys': False},
        {'receive_timeout': 5.0},
        {'buffer_size': 65535},
    ]

    @parseargs(options)
    def connect(self, *args, **kwargs):
        self.buffer_size = kwargs['buffer_size']
        self.sshClient = SSHClient()
        if kwargs['add_host_keys']:
            self.sshClient.set_missing_host_key_policy(AutoAddPolicy())
        if kwargs['load_host_keys']:
            self.sshClient.load_system_host_keys()
        self.sshClient.connect(
            self._ip,
            username=self._username,
            password=self._password,
            look_for_keys=kwargs['look_for_keys'],
            allow_agent=kwargs['allow_agent'],
            port=self._port
        )
        try:
            self.connection = self.sshClient.invoke_shell()
            self.connection.settimeout(kwargs['receive_timeout'])
            return self.connection
        except Exception as e:
            print(
                "ERROR: Got exception, could not invoke paramiko shell"
                " connection:", e
            )
            return False

    def disconnect(self):
        print "Disconnect"
        self.connection.close()

    def transmit(self, command):
        if not command.endswith('\n'):
            command = command + '\n'
        self.connection.send(command)

    def receive(self, buffer_size=None):
        if buffer_size is None:
            buffer_size = self.buffer_size
        raw_output = ""
        while self.connection.recv_ready():
            raw_output += self.connection.recv(buffer_size)
        return raw_output.split('\n')
