#!/usr/bin/env python
import paramiko
from getpass import getpass

from pyclass.common import config
from pyclass.common.entities import entities
(device_ip, device_port, device_type) = entities.ssh_devices['rtr1']
username = entities.entities['ssh_user']
print device_ip, device_port, username


class shellConnection(object):
    def __init__(self, **kwargs):
        self.common = {
            'client': kwargs.get('client', 'paramiko'),
            'username': kwargs.get('username'),
            'password': kwargs.get('password', getpass()),
            'ip': kwargs.get('ip'),
            'port': kwargs.get('port'),
            'dev_name': kwargs.get('dev_name', kwargs.get('ip')),
        }
        self.paramiko_option = {
            'add_host_keys': kwargs.get('add_host_keys', True),
            'look_for_keys': kwargs.get('look_for_keys', False),
            'allow_agent': kwargs.get('allow_agent', False),
            'load_host_keys': kwargs.get('load_host_keys', False),
            'read_timeout': kwargs.get('read_timeout', 6.0),
            'buffer_size': kwargs.get('buffer_size', 65535),
        }
        if 'paramiko' in self.common['client'].lower():
            self.connection = self.get_paramiko_connection()
        elif 'pexpect' in self.common['client'].lower():
            self.connection = self.get_pexpect_connection()
        else:
            self.connection = None
            raise "Invalid client type requested: ", self.common['client']

    def get_paramiko_connection(self):
        self.remote_conn_pre = paramiko.SSHClient()
        if self.paramiko_option['add_host_keys']:
            self.remote_conn_pre.set_missing_host_key_policy(
                paramiko.AutoAddPolicy()
            )
        if self.paramiko_option['load_host_keys']:
            self.remote_conn_pre.load_system_host_keys()
        self.remote_conn_pre.connect(
            self.common['ip'],
            username=self.common['username'],
            password=self.common['password'],
            look_for_keys=self.paramiko_option['look_for_keys'],
            allow_agent=self.paramiko_option['allow_agent'],
            port=self.common['port']
        )
        try:
            remote_conn = self.remote_conn_pre.invoke_shell()
            remote_conn.settimeout(self.paramiko_option['read_timeout'])
            return remote_conn
        except Exception as e:
            print "Got execption, could not invoke shell connection:", e

    def get_pexpect_connection(self):
        pass

    def get_buffer(self, buffer_size=None):
        if buffer_size is None:
            buffer_size = self.paramiko_option['buffer_size']
        raw_output = ""
        while self.connection.recv_ready():
            raw_output += self.connection.recv(buffer_size)
        return raw_output.split('\n')

    def send(self, command):
        if not command.endswith('\n'):
            command = command + '\n'
        self.connection.send(command)

