#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import os
import sys
import getopt
import logging
import fileDownloader
import json
import codecs
from prettytable import PrettyTable

from libs.browser import Browser
from libs.scraper import Scraper
from libs.importer import import_json_file
from libs.log import add_logger

from selenium.common.exceptions import WebDriverException
from urllib2 import HTTPError


email = None
password = None

ytvbot_dir = None
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


def select_download_link(recording, quality_priority='hd'):

    selected = None
    links = recording.links
    for link in links:
        link_found = False
        if isinstance(quality_priority, list):
            for quality in quality_priority:
                if quality in link:
                    link_found = True
                    selected = link
                    break
        else:
            if quality in link:
                link_found = True
                selected = link

        if link_found:
            logger.debug('Selecting link: %s' % selected)
            break

    return selected


def get_recordings(search=None):
    recordings = []
    br = Browser(config_dir=ytvbot_dir)
    try:
        br.login(email, password)
        scraper = Scraper(br.browser)
        recordings = scraper.get_recordings(search)
        br.destroy()
    except (KeyboardInterrupt, WebDriverException):
        if br:
            br.destroy()
    return recordings


def resume(downloader, download_link, output_file):

    tmp_file = output_file + ".download"

    if (os.path.isfile(tmp_file)):
        logger.debug('Resuming download: %s' % download_link)
        try:
            downloader.resume()
            os.remove(tmp_file)
        except HTTPError:
            logger.debug(
                "Can't resume. File already finished downloading")
    else:
        logger.debug("File already finished downloading: %s" %
            output_file)


def download_recording(item, output_dir, progress_bar=False):
    download_link = select_download_link(item, ['hd', 'hq'])
    filename = item.format_output_filename()
    output_file = filename
    if output_dir:
        if item.show_name:
            output_tmp = os.path.join(output_dir, item.show_name)
            if not os.path.exists(output_tmp):
                os.mkdir(output_tmp)
            output_file = os.path.join(output_tmp, filename)
        else:
            output_file = os.path.join(output_dir, filename)
    else:
        if item.show_name:
            output_file = os.path.join(item.show_name, filename)
            if not os.path.exists(item.show_name):
                os.mkdir(str(item.show_name))


    if item.information:
        info_file = output_file.split('.')[0] + ".txt"
        item.write_information_file(info_file)


    downloader = fileDownloader.DownloadFile(download_link, output_file,
                progress_bar=progress_bar)

    if os.path.isfile(output_file):
        resume(downloader, download_link, output_file)
    else:
        logger.info('Downloading: %s' % download_link)
        tmp_file = output_file + ".download"
        with open(tmp_file, 'w'):
            os.utime(tmp_file, None)
        downloader.download()
        os.remove(tmp_file)



def download_recordings(links, output_dir=None, progress_bar=False):

    for item in links:
        download_recording(item, output_dir, progress_bar)


def write_links_to_file(recordings, output):

    logger.info("Wrtiting links to file: %s" % output)
    for recording in recordings:
        download_link = select_download_link(recording)
        if download_link:
            if download_link not in open(output).read():
                logger.debug('Link not found in file adding: %s' % download_link)
                with open(output, "a") as f:
                    f.write("%s\n" % download_link)
            else:
                logger.debug('Link already found in file %s' % download_link)


def print_recordings(recordings, fields='id'):
    pt = PrettyTable(fields)
    if isinstance(fields, list):
        for recording in recordings:
            pt.add_row(recording.list(fields))
    else:
        pt.add_row(recording.list(fields))
    print(pt)


def main():

    output_dir = None
    link_output = None
    download_files = True
    progress_bar = False
    json_file = None

    try:
        long_opts = ["help", "output=", "links=", "user=", "password=",
                "config-dir=", "no-download", "progress", "search=",
                "json="]

        opts, args = getopt.getopt(sys.argv[1:], "hno:l:u:p:c:#s:j:", long_opts )
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
            global ytvbot_dir
            ytvbot_dir = a
        elif o in ("-#", "--progress"):
            progress_bar = True
        elif o in ("-s", "--search"):
            global search
            search = a
        elif o in ("-j", "--json"):
            json_file = os.path.abspath(a)
        else:
            assert False, "unhandled option"

    setup_dir()

    if not json_file or (json_file and not os.path.exists(json_file)):
        recordings = get_recordings(search)

    if json_file:
        if os.path.isfile(json_file):
            logger.debug('Importig json file: %s' % json_file)
            recordings = import_json_file(json_file)
        else:
            logger.debug("Writing json file to: %s" % link_output)
            recordings_list = []
            for recording in recordings:
                recordings_list.append(recording.dict())
            with codecs.open(json_file, 'w', 'utf-8') as f:
                f.write(json.dumps(recordings_list, f, indent=2,
                    sort_keys=True, ensure_ascii=False))

    if recordings:
        print_recordings(recordings, ['id', 'name', 'title',
                'date', 'start_time', 'end_time', 'network'])
    else:
        logger.debug('No recordings found to print')

    #cache_file = os.path.join(ytvbot_dir, 'cache')
    #write_links_to_file(recordings, cache_file)

    if link_output:
        with open(link_output, 'w'):
            os.utime(link_output, None)
        write_links_to_file(recordings, link_output)

    if download_files:
        logger.info("Start download recordings")
        download_recordings(recordings, output_dir, progress_bar=progress_bar)

logger = add_logger('ytvbot')

if __name__ == "__main__":
    main()
