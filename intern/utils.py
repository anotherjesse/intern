#   Copyright 2010-2011 Josh Kearney
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

"""Intern Utility Library"""

from __future__ import with_statement

import logging
import logging.handlers
import os
import re
import sys

import config



def logger(name, debug=False):
    """Log handler"""
    log_dir = get_directory("logs")
    level = logging.DEBUG if debug else logging.INFO
    format = "%(asctime)s [%(name)s] %(message)s"
    datefmt = "%H:%M:%S"

    logging.basicConfig(level=level, format=format, datefmt=datefmt)

    log = logging.handlers.TimedRotatingFileHandler("%s/%s.log" % (log_dir,
            name.lower()), "midnight")
    log.setLevel(level)
    formatter = logging.Formatter(format, datefmt)
    log.setFormatter(formatter)
    logging.getLogger(name).addHandler(log)

    return logging.getLogger(name)


def admin(func):
    """Administration Decorator"""
    def f(self, *args, **kwargs):
        if self.irc.source in self.irc.admins:
            func(self, *args, **kwargs)
        else:
            self.irc.reply("Sorry, you are not authorized to do that.")
    f.__doc__ = func.__doc__
    f.__name__ = func.__name__
    f.__module__ = func.__module__
    return f


def ensure_int(param):
    """Ensure the given param is an int"""
    try:
        param = re.sub("\W", "", param)
        return int(param)
    except ValueError:
        return None


def load_config(section, conf):
    """Load a config section"""
    return config.Config(conf, section)


def get_home_directory():
    """Return the home directory"""
    home_dir = os.getenv("HOME") + "/.intern/"
    if not os.path.exists(home_dir):
        os.makedirs(home_dir)

    return home_dir


def get_directory(new_dir):
    """Return a directory"""
    home_dir = get_home_directory()
    new_dir = home_dir + new_dir

    if not os.path.exists(new_dir):
        os.makedirs(new_dir)

    return new_dir + "/"


def write_file(dir, file, data):
    """Write data to file"""
    dir = get_directory(dir)

    with open(dir + file, "w") as f:
        f.write(str(data).strip())
    f.closed


def read_file(dir, file):
    """Read and return the data in file"""
    dir = get_directory(dir)

    try:
        with open(dir + file, "r") as f:
            data = f.read()
        f.closed

        return data
    except IOError:
        return None


def generate_config():
    """Generate an example config"""
    example = """# Global Configuration

[cloud]
auth_endpoint: http://localhost:5000/v2.0/

[user]
user: demo
tenant: demo
password: secrete

[admin]
user: admin
tenant: admin
password: secrete

"""

    conf_file = get_home_directory() + "intern.conf"

    if os.path.exists(conf_file):
        return

    print "Generating..."
    with open(conf_file, "w") as f:
        f.write(example)
    f.closed
    print "Done"
