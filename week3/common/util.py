import json
import os
import time
import yaml
# import cPickle as pickle
import pickle
from common.Kirk import email_helper
from common.Kirk import snmp_helper

class myDict(dict):
    def __init__(self, *args, **kwargs):
        super(myDict, self).__init__(*args, **kwargs)
    def __getattr__(self, name):
        return self.get(name)
    def __setattr__(self, name, value):
        self[name] = value
    def __delattr__(self, name):
        if name in self:
            del self[name]
    def __getstate__(self):
        return self.__dict__
    def __setstate__(self, d):
        self.__dict__.update(d)
    def __repr__(self):
        return str(dict(self))


def cisco_tics_to_ctime(epoch, uptime, r_c_tics, r_s_tics, s_c_tics):
    total_uptime_seconds = float(uptime) / 100
    running_changed_seconds = float(r_c_tics) / 100
    running_saved_seconds = float(r_s_tics) / 100
    startup_changed_seconds = float(s_c_tics) / 100

    uptime_minutes, uptime_seconds = divmod(total_uptime_seconds, 60)
    uptime_hours, uptime_minutes = divmod(uptime_minutes, 60)
    uptime_days, uptime_hours = divmod(uptime_hours, 24)
    uptime_weeks, uptime_days = divmod(uptime_days, 7)
    uptime_years, uptime_weeks = divmod(uptime_weeks, 52)

    c_uptime = (
        "Y:%d W:%d D:%d H:%d M:%d S:%d" % (
            int(uptime_years),
            int(uptime_weeks),
            int(uptime_days),
            int(uptime_hours),
            int(uptime_minutes),
            int(uptime_seconds)
        )
    )
    epoch = float(epoch)
    scan_time = time.ctime(epoch)
    tus = total_uptime_seconds
    c_boot_time = time.ctime(epoch - tus)
    c_r_c_time = time.ctime(epoch - (tus - running_changed_seconds))
    c_r_s_time = time.ctime(epoch - (tus - running_saved_seconds))
    c_s_c_time = time.ctime(epoch - (tus - startup_changed_seconds))
    time_status_dict = {
        'boot_time': c_boot_time,
        'up_time': c_uptime,
        'running_changed_time': c_r_c_time,
        'running_saved_time': c_r_s_time,
        'startup_changed_time': c_s_c_time,
        'scan_time': scan_time,
    }
    return time_status_dict

    
def get_snmp_data(device_tuple, user_tuple, oid_string):

    v3get = snmp_helper.snmp_get_oid_v3
    nice_data = snmp_helper.snmp_extract

    try:
        snmp_raw_data = v3get(
            device_tuple,
            user_tuple,
            oid_string,
        )
        snmp_data = nice_data(snmp_raw_data)
    except Exception as e:
        print(
            (
                "Could not get SNMP data for:",
                "device->", device_tuple,
                "user->", user_tuple,
                "oid->", oid_string,
                "exception->", e,
            )
        )
    else:
        return snmp_data
    return None


def file_type_from_ext(file_name):
    ext = os.path.splitext(file_name)[1]
    if ext.lower() in ['.yml', '.yaml']:
        data_format = "YAML"
    elif ext.lower() == '.json':
        data_format = "JSON"
    else:
        data_format = "PICKLE"
    return data_format


def write_data_file(file_name, data_dict):
    assert(type(file_name) == type(str()))
    assert(type(data_dict) in [type(dict()), type(myDict())])
   
    data_format = file_type_from_ext(file_name)
    try:
        if data_format == "YAML":
            fp = open(file_name, "w+")
            y_dict = dict(data_dict)
            yaml.safe_dump(y_dict, fp, default_flow_style=False)
        elif data_format == "JSON":
            fp = open(file_name, "w+")
            json.dump(data_dict, fp)
        elif data_format == "PICKLE":
            fp = open(file_name, "wb+")
            pickle.dump(data_dict, fp)
    except Exception as e:
        print "ERROR: Could not open file for writing:", file_name, e
        raise
    else:
        fp.close()


def read_data_file(file_name):
    assert(type(file_name) == type(str()))
   
    data_format = file_type_from_ext(file_name)
    try:
        if data_format == "YAML":
            fp = open(file_name, "r")
            data = myDict(yaml.load(fp))
        elif data_format == "JSON":
            fp = open(file_name, "r")
            data = myDict(json.load(fp))
        elif data_format == "PICKLE":
            fp = open(file_name, "rb")
            data = myDict(pickle.load(fp))
    except Exception as e:
        print(
            "ERROR: Could not read data from file: file=%s, format=%s, "
            "exception=%r" % (file_name, data_format, e)
        )
    else:
        fp.close()
        return data


def get_terminal_size():
    env = os.environ
    def ioctl_GWINSZ(fd):
        try:
            import fcntl, termios, struct
            cr = struct.unpack('hh', fcntl.ioctl(fd, termios.TIOCGWINSZ,
        '1234'))
        except:
            return
        return cr
    cr = ioctl_GWINSZ(0) or ioctl_GWINSZ(1) or ioctl_GWINSZ(2)
    if not cr:
        try:
            fd = os.open(os.ctermid(), os.O_RDONLY)
            cr = ioctl_GWINSZ(fd)
            os.close(fd)
        except:
            pass
    if not cr:
        cr = (env.get('LINES', 25), env.get('COLUMNS', 80))

        ### Use get(key[, default]) instead of a try/catch
        #try:
        #    cr = (env['LINES'], env['COLUMNS'])
        #except:
        #    cr = (25, 80)
    return int(cr[1]), int(cr[0])
