"""
Commonly used OIDS module
"""

from pyclass.common import config
from pyclass.common import util

__author__ = "Jason Butler"
__version__ = "0.1a"

def oid_by_name(name=None, oids_yml_file=config.cfg.oids_yml_file):
    """Given an OID name, return the OID string and the oids_dict in a tuple.

    Parameter:: name
    Parameter_type:: string
    Return:: return_val
    Return_type:: tuple (string, dict)

    Prints an error to stdout if 'name' paramter does not match a key
    in oids_dict.
    """

    oids_dict = util.read_data_file(oids_yml_file)

    return_val = oids_dict.get(name)
    if return_val[0] == None:
        print "Error: Parameter value of parameter 'name' did not match a key in oids_dict.  'name' = ", name
        print "  Valid keys in oids_dict:"
        print "  ", oids_dict.keys()
    return return_val

get = oid_by_name
