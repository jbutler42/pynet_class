#!/usr/bin/env python

'''
2. telnetlib

    a. Write a script that connects using telnet to the pynet-rtr1 router. Execute the 'show ip int brief' command on the router and return the output.

Try to do this on your own (i.e. do not copy what I did previously). You should be able to do this by using the following items:

telnetlib.Telnet(ip_addr, TELNET_PORT, TELNET_TIMEOUT)
remote_conn.read_until(<string_pattern>, TELNET_TIMEOUT)
remote_conn.read_very_eager()
remote_conn.write(<command> + '\n')
remote_conn.close()


3. telnetlib (optional - challenge question)

    Convert the code that I wrote here to a class-based solution (i.e. convert over from functions to a class with methods).
'''

from __future__ import print_function
import telnetlib
import time
import socket
import sys

class telnetDevice(object):
    def __init__(self,
                 host,
                 username,
                 password,
                 port=23,
                 timeout=6,
                 wait=1):
        self.host = host
        self.username = username
        self.password = password
        self.port = port
        self.timeout = timeout
        self.wait = wait
        try:
            self.remote_conn = telnetlib.Telnet(host, port, timeout)
        except socket.timeout:
            sys.exit("Could not connect due to socket timeout")

    def send_command(self, cmd):
        self.cmd = cmd.rstrip()
        self.remote_conn.write(self.cmd + '\n')
        time.sleep(1)
        return self.remote_conn.read_very_eager()
    
    def login(self):
        self.output = self.remote_conn.read_until("sername:", self.timeout)
        self.remote_conn.write(self.username + '\n')
        self.output += self.remote_conn.read_until("ssword:", self.timeout)
        self.remote_conn.write(self.password + '\n')
        time.sleep(self.wait)
        self.output += self.remote_conn.read_very_eager()
        return self.output

    def close(self):
        self.remote_conn.close()

def main():
    ip_addr = '50.76.53.27'
    username = 'pyclass'
    password = '88newclass'

    telnet_device = telnetDevice(host=ip_addr,
                                 username=username,
                                 password=password)
    output = telnet_device.login()
    print(output)

    telnet_device.send_command("term len 0")
    print(telnet_device.send_command("show ip int brie"))

    telnet_device.close()

if __name__ == "__main__":
    main()

