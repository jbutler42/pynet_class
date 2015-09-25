from pyclass.common.entities import entities
from pyclass.week4.shell import shellConnection
from time import sleep


def get_supported_device_types():
    types = [
        'ios',
        'junos',
    ]
    return types


def concrete(dev_type, thing_to_decode, **kwargs):
    decoded_things = {}
    dev_type = dev_type.lower()
    supported_types = get_supported_device_types()
    if dev_type not in supported_types:
        raise "Device type not supported for decode:", dev_type
    for supported_type in supported_types:
        decoded_things[supported_type] = {}
    decoded_things['ios'].update(
        {
            'disable paging': 'term len 0',
            'log buffer size': 'logging buffered {}'.format(kwargs.get('size')),
            'config level': 'config t',
            'priv level': 'enable',
            'top level': 'end',
            'about': 'show version',
        }
    )
    decoded_thing = decoded_things[dev_type].get(thing_to_decode.lower())
    return decoded_thing
        

def get_ssh_conn(ip, port, username):
    conn = shellConnection(
        ip=ip,
        port=port,
        username=username,
    )
    return conn


def print_output(output):
    if type(output) != type(list()):
        output = list(output)
    for line in output:
        print line


def psend(conn, cmd):
    conn.send(cmd)
    sleep(1.3)
    output = conn.get_buffer()
    print_output(output)


def setup_device(conn, dev_type):
    if dev_type == 'ios':
         abstract_cmds = [
             'disable paging',
         ]
    for abstract_cmd in abstract_cmds:
        cmd = concrete(dev_type, abstract_cmd)
        psend(conn, cmd)
             

def main():
    dev_name = 'rtr2'
    username = entities.entities['ssh_user']
    (device_ip, device_port, device_type) = entities.ssh_devices[dev_name]

    conn = get_ssh_conn(device_ip, device_port, username)

    setup_device(conn, device_type)

    cmd = concrete(device_type, 'about')
    psend(conn, cmd)
    
    cmd = 'show logging'
    psend(conn, cmd)
    cmd = concrete(device_type, 'config level')
    psend(conn, cmd)
    cmd = concrete(device_type, 'log buffer size', size=4096)
    psend(conn, cmd)
    cmd = concrete(device_type, 'top level')
    psend(conn,cmd)
    cmd = 'show logging'
    psend(conn, cmd)
   

if __name__ == '__main__':
    main()
