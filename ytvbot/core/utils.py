# -*- coding: utf-8 -*-
import os
import codecs


def check_dir(directory):
    if not os.path.isdir(directory):
        os.mkdir(directory)


def setup_config_dir(config_dir):

    if not config_dir:
        home = os.path.expanduser("~")
        config_dir = os.path.join(home, '.ytvbot')

    check_dir(config_dir)

    cache_file = os.path.join(config_dir, 'cache')
    if not os.path.exists(cache_file):
        with codecs.open(cache_file, 'a', 'utf-8'):
            os.utime(cache_file, None)
    return config_dir
