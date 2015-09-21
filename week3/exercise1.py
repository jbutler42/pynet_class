#!/usr/bin/env python

from common import config
from common.entities import entities
from common import oids
from common.prettytable import PrettyTable
from common.util import cisco_tics_to_ctime
from common.util import send_email
from common.util import get_snmp_data
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
        if saved_data[file_name] is not None:
            saved_devices = saved_data[file_name]
    else:
        print (
            "ERROR: Data in data files differs! Deleting data files.",
            args.data_files
        )
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
    devices_dict = {}
    for dev_name in list([x for x in snmp_data if x in saved_devices]):
        saved = saved_devices[dev_name]
        snmp = snmp_data[dev_name]

        # logic to detect running config changes and reloads
        change_detected = False
        reload_detected = False
        status_msg = ""
        if (
            snmp['uptime'] < saved['uptime'] or
            snmp['running_last_changed'] < saved['running_last_changed']
        ):
            reload_detected = True
            if (
                snmp['running_last_changed'] <=
                config.cfg.reload_max_last_changed
            ):
                status_msg = (
                    dev_name, "was RELOADED, running config NOT CHANGED."
                )
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
        devices_dict.update(
            {
                dev_name: {
                    'Status Message': status_msg,
                    'Change Detected': change_detected,
                    'Reload Detected': reload_detected,
                    'old': cisco_tics_to_ctime(
                        saved['epoch'],
                        saved['uptime'],
                        saved['running_last_changed'],
                        saved['running_last_saved'],
                        saved['startup_last_changed']
                    ),
                    'new': cisco_tics_to_ctime(
                        snmp['epoch'],
                        snmp['uptime'],
                        snmp['running_last_changed'],
                        snmp['running_last_saved'],
                        snmp['startup_last_changed']
                    ),
                },
            },
        )

    # save all device data to file(s)
    for file_name in args.data_files:
        write_data(file_name, snmp_data)

    # report on detected device info
    report_name = "Cisco Device Configuration Change Detection Report"
    report_time = time.ctime(time.time())
    device_count = len(devices_dict)
    reload_count = 0
    change_count = 0
    unchange_count = 0
    tables = {}
    data_rows = {}
    tables['header_table'] = PrettyTable(
        [
            'Report Name',
            'Time of Report'
        ]
    )
    tables['header_table'].add_row([report_name, report_time])
    tables['summary_table'] = PrettyTable(
        [
            'Total Device Count',
            'Total Changed Device Count',
            'Total Reloaded Device Count',
            'Total Unchanged Device Count',
        ]
    )
    data_table_cols = [
        'Device Name',
        'Attribute',
        'Current Value',
        'Previous Value',
    ]
    states = ['changed', 'unchanged']
    for state in states:
        tables[state] = PrettyTable(data_table_cols)
        tables[state].align = 'r'
        data_rows[state] = []
    yes = 'YES'
    no = 'NO'
    na = 'N/A (not saved)'
    time_cols = [
        'Scan Time',
        'Up Time',
        'Boot Time',
        'Startup Config Changed Time',
        'Running Config Saved Time',
        'Running Config Changed Time'
    ]
    for dev_name in devices_dict.iterkeys():
        dev = devices_dict[dev_name]
        dev_old = dev['old']
        dev_new = dev['new']

        if dev['Reload Detected'] and dev['Change Detected']:
            reload_count += 1
            change_count += 1
            cd = rd = yes
            state = 'changed'
        elif dev['Reload Detected']:
            reload_count += 1
            cd = no
            rd = yes
            state = 'unchanged'
        elif dev['Change Detected']:
            change_count += 1
            cd = yes
            rd = no
            state = 'changed'
        else:
            cd = no
            rd = no
            state = 'unchanged'

        data_rows[state].extend(
            [
                [
                    dev_name,
                    'Change Detected',
                    cd,
                    na
                ],
                [
                    dev_name,
                    'Reload Detected',
                    rd,
                    na
                ],
                [
                    dev_name,
                    'Status Message',
                    dev['Status Message'],
                    na
                ],
            ]
        )
        for time_col in time_cols:
            data_rows[state].append(
                [
                    dev_name,
                    time_col,
                    dev_new[time_col],
                    dev_old[time_col]
                ],
            )
    unchange_count = device_count - change_count
    tables['summary_table'].add_row(
        [
            device_count,
            change_count,
            reload_count,
            unchange_count,
        ]
    )
    for state in states:
        for data_row in data_rows[state]:
            tables[state].add_row(data_row)

    ordered_tables = [
        ('header_table', '>>> Report Header <<<'),
        ('summary_table', '>>> Report Summary <<<'),
        ('changed', '>>> %d *Changed* Devices <<<' % change_count),
        ('unchanged', '>>> %d *UnChanged* Devices <<<' % unchange_count),
    ]
    output = ""
    for table_tuple in ordered_tables:
        table = table_tuple[0]
        msg = table_tuple[1]
        if table == 'changed' and change_count == 0:
            continue
        elif table == 'unchanged' and unchange_count == 0:
            continue
        else:
            output = output + msg + str(tables[table]) + '\n'

    # print to screen
    print output
    # send email if email_enable == True
    if cfg.email.get('email_enabled'):
        m_from = config.cfg.email.get('from')
        m_to = config.cfg.email.get('to')
        subject = "Detected Device Config Change"
        send_mail(m_from, m_to, subject, output)

    
if __name__ == "__main__":
    args = setup()
    while True:
        main(args)
        time.sleep(config.cfg.loop_pause_seconds)
