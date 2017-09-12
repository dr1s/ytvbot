#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import os
import sys
import getopt
import logging
import fileDownloader


from libs.browser import Browser
from libs.scraper import Scraper

from selenium.common.exceptions import WebDriverException
from urllib2 import HTTPError


email = None
password = None

ytvbot_dir = None
search = None

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
    print(" -s | --search [show_name]: only look for show_name")

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


def get_download_links(search=None):
    download_links = []
    br = Browser(config_dir=ytvbot_dir, loglevel=loglevel)
    try:
        br.login(email, password)
        scraper = Scraper(br.browser, loglevel=loglevel)
        download_links = scraper.get_all_download_links(search)
        br.destroy()
    except KeyboardInterrupt or WebDriverException:
        if br:
            br.destroy()
    return download_links

def download(links, output_dir=None, progress_bar=False):

    for item in links:
        filename = os.path.basename(item)
        output_file = filename
        tmp_file = filename + ".download"
        if output_dir:
            output_file = os.path.join(output_dir, filename)

        downloader = fileDownloader.DownloadFile(item, output_file,
                    progress_bar=progress_bar)
        if os.path.isfile(output_file):
            if (os.path.isfile(tmp_file)):
                logger.debug('Resuming download: %s' % item)
                try:
                    downloader.resume()
                    os.remove(tmp_file)
                except HTTPError:
                    logger.debug(
                        "Can't resume. File already finished downloading")
            else:
                logger.debug("File already finished downloading: %s" %
                    output_file)
        else:
            logger.info('Downloading: %s' % item)
            with open(tmp_file, 'w'):
                    os.utime(tmp_file, None)
            downloader.download()
            os.remove(tmp_file)


def write_links_to_file(links, output):

    logger.info("Wrtiting links to file: %s" % output)
    print links
    for link in links:
        if link not in open(output).read():
            logger.debug('Link not found in file adding: %s' % link)
            with open(output, "a") as f:
                f.write("%s\n" % link)
        else:
            logger.debug('Link already found in file %s' % link)


def main():

    output_dir = None
    link_output = None
    download_links_file = None
    download_files = True
    progress_bar = False

    try:
        long = ["help", "output=", "links=", "file=", "user=",
                "password=", "config-dir=", "no-download", "progress",
                "search"]
        opts, args = getopt.getopt(sys.argv[1:], "hno:l:f:u:p:c:#s:", long )
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
        elif o in ("-s", "--search"):
            global search
            search = a
        else:
            assert False, "unhandled option"

    setup_dir()
    download_links = None
    recording_links = []
    browsers = None

    if not download_links_file:
        download_links = get_download_links(search)
        print download_links
    else:
        with open(download_links_file) as f:
            download_links = f.readlines()
        download_links = [x.strip() for x in download_links]

    cache_file = os.path.join(ytvbot_dir, 'cache')
    write_links_to_file(download_links, cache_file)

    if link_output and not download_links_file:
        with open(link_output, 'w'):
                    os.utime(link_output, None)
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
