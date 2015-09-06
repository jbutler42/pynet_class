#!/usr/bin/env python

from common import config
from common import entities
from common import oids
from common import util
from common.Kirk import email_helper
from common.Kirk import snmp_helper


def my_oids():
    oids_tuple = (
        ('running_last_changed', oids.get('ccmHistoryRunningLastChanged')),
        ('running_last_saved', oids.get('ccmHistoryRunningLastSaved')),
        ('startup_last_changed', oids.get('ccmHistoryStartupLastChanged')),
        ('uptime', oids.get('sysUptime')),
    )
    return oids_tuple


def my_data_files():
    data_folder = config.cfg.data_file_folder
    data_files = ['last_changed.p', 'last_changed.json', 'last_changed.yml']
    full_file_paths = []
    for data_file in data_files:
        file_name = '/'.join([data_folder, data_file]) 
        full_file_paths.append(file_name)
    return full_file_paths


def my_snmp_data(devices, user_tuple, oids_tuple):
    snmp_data_dict = {}
    for oid_tuple in oids_tuple:
        (key, oid_string) = oid_tuple
        snmp_data_dict[key] = util.get_snmp_data(
            device_tuple,
            user_tuple,
            oid_string
        )
    return snmp_data_dict


def setup():
    devices = entities.entities.get('devices')
    user_tuple = entities.entities.get('users')[0]
    oids_tuple = my_oids()
    data_files = my_data_files()
    return (devices, user_tuple, oids_tuple, data_files)
    

def main(devices, user_tuple, oids_tuple, data_files):
   
    for dev_name, device_tuple in devices.iteritems():
        saved_val = file_data_dict.get(dev_name).get(key)
        snmp_val = snmp_data_dict.get(key)
    for file_name in data_files:
        file_data_dict = util.read_change_times_data(file_name)
        if 
            


if __name__ == "__main__":
    (devices, user, oids_tuple, data_files) = setup()
    while True:
        main(devices, user, oids_tuple, data_files)
    
