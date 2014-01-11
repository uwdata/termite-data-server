#!/usr/bin/python

import getopt
import glob
import os
import sys

def dict_parser(d):
    print d
    if d.startswith("{"):
        return eval(d)
    else:
        print "Cannot parse dictionary: " + str(d)
        return {}

def list_parser(s):
    global list_separator

    s = s.strip()
    if s != "":
        l = s.split(list_separator)
    else:
        l = []
    return l


def intlist_parser(s):
    global list_separator
    return [int(x) for x in s.split(list_separator)]

def filename_parser(s):
    return os.path.expanduser(s)

def glob_parser(s):
    return glob.glob(s)

def bool_parser(s):
    s = s.lower()
    if s == "true":
        return True
    elif s == "false":
        return False
    else:
        raise "Cannot parse boolean: '" + s + "'"

__flags = []
__post_inits = []

def define_dict(name, default, description):
    global __flags
    __flags.append((name, default, description, dict_parser))

def define_bool(name, default, description):
    global __flags
    __flags.append((name, default, description, bool_parser))

def define_string(name, default, description):
    global __flags
    __flags.append((name, default, description, str))

def define_str(name, default, description):
    global __flags
    __flags.append((name, default, description, str))

def define_int(name, default, description):
    global __flags
    __flags.append((name, default, description, int))

def define_float(name, default, description):
    global __flags
    __flags.append((name, default, description, float))

def define_list(name, default, description):
    global __flags
    __flags.append((name, default, description, list_parser))

def define_intlist(name, default, description):
    global __flags
    __flags.append((name, default, description, intlist_parser))

def define_filename(name, default, description):
    global __flags
    __flags.append((name, default, description, filename_parser))

def define_glob(name, default, description):
    global __flags
    __flags.append((name, default, description, glob_parser))


define_string("list_separator", ",", "String used to separate list item.")

def RunAfterInit(func):
    global __post_inits
    __post_inits.append(func)

def InitFlags():
    global __flags
    this_mod_dict = globals()

    usage = ""
    switches = []
    for f in __flags:
        name = f[0]
        description = f[2]
        default = f[1]
        this_mod_dict[name] = default
        switches.append(name + "=")
        usage += "\t" + name + "\t" + description + " [default = " + str(default) + "]\n"

    try:
        opts, args = getopt.getopt(sys.argv[1:], "", switches)
    except getopt.GetoptError:
        print usage
        sys.exit(2)

    for o, a in opts:
        index = [x for x in __flags if x[0] == o[2:]]
        if len(index) != 1:
            print usage
            sys.exit(2)
        else:
            index = index[0]
            this_mod_dict[index[0]] = index[3](a)

    for func in __post_inits:
        func()

    return args
