""" String utilities for use with compiler. """

import re

def is_an_identifier(name):
    """ Return True if name conforms to rules of an identifier. """
    return(re.search(r"^([A-Z]|_)\w*$", name)) 

def str_is_numeric(s):
    """ Return True if string looks like a decimal. """
    return(re.search(r"^\d+$", s))

def str_is_hex_numeric(s):
    """ Return True if string looks like a hexadecimal. """
    return(re.search(r"^\$([A-F]|\d)+$", s))
