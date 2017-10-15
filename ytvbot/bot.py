#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import os
import sys
import getopt
import json
import codecs

from core.scraping.browser import Browser
from core.scraping.scraper import Scraper
from core.importer import import_json_file
from core.scraping.exporter import write_links_to_file, print_recordings
from core.log import add_logger
from core import fileDownloader
from core.dlmgr import Manager
from core.utils import check_dir, setup_config_dir
from selenium.common.exceptions import WebDriverException
from urllib2 import HTTPError


email = None
password = None

search = None


def usage():
    print("usage: ytvbot [arguments]")
    print(" -u | --user [email]: email adress of the account")
    print(" -p | --password [password]: password ouf the account ")
    print(" -c | --config-dir [config-dir]: path to configuration directory")
    print(" -o | --output [output_dir]: output directory")
    print(" -h | --help: shows this message")
    print(" -n | --no-download: Don't download anything")
    print(" -l | --links [output_file]: Save links in this file")
    print(" -# | --progress: show progress bar when downloading files")
    print(" -s | --search [show_name]: only look for show_name")
    print(" -j | --json [output_file]: save results as json file")
    print(" -z | --network [network_name]: show results for network")



def get_recordings(conf_dir, search=None, network=None):
    recordings = []
    br = Browser(config_dir=conf_dir)
    try:
        br.login(email, password)
        scraper = Scraper(br.browser)
        recordings = scraper.get_recordings(search, network)
        br.destroy()
    except (KeyboardInterrupt, WebDriverException):
        if br:
            br.destroy()
    return recordings


def main():

    output_dir = None
    link_output = None
    download_files = True
    progress_bar = False
    json_file = None
    network = None
    ytvbot_dir = None

    try:
        long_opts = ["help", "output=", "links=", "user=", "password=",
                "config-dir=", "no-download", "progress", "search=",
                "json=", "network="]

        opts, args = getopt.getopt(sys.argv[1:], "hno:l:u:p:c:#s:j:z:",
            long_opts )
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
        elif o in ("-n", "--no-download"):
            download_files = False
        elif o in ("-u", "--user"):
            global email
            email = a
        elif o in ("-p", "--password"):
            global password
            password = a
        elif o in ("-c", "--config-dir"):
            ytvbot_dir = a
        elif o in ("-#", "--progress"):
            progress_bar = True
        elif o in ("-s", "--search"):
            global search
            search = a
        elif o in ("-j", "--json"):
            json_file = os.path.abspath(a)
        elif o in ("-z","--network"):
            network = a
        else:
            assert False, "unhandled option"

    ytvbot_dir = setup_config_dir(ytvbot_dir)

    if not json_file or (json_file and not os.path.exists(json_file)):
        recordings = get_recordings(ytvbot_dir, search, network)

    if json_file:
        if os.path.isfile(json_file):
            logger.debug('Importig json file: %s' % json_file)
            recordings = import_json_file(json_file)
        else:
            logger.debug("Writing json file to: %s" % link_output)
            recordings_list = []
            for recording in recordings:
                rec_dict = recording.dict()
                recordings_list.append(rec_dict)
            with codecs.open(json_file, 'w', 'utf-8') as f:
                f.write(json.dumps(recordings_list, f, indent=2,
                    sort_keys=True, ensure_ascii=False))

    if recordings:
        print_recordings(recordings, ['id', 'show_name', 'title',
                'date', 'start_time', 'end_time', 'network'])
    else:
        logger.debug('No recordings found to print')

    if link_output:
        with codecs.open(link_output, 'w', 'utf-8'):
            os.utime(link_output, None)
        write_links_to_file(recordings, link_output)

    if download_files and recordings:
        logger.info("Start download recordings")
        mgr = Manager(output_dir, recordings)
        mgr.start()

logger = add_logger('ytvbot')

if __name__ == "__main__":
    main()
