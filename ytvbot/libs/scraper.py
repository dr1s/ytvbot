# -*- coding: utf-8 -*-

import sys
import logging

from selenium.common.exceptions import NoSuchElementException


class Recording:

    def __init__(self, url, show_name, links , information=None):
        self.url = url
        self.show_name = show_name
        self.links = links
        self.information = information



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
        self.recorder_url = "https://www.youtv.de/videorekorder"

    def get_recording_link(self, title):

        href = None
        try:
            recording = title.find_element_by_tag_name('a')
            href = recording.get_attribute('href')
        except NoSuchElementException:
            pass

        if href:
            self.logger.debug("recording found: %s" % href)
            return href
        else:
            return None

    def load_recordings_page(self):
        self.logger.info('Getting available recordings')
        self.browser.get(self.recorder_url)
        # Scroll to bottom to load all recordings
        self.browser.execute_script(
            "window.scrollTo(0, document.body.scrollHeight);")

    def get_available_recordings(self):
        if not self.browser.current_url is self.recorder_url:
            self.load_recordings_page()
        recordings = []
        titles = self.browser.find_elements_by_class_name(
            'broadcasts-table-cell-title')
        for title in titles:
            recording_tmp = self.get_recording_link(title)
            if recording_tmp:
                recordings.append(recording_tmp)

        self.logger.info('Found %i available recordings' % len(recordings))

        return recordings


    def get_recordings_for_name(self, name):
        if not self.browser.current_url is self.recorder_url:
            self.load_recordings_page()
        recordings = []
        titles = self.browser.find_elements_by_class_name(
            'broadcasts-table-cell-title')
        for title in titles:
            if name in title.text:
                recordings.append(self.get_recording_link(title))

        return recordings


    def get_links_for_recording(self, url):

        self.logger.info('Getting links from: %s' % url)
        if not self.browser.current_url is url:
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


    def get_showname_from_recording(self, url):

        show_name = None
        if not self.browser.current_url is url:
            self.browser.get(url)

        try:
            show_tmp = self.browser.find_element_by_class_name("broadcast-details-header--content")
            show_name = show_tmp.find_element_by_tag_name('a').text.title()
        except NoSuchElementException:
            self.logger.debug("Cant find show link for: %s" % url)

        if not show_name:
            try:
                show_tmp = self.browser.find_element_by_class_name(
                    "broadcast-details-header--content")
                show_name = show_tmp.find_element_by_tag_name('h3').text.title()
            except NoSuchElementException:
                self.logger.debug("Can't find any show name for: %s" % url)
        return show_name


    def get_information_from_recording(self, url):

        information = []

        if not self.browser.current_url is url:
            self.browser.get(url)

        try:
            information_tmp = self.browser.find_element_by_class_name(
                "broadcast-details--information")
            information_div = information_tmp.find_elements_by_tag_name("div")
            for i in information_div:
                information.append(i.text)
        except NoSuchElementException:
            self.logger.debug("No information found for: %s" % url)
        return information

    def get_recording_from_url(self, url):

        links = self.get_links_for_recording(url)
        name = self.get_showname_from_recording(url)
        information = self.get_information_from_recording(url)
        recording = Recording(url, name, links, information)
        return recording


    def get_recordings(self, search=None):
        recordings = []
        recordings_urls= []
        if search:
            recordings_urls = self.get_recordings_for_name(search)
        else:
            recordings_urls = self.get_available_recordings()

        for url in recordings_urls:
            recordings.append(self.get_recording_from_url(url))

        return recordings
