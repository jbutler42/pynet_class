from abc import ABCMeta
from abc import abstractmethod


class connectionABC(object):
    """ABC for Connections.

    > username: Username to establish connection as.
        - type: string
    > password: Password to authenticate username.
        - type: string
    > ip: Internet Protocol address to connect to.
        - type: string
    > port: TCP port to connect to.
        - type: integer between 1 - 65535
    > name: Name of connection.

    < conn: connection object
        - type: connection object."""

    __metaclass__ = ABCMeta

    options = []

    def __init__(self, username, password, ip, port, name):
        self._username = username
        self._password = password
        self._ip = ip
        self._port = port
        self._name = name

    @abstractmethod
    def connect(self):
        """Connect and return connection object."""
        pass

    @abstractmethod
    def transmit(self):
        """Send something."""
        pass

    @abstractmethod
    def receive(self):
        """Receive something."""
        pass

    @abstractmethod
    def disconnect(self):
        """Disconnect."""
        pass
