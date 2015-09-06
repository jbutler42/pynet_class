"""
Commonly used OIDS module
"""

__author__ = "Jason Butler"
__version__ = "0.1a"

def oid_by_name(name=None):
    """Given an OID name, return the OID string and the oids_dict in a tuple.

    Parameter:: name
    Parameter_type:: string
    Return:: return_val
    Return_type:: tuple (string, dict)

    Prints an error to stdout if 'name' paramter does not match a key
    in oids_dict.
    """

    oids_dict = {
        'ifDescr': '1.3.6.1.2.1.2.2.1.2',
        'ifInOctets': '1.3.6.1.2.1.2.2.1.10.5',
        'ifInUcastPkts': '1.3.6.1.2.1.2.2.1.11.5',
        'ifOutOctets': '1.3.6.1.2.1.2.2.1.16.5',
        'ifOutUcastPkts': '1.3.6.1.2.1.2.2.1.17.5',
    }
    return_val = (oids_dict.get(name), oids_dict)
    if return_val[0] == None:
        print "Error: Parameter value of parameter 'name' did not match a key in oids_dict.  'name' = ", name
        print "  Valid keys in oids_dict:"
        print "  ", oids_dict.keys()
    return return_val
