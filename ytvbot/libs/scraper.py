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
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        ch.setFormatter(formatter)
        logger.addHandler(ch)

        self.logger = logger

        self.browser = browser
        self.logged_in = False


    def get_available_recordings(self):

        self.logger.info('Getting available recordings')
        self.browser.get('https://www.youtv.de/videorekorder')
        # Scroll to bottom to load all recordings
        self.browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        recordings = []
        titles = self.browser.find_elements_by_class_name('broadcasts-table-cell-title')
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

        return recordings

    def get_links_for_recording(self, url):

        self.logger.info('Getting links for: %s' % url)
        self.browser.get(url)

        downloads =  self.browser.find_elements_by_partial_link_text('Definition')
        downloads += self.browser.find_elements_by_partial_link_text('Qualität')

        links = []
        for d in downloads:
            links.append(d.get_attribute('href').split('?')[0])
        self.logger.debug('links for recording %s found %s' %(url, str(links)))

        return links


    def get_links_for_recordings(self, urls):

        self.logger.info("getting links for recordings")
        links = {}
        for url in urls:
            new_links = self.get_links_for_recording(url)
            links[url] = new_links
        return links
