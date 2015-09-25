#!/usr/bin/env python

'''This program is step 7 of class 1 of the PytNet course

7. Write a Python program that reads both the YAML file and the JSON file
created in exercise6 and pretty prints the data structure that is
returned.
'''

from step6 import pretty_print_list

if __name__ == '__main__':
    pretty_print_list('var/yaml_file.yml', 'YAML')
    pretty_print_list('var/json_file.json', 'JSON')
