#!/usr/bin/env python

'''This program is step 6 of class 1 of the PytNet course

YAML/JSON
6. Write a Python program that creates a list. One of the elements of the list
should be a dictionary with at least two keys. Write this list out to a file 
using both YAML and JSON data_formats. The YAML file should be in the expanded
form.
'''

from json import dump as jdump
from json import dumps as jdumps
from json import load as jload
from pprint import pprint as pp
from yaml import dump as ydump
from yaml import load as yload


def pretty_print_list(file_name=None, data_format="JSON"):
    # print YAML or JSON representations of list data
    assert(file_name is not None), "Provide a file name"
    assert((data_format == "JSON" or data_format == "YAML")), ("Format must be 'JSON'"
                                                     " or 'YAML'")

    try:
        formatted_list = []
        with open(file_name, "r") as f:
            if data_format == "JSON":
                some_list = jload(f)
                formatted_list = jdumps(some_list)
            elif data_format == "YAML":
                some_list = yload(f)
                formatted_list = ydump(some_list,
                                       default_flow_style=False,
                                       explicit_start=True,
                                       width=1,
                                       indent=2)
    except IOError as e:
        print "Could not read file: %s" % e
    except Exception as e:
        print "Unexpected exception: %s" % e
 
    print "======================"
    print "list from file: %s in %s data_format:" % (file_name, data_format)
    print "======================"
    print formatted_list
    print "======================"
    print "list from file: %s in pretty_print native python" % file_name
    print "======================"
    pp(some_list, width=1)

def write_list(some_list=[]):
    # write list to a file using YAML
        try:
            with open("var/yaml_file.yml", "w") as f:
	            f.write(ydump(
	                some_list,
	                default_flow_style=False,
	                explicit_start=True,
	                width=1,
	                indent=2))
        except IOError as e:
            print "Could not write to file: %s" % e

    # write list to a file using JSON
        try:
            with open("var/json_file.json", "w") as f:
                jdump(some_list, f)
        except IOError as e:
            print "Could not write to file: %s" % e

if __name__ == '__main__':
    # make a list of data
    some_list = range(10)
    some_list.append({'key1': [0, 1, 2, 3], 'key2': 'some_value_for_key2'})
    # write data files
    write_list(some_list)
    
