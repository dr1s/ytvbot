#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import os
import sys
import getopt
import logging

from libs.browser import Browser
from libs.scraper import Scraper
from libs.io import *

from selenium.common.exceptions import WebDriverException

email = None
password = None

ytvbot_dir = None
loglevel = logging.DEBUG


def usage():
    print("usage: ytvbot [arguments]")
    print(" -u | --user [email]: email adress of the account")
    print(" -p | --password [password]: password ouf the account ")
    print(" -c | --config-dir [config-dir]: path to configuration directory")
    print(" -o | --output [output_dir]: output directory")
    print(" -h | --help: shows this message")
    print(" -n | --no-download: Don't download anything")
    print(" -l | --links [output_file]: Save links in this file")
    print(" -f | --file [input_file]: File with links to download")
    print(" -# | --progress: show progress bar when downloading files")

def setup_dir():

    global ytvbot_dir

    if not ytvbot_dir:
        home = os.path.expanduser("~")
        ytvbot_dir = os.path.join(home, '.ytvbot')

    if not os.path.isdir(ytvbot_dir):
        os.mkdir(ytvbot_dir)

    cache_file = os.path.join(ytvbot_dir, 'cache')
    if not os.path.exists(cache_file):
        with open(cache_file, 'a'):
            os.utime(cache_filen, None)

def main():

    output_dir = None
    link_output = None
    download_links_file = None
    download_files = True
    progress_bar = False

    try:
        long = ["help", "output=", "links=", "file=", "user=",
                "password=", "config-dir=", "no-download", "progress"]
        opts, args = getopt.getopt(sys.argv[1:], "hno:l:f:u:p:c:#", long )
    except getopt.GetoptError as err:
        print str(err)
        usage()
        sys.exit(2)
    for o, a in opts:
        if o in ("-h", "--help"):
            usage()
            sys.exit()
        elif o in ("-o", "--output"):
            output_dir = os.path.abspath(a)
        elif o in ("-l", "--links"):
            link_output = os.path.abspath(a)
        elif o in ("-f", "--file"):
            download_links_file = os.path.abspath(a)
        elif o in ("-n", "--no-download"):
            download_files = False
        elif o in ("-u", "--user"):
            global email
            email = a
        elif o in ("-p", "--password"):
            global password
            password = a
        elif o in ("-c", "--config-dir"):
            global ytvbot_dir
            ytvbot_dir = a
        elif o in ("-#", "--progress"):
            progress_bar = True
        else:
            assert False, "unhandled option"

    setup_dir()
    download_links = None
    recording_links = []
    browsers = None

    if not download_links_file:

        br = Browser(config_dir=ytvbot_dir, loglevel=loglevel)
        try:
            br.login(email, password)
            scraper = Scraper(br.browser, loglevel=loglevel)
            download_links = scraper.get_all_download_links()
            br.destroy()
        except KeyboardInterrupt or WebDriverException:
            if br:
                br.destroy()
    else:
        with open(download_links_file) as f:
            download_links = f.readlines()
        download_links = [x.strip() for x in download_links]

    cache_file = os.path.join(ytvbot_dir, 'cache')

    write_links_to_file(download_links, cache_file)

    if link_output and not download_links_file:
        write_links_to_file(download_links, link_output)

    if download_files:
        download(download_links, output_dir, progress_bar=progress_bar)


logger = logging.getLogger('ytvbot')
logger.setLevel(loglevel)
ch = logging.StreamHandler()
ch.setLevel(loglevel)
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

if __name__ == "__main__":
    main()
