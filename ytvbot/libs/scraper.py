# -*- coding: utf-8 -*-

import sys
import logging

from selenium.common.exceptions import NoSuchElementException


class Scraper:

    def __init__(self, browser, loglevel=logging.DEBUG):

        reload(sys)
        sys.setdefaultencoding('utf8')

        logger = logging.getLogger('scraper')
        logger.setLevel(loglevel)
        ch = logging.StreamHandler()
        ch.setLevel(loglevel)
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        ch.setFormatter(formatter)
        logger.addHandler(ch)

        self.logger = logger

        self.browser = browser
        self.logged_in = False


    def get_available_recordings(self):

        self.logger.info('Getting available recordings')
        self.browser.get('https://www.youtv.de/videorekorder')
        # Scroll to bottom to load all recordings
        self.browser.execute_script(
            "window.scrollTo(0, document.body.scrollHeight);")

        recordings = []
        titles = self.browser.find_elements_by_class_name(
            'broadcasts-table-cell-title')
        for title in titles:
            href = None
            try:
                recording = title.find_element_by_tag_name('a')
                href = recording.get_attribute('href')
            except NoSuchElementException:
                pass

            if href:
                self.logger.debug("recording found: %s" % href)
                recordings.append(href)

        self.logger.info('Found %i available recordings' % len(recordings))

        return recordings


    def get_links_for_recording(self, url):

        self.logger.info('Getting links from: %s' % url)
        self.browser.get(url)

        downloads =  self.browser.find_elements_by_partial_link_text(
            'Definition')
        downloads += self.browser.find_elements_by_partial_link_text(
            'Qualität')

        links = []
        for d in downloads:
            links.append(d.get_attribute('href').split('?')[0])
        self.logger.debug('links for recording %s found %s' %
            (url, str(links)))

        return links


    def get_links_for_recordings(self, urls):

        links = {}
        for url in urls:
            new_links = self.get_links_for_recording(url)
            links[url] = new_links

        return links


    def select_download_links(  self, recording_links,
                                quality_priority_list=['hd','hq','nq']):

        self.logger.info('Selecting best resolution for recordings')
        download_links = []
        for recording in recording_links:
            links = recording_links[recording]
            for link in links:
                for quality in quality_priority_list:
                    if quality in link:
                        self.logger.debug('Selecting link: %s' % link)
                        download_links.append(link)
                        break
                    break

        return download_links


    def get_all_download_links( self, quality_priority_list=['hd','hq','nq']):
        recordings = self.get_available_recordings()
        recording_links = self.get_links_for_recordings(recordings)
        download_links = self.select_download_links(recording_links)

        return download_links
