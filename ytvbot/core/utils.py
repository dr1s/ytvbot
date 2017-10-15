# -*- coding: utf-8 -*-
import os
import codecs

def check_dir(directory):
    if not os.path.isdir(directory):
        os.mkdir(directory)


def setup_config_dir(ytvbot_dir):

    if not ytvbot_dir:
        home = os.path.expanduser("~")
        ytvbot_dir = os.path.join(home, '.ytvbot')

    check_dir(ytvbot_dir)

    cache_file = os.path.join(ytvbot_dir, 'cache')
    if not os.path.exists(cache_file):
        with codecs.open(cache_file, 'a', 'utf-8'):
            os.utime(cache_file, None)
    return ytvbot_dir
