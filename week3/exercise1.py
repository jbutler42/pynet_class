#!/usr/bin/env python

from common import config
from common.entities import entities
from common import oids
from common.util import cisco_tics_to_ctime
from common.util import get_snmp_data
from common.util import myDict
from common.util import read_data_file
from common.util import write_data_file
import time


def my_oids():
    oids_dict = {
        'running_last_changed': oids.get('ccmHistoryRunningLastChanged'),
        'running_last_saved': oids.get('ccmHistoryRunningLastSaved'),
        'startup_last_changed': oids.get('ccmHistoryStartupLastChanged'),
        'uptime': oids.get('sysUptime'),
    }
    return myDict(oids_dict)


def my_data_files():
    data_folder = config.cfg.data_file_folder
    data_files = ['last_changed.p', 'last_changed.json', 'last_changed.yml']
    full_file_paths = []
    for data_file in data_files:
        file_name = '/'.join([data_folder, data_file]) 
        full_file_paths.append(file_name)
    return full_file_paths


def is_equal_dicts(data_dict):
    d_list = []
    for data in data_dict.itervalues():
        d_list.append(data)

    if d_list.count(d_list[0]) == len(d_list):
        return True
    else:
        return False


def my_get_snmp_data(device_tuple, user_tuple, oids_dict):
    snmp_data_dict = myDict()
    snmp_data_dict['epoch'] = time.time()
    for oid_alias, oid_string in oids_dict.items():
        snmp_data_dict[oid_alias] = get_snmp_data(
            tuple(device_tuple),
            tuple(user_tuple),
            oid_string
        )
    return snmp_data_dict


def get_file_data(file_name):
    file_data_dict = read_data_file(file_name)
    return file_data_dict


def write_data(file_name, data):
    write_data_file(file_name, data)


def setup():
    setup_args = myDict()
    setup_args.devices = entities.devices
    setup_args.user_tuple = entities.users.user1
    setup_args.oids_dict = my_oids()
    setup_args.data_files = my_data_files()
    setup_args.file_data_dict = myDict()
    return setup_args
    

def main(args):

    # Load saved device data if any, from all indicated data files.
    # There are multiple data files just to illustrate the use of 
    # various data formats (JSON, YAML, PICKLE).
    # Make sure the data structure is the same in each data file.
    saved_data = myDict()
    saved_devices = myDict()
    for file_name in args.data_files:
        saved_data[file_name] = get_file_data(file_name)
    if is_equal_dicts(saved_data):
        if saved_data[file_name] != None:
            saved_devices = saved_data[file_name]
        print "DEBUG:", saved_devices
    else:
        print "ERROR: Data in data files differs!", args.data_files
        raise BaseException
        
    # get snmp data from each device for each oid
    snmp_data = myDict()
    for dev_name, device_tuple in args.devices.iteritems():
        snmp_data[dev_name] = my_get_snmp_data(
            device_tuple,
            args.user_tuple,
            args.oids_dict
        )

        print dev_name, snmp_data[dev_name]

    # compare SNMP data with saved data
    changed_devices_list = []
    for dev_name in list([x for x in snmp_data if x in saved_devices]):
        saved = saved_devices[dev_name]
        snmp = snmp_data[dev_name]
        epoch = snmp.epoch
        uptime = snmp.uptime
        running_changed = snmp.running_last_changed
        running_saved = snmp.running_last_saved
        startup_changed = snmp.startup_last_changed
        time_info = cisco_tics_to_ctime(
            epoch,
            uptime,
            running_changed,
            running_saved,
            startup_changed
        )
        if (
            snmp.uptime > saved.uptime or
            snmp.running_last_changed < saved.running_last_changed
        ):
            if snmp.running_last_changed <= config.cfg.reload_max_last_changed:
                print "Device was reloaded but config was not changed:", dev_name
            else:
                print "Device was reloaded and running config changed:", dev_name
                changed_device_list.append(
                    {'name': dev_name, 'time_info': time_info}
                )
        elif snmp.running_last_changed == saved.running_last_changed:
            print "Device config not changed:", dev_name
        elif snmp.running_last_changed > saved.running_last_changed:
            print "Device config changed:", dev_name        
            changed_device_list.append(
                {'name': dev_name, 'time_info': time_info}
            )
        else:
            print "ERROR: What?!?!"
            raise ValueError()
                
    # determine changed device data to save in data file(s)
    write_devices_dict = myDict()
    for changed_device_dict in changed_devices_list:
        dev_name = changed_device_dict.name
        write_devices_dict[dev_name] = snmp_data[dev_name]

    # determine non existent files(s) to save device data
    for dev_name in list([x for x in snmp_data if x not in saved_devices]):
        write_devices_dict[dev_name] = snmp_data[dev_name]

    # write data if any to file(s)
    if write_devices_dict != myDict():
        for file_name in args.data_files:
            write_data(file_name, write_devices_dict)
   
    # notify about devices with changed running configs 
        
        
if __name__ == "__main__":
    args = setup()
    while True:
        main(args)
    
