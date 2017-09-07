#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import os
import sys
import getopt
import logging
import fileDownloader

from libs import scraper

from selenium.common.exceptions import WebDriverException
from urllib2 import HTTPError

email = None
password = None

ytvbot_dir = None

def download(links, output_dir=None):

    for item in links:
        filename = item.split('/')[len(item.split('/'))-1]
        output_file = filename
        if output_dir:
            output_file = os.path.join(output_dir, filename)

        downloader = fileDownloader.DownloadFile(item, output_file)
        if os.path.isfile(filename):
            logger.info('Resuming download: %s' % item)
            try:
                downloader.resume()
            except HTTPError:
                pass
        else:
            logger.info('Downloading: %s' % item)
            downloader.download()

def select_download_links(recording_links):

    logger.info('Selecting best resolution for recordings')
    download_links = []
    for recording in recording_links:
        links = recording_links[recording]
        for link in links:
            if 'hd' in link:
                download_links.append(link)
                break
            elif 'hq' in link:
                download_links.append(link)
    return download_links


def write_links_to_file(links, output):

    logger.info("Wrtiting links to file: %s" % output)
    output_file = open(output, 'w')
    for item in links:
        output_file.write("%s\n" % item)
    output_file.close()

def usage():
    print("usage: ytvbot [arguments]")
    print(" -u | --user [email]: email adress of the account")
    print(" -p | --password [password]: password ouf the account ")
    print(" -o | --output [output_dir]: output directory")
    print(" -h | --help: shows this message")
    print(" -n | --no-download: Don't download anything")
    print(" -l | --links [output_file]: Save links in this file")
    print(" -f | --file [input_file]: File with links to download")

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
            os.utime(cache_file)

def main():

    print("_____.___.           _______________   _______.           __   ")
    print("\__  |   | ____  __ _\__    ___/\   \ /   /\_ |__   _____/  |_ ")
    print(" /   |   |/  _ \|  |  \|    |    \   Y   /  | __ \ /  _ \   __\\")
    print(" \____   (  <_> )  |  /|    |     \     /   | \_\ (  <_> )  |  ")
    print(" / ______|\____/|____/ |____|      \___/    |___  /\____/|__|  ")
    print(" \/                                             \/             ")
    print(" ")

    output_dir = None
    link_output = None
    download_links_file = None
    download_files = True

    try:
        long = ["help", "output=", "links=", "download-links=", "user=",
            "password="]
        opts, args = getopt.getopt(sys.argv[1:], "hno:l:d:u:p:", long )
    except getopt.GetoptError as err:
        print str(err)
        usage()
        sys.exit(2)
    for o, a in opts:
        if o in ("-h", "--help"):
            #usage()
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
        else:
            assert False, "unhandled option"

    setup_dir()
    download_links = None
    if not download_links_file:
        try:
            scrapers = scraper.Scraper()
            scrapers.login(email, password)
            recordings = scrapers.get_available_recordings()
            recording_links = scrapers.get_links_for_recordings(recordings)
            scrapers.destroy()
        except KeyboardInterrupt:
            scrapers.destroy()
        except WebDriverException:
            scrapers.destroy()
        download_links = select_download_links(recording_links)
    else:
        with open(download_links_file) as f:
            download_links = f.readlines()
        download_links = [x.strip() for x in download_links]

    for link in download_links:
        cache_file = os.path.join(ytvbot_dir, 'cache')
        if link not in open(cache_file).read():
            logger.debug('Link not found in cache, adding: %s' % link)
            with open(cache_file, "a") as f:
                f.write(link)
        else:
            logger.debug('Link already found in cache %s' % link)

    if link_output and not download_links_file:
        write_links_to_file(download_links, link_output)

    if download_files:
        download(download_links, output_dir)

logger = logging.getLogger('youtv')
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

if __name__ == "__main__":
    main()
