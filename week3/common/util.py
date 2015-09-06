import json
import os
import yaml
import cPickle as pickle
from common.Kirk import email_helper
from common.Kirk import snmp_helper


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
                "user->", user_typle,
                "oid->", oid_string,
                "exception->", e,
            )
        )
    else:
        return snmp_data
    return None


def load_yaml_from_file(file_name=None):
    assert(file_name != None), ("ERROR: file_name must be a string file name:", file_name)
    assert(type(file_name) == type(str())), ("ERROR: file_name must be a string file name:", file_name)
    
    try:
        with open(file_name, "r") as fp:
            data = yaml.load(fp)
    except Exception as e:
        print "ERROR: Could not load YAML from file:", e
        raise
    else:
        return data


def write_change_times_data(file_name, data_dict):
    assert(type(file_name) == type(str())
    assert(type(data_dict) == type(dict())
   
    data_format = file_type_from_ext(file_name)
    fp = open(file_name, "w")
    
    if data_format == "YAML":
        yaml.dump(data_dict, fp, default_flow_style=False)
    elif data_format == "JSON":
        json.dump(data_dict, fp)
    elif data_format == "PICKLE":
        pickle.dump(data_dict, fp)
    
    fp.close() 


def read_change_times_data(file_name):
    assert(type(file_name) == type(str())
   
    data_format = file_type_from_ext(file_name)
    fp = open(file_name, "r")
    
    if data_format == "YAML":
        data = yaml.load(fp)
    elif data_format == "JSON":
        data = json.load(fp)
    elif data_format == "PICKLE":
        data = pickle.load(fp)
    
    fp.close()
    return data

    
def file_type_from_ext(file_name):
    ext = os.path.splitext(file_name)[1]
    if ext.lower() in ['yml', 'yaml']:
        data_format = "YAML"
    elif ext.lower() == 'json':
        data_format = "JSON"
    else:
        data_format = "PICKLE"
    return data_format
