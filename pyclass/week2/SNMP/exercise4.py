#!/usr/bin/env python

'''
4. SNMP Basics

    a. Create an 'SNMP' directory in your home directory.

$ mkdir SNMP
$ cd SNMP 

    b. Verify that you can import the snmp_helper library.  This is a small library that I created to simplify aspects of PySNMP.

$ python
Python 2.7.5 (default, Feb 11 2014, 07:46:25) 
[GCC 4.8.2 20140120 (Red Hat 4.8.2-13)] on linux2
Type "help", "copyright", "credits" or "license" for more information.
>>> 
>>> import snmp_helper

    c. Create a script that connects to both routers (pynet-rtr1 and pynet-rtr2) and prints out both the MIB2 sysName and sysDescr.
'''

from __future__ import print_function

from snmp_helper import snmp_get_oid
from snmp_helper import snmp_extract

def snmp_get(router, oids):
    data = {}
    for oid_name, oid in oids.items():
        data['router_ip'] = router[0]
        data[oid_name] = snmp_extract(snmp_get_oid(router, oid))
    print(data)
    return data
    
def main():
    routers = []
    oids = {'sysname': '1.3.6.1.2.1.1.5.0',
            'sysdesc': '1.3.6.1.2.1.1.1.0',}
    routers.append(('50.76.53.27', 'galileo', 7961))
    routers.append(('50.76.53.27', 'galileo', 8061))

    for router in routers:
        data = snmp_get(router, oids)
        print()
        print("=====================================")
        for k, v in data.items():
            print("[%s]:\t----\t%s" % (k, v))
            print()
        print()

if __name__ == "__main__":
    main()
