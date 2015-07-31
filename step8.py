#!/usr/bin/env python

'''This program is step 8, 9 and 10 of class 1 of the PytNet course

ciscoconfparse
8. Write a Python program using ciscoconfparse that parses this config file.
Note, this config file is not fully valid (i.e. parts of the configuration are
missing). The script should find all of the crypto map entries in the file
(lines that begin with 'crypto map CRYPTO') and for each crypto map entry print
out its children.

9. Find all of the crypto map entries that are using PFS group2

10. Using ciscoconfparse find the crypto maps that are not using AES (based-on 
the transform set name). Print these entries and their corresponding transform
set name.
'''

from ciscoconfparse import CiscoConfParse

with open("var/step8.cfg", "r") as f:
    conf = CiscoConfParse(f)

print ">> crypto objects with 'crypto map CRYPTO':"
objects = conf.find_objects(r'crypto map CRYPTO')
for object in objects:
    children = object.children
    text = object.text
    print "=========================="
    print text,
    print "=========================="
    for child in children:
        print "    %s" % child.text,
    print

print ">> crypto objects with 'pfs group2' children:"
group2_objects = conf.find_objects_w_child(r'crypto map CRYPTO', r'set pfs group2')
for group2_object in group2_objects:
    print "=========================="
    print group2_object.text,
    print "=========================="
print

print ">> objects with no children using AES:"
print "=========================="
non_aes_objects = conf.find_objects_wo_child(r'crypto map CRYPTO', r'transform-set AES')
for non_aes_object in non_aes_objects:
    children = non_aes_object.children
    for child in children:
        if 'transform-set' in child.text:
            # child = non_aes_object.re_search_children(r'transform-set')
            print non_aes_object.text, child.text,
print "=========================="
print



