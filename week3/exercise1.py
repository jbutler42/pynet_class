#!/usr/bin/env python

from common import config
from common.entities import entities
from common import oids
from common.util import cisco_tics_to_ctime
from common.util import get_snmp_data
from common.util import get_terminal_size
from common.util import myDict
from common.util import read_data_file
from common.util import write_data_file
import os
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


def get_max_length(list_of_lists):
    max_length = 0
    for this_list in list_of_lists:
        this_max_length = max([len(x) for x in this_list])
        max_length = max(max_length, this_max_length)
    return max_length 


def my_get_snmp_data(device_tuple, user_tuple, oids_dict):
    snmp_data_dict = myDict()
    snmp_data_dict['epoch'] = str(time.time())
    for oid_alias, oid_string in oids_dict.items():
        snmp_data_dict[oid_alias] = get_snmp_data(
            tuple(device_tuple),
            tuple(user_tuple),
            oid_string
        )
    return dict(snmp_data_dict)


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
    else:
        print "ERROR: Data in data files differs! Deleting data files.", args.data_files
        for file_name in args.data_files:
            if os.path.exists(file_name):
                os.remove(file_name)
        raise BaseException
        
    # get snmp data from each device for each oid
    snmp_data = myDict()
    for dev_name, device_tuple in args.devices.iteritems():
        snmp_data[dev_name] = my_get_snmp_data(
            device_tuple,
            args.user_tuple,
            args.oids_dict
        )


    # compare SNMP data with saved data
    devices_list = []
    for dev_name in list([x for x in snmp_data if x in saved_devices]):
        saved = saved_devices[dev_name]
        snmp = snmp_data[dev_name]
        epoch = snmp['epoch']
        uptime = snmp['uptime']
        running_changed = snmp['running_last_changed']
        running_saved = snmp['running_last_saved']
        startup_changed = snmp['startup_last_changed']

        # compile previous time info with current time info
        old_and_new_data = {'old': saved, 'new': snmp}
        time_info = {}
        for temporal_state, data in old_and_new_data.iteritems():
            time_info[temporal_state] = cisco_tics_to_ctime(
                data['epoch'],
                data['uptime'],
                data['running_last_changed'],
                data['running_last_saved'],
                data['startup_last_changed'],
            )

        # logic to detect running config changes and reloads
        change_detected = False
        reload_detected = False
        status_msg = ""
        if (
            snmp['uptime'] < saved['uptime'] or
            snmp['running_last_changed'] < saved['running_last_changed']
        ):
            reload_detected = True
            if snmp['running_last_changed'] <= config.cfg.reload_max_last_changed:
                status_msg = dev_name, "was RELOADED, running config NOT CHANGED."
                change_detected = False
            else:
                status_msg = dev_name, "was RELOADED, running config CHANGED."
                change_detected = True
        elif snmp['running_last_changed'] == saved['running_last_changed']:
            status_msg = dev_name, "running config NOT CHANGED."
            change_detected = False
        elif snmp['running_last_changed'] > saved['running_last_changed']:
            status_msg = dev_name, "running config CHANGED."
            change_detected = True
        else:
            print "ERROR: What?!?!"
            raise ValueError()

        # device info for report and notifications
        devices_list.append(
            {
                'name': dev_name,
                'time_info': time_info,
                'status_msg': status_msg,
                'change_detected': change_detected,
                'reload_detected': reload_detected,
            }
        )

    # save all device data to file(s)
    for file_name in args.data_files:
        write_data(file_name, snmp_data)

    # report on findings
    # device columns to use in report
    d_cols = [
        'name',
        'change_detected',
        'reload_detected',
        'status_msg',
    ]
    # time columns in desired order
    time_columns = [
        'scan_time',
        'boot_time',
        'up_time',
        'running_changed_time',
        'running_saved_time',
        'startup_changed_time',
    ]
    # find max widths for formatting
    # max time column width
    m_t_c_w = max([len(x) for x in time_columns])
    # max device column width
    m_d_c_w = max([len(x) for x in d_cols])
    # max time value width
    m_t_v_w = {}
    for temporal in ['old', 'new']:
        m_t_v_w[temporal] = get_max_length(
            [x['time_info'][temporal] for x in devices_list]
        )

    line_break = "-"*79
    report_header = []
    report_content = {
        'changed': [
            '\n',
            line_break,
            'Changed Device List',
            line_break,
            '\n',
        ],
        'unchanged': [
            '\n',
            line_break,
            'Unchanged Device List',
            line_break,
            '\n',
        ]
    }
    report_time = time.ctime(time.time())
    device_count = len(devices_list)
    reload_count = 0
    change_count = 0
    for device in devices_list:
        if device['reload_detected']:
            reload_count += 1
        if device['change_detected']:
            change_count += 1
            device_state = 'changed'        
        else:
            device_state = 'unchanged'        
      
        # device info
        report_content[device_state].append(line_break)
        for d_col in d_cols:
            report_content[device_state].append(
                "|{:>{}}: {}|".format(
                    d_col, m_d_c_w,
                    device[d_col]
                )
            ) 
        report_content[device_state].append(line_break)
        # time info dict
        t_i_d = device['time_info']
        for time_column in time_columns:
            report_content[device_state].append(
                "|{:>{}}: {:<{}} | {:<{}}|".format(
                    time_column, m_t_c_w,
                    t_i_d['new'][time_column], m_t_v_w['new'],
                    t_i_d['old'][time_column], m_t_v_w['old']
                )
            )
        report_content[device_state].append(line_break)
    report_header.append(line_break)
    report_header.append(line_break)
    report_header.append("Cisco Device Configuration Change Detection Report")
    report_header.append(line_break)
    report_header.append(line_break)
    report_header.append("Report Generated: %s" % report_time)
    report_header.append("Total Device Count: %d" % device_count)
    report_header.append("Running Configuration Change Device Count: %d" % change_count)
    report_header.append("Reloaded Device Count: %d" % reload_count)
    report_header.append(line_break)
    report_header.append(line_break)

    try:
        (width, height) = get_terminal_size()
    except Exception as e:
        width = 100

    for line in report_header:
        print "{:^{}}".format(line, width)
    for state in ['changed', 'unchanged']:
        if state == 'changed' and change_count == 0:
            continue
        elif state == 'unchanged' and change_count == len(devices_list):
            continue
        for line in report_content[state]:
            print "{:^{}}".format(line, width)
                    
            

    
        
if __name__ == "__main__":
    args = setup()
    while True:
        main(args)
        time.sleep(config.cfg.loop_pause_seconds)
    
