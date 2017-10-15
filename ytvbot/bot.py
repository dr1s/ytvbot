#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import os
import json
import codecs
import argparse

from core.scraping.browser import Browser
from core.scraping.scraper import Scraper
from core.importer import import_json_file
from core.scraping.exporter import write_links_to_file, print_recordings
from core.log import add_logger
from core.dlmgr import Manager
from core.utils import setup_config_dir
from selenium.common.exceptions import WebDriverException


email = None
password = None

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

    parser = argparse.ArgumentParser(
        description='Download recordings from ytv')

    parser.add_argument('-u', '--user',
        help='email address', default=None)
    parser.add_argument('-p', '--password',
        help='passord', default=None)
    parser.add_argument('-c', '--configdir',
        help='path to configuration directory', default=None)
    parser.add_argument('-o', '--output',
        help='path to output directory', default=None)
    parser.add_argument('-n', '--nodownload',
        help='Don\'t download anything', action='store_false',
        default=True)
    parser.add_argument('-l', '--links',
        help='save links in this file', default=None)
    parser.add_argument('-#', '--progress',
        help='show progress bar when downloading files',
        action='store_true', default=False)
    parser.add_argument('-s', '--search',
        help='search for show name', default=None)
    parser.add_argument('-j', '--json',
        help='save or load results to/from json file', default=None)
    parser.add_argument('-z', '--network',
        help='show results for network', default=None)
    args = parser.parse_args()

    global email
    email = args.user
    global password
    password = args.password
    ytvbot_dir = args.configdir
    output_dir = args.output
    download_files = args.nodownload
    link_output = args.links
    progress_bar = args.progress
    search = args.search
    json_file = args.json
    network = args.network


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
        mgr = Manager(output_dir, recordings, progress_bar=progress_bar)
        mgr.start()

logger = add_logger('ytvbot')

if __name__ == "__main__":
    main()
