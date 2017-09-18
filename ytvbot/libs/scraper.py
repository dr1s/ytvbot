# -*- coding: utf-8 -*-

import sys
import logging
import datetime

from selenium.common.exceptions import NoSuchElementException

from recording import Recording


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

        recordings = []

        titles = self.browser.find_elements_by_class_name(
            'broadcasts-table-cell-title')

        for title in titles:
            title_tmp = None
            try:
                title_tmp = title.find_element_by_tag_name('b')
            except NoSuchElementException:
                pass
            if title_tmp:
                if name in title_tmp.text:
                    recordings.append(self.get_recording_link(title))

        return recordings


    def get_recording_links(self, url):

        self.logger.info('Getting links from: %s' % url)

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


    def get_recording_showname(self, url):

        show_name = None

        try:
            show_tmp = self.browser.find_element_by_class_name(
                "broadcast-details-header--content")
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


    def get_recording_title(self, url):

        title = None

        try:
            title_tmp = self.browser.find_element_by_class_name(
                "broadcast-details-header--content")
            title = title_tmp.find_element_by_tag_name('small').text
        except NoSuchElementException:
            self.logger.debug('Cant find title: %s' % url)

        return title


    def get_recording_dates(self, url):

        try:
            date_tmp = self.browser.find_element_by_class_name(
                "broadcast-details-header--content-channel-description")
            desc_list = date_tmp.text.split()

            date = desc_list[4]
            start_time = desc_list[1]
            stop_time = desc_list[3].strip(',')

            start_tmp = date + ':' + start_time
            stop_tmp = date + ':' + stop_time

            start_date = datetime.datetime.strptime(
                start_tmp, "%d.%m.%Y:%H:%M")
            stop_date = datetime.datetime.strptime(
                stop_tmp, "%d.%m.%Y:%H:%M")


        except NoSuchElementException:
            self.logger.debug("No recording date found for: %s" % url)

        return [start_date, stop_date]


    def get_recording_genre(self, url):

        genre = None

        try:
            tmp = self.browser.find_element_by_class_name(
                "broadcast-details-header--content-channel-description")
            desc_list = tmp.text.split()

            genre = desc_list[6].strip(',')
            if len(desc_list) > 7:
                for i in range(7, len(desc_list)):
                    if desc_list[i] in ['Episode', 'Folge', 'Staffel']:
                        break
                    else:
                        genre += " " + desc_list[i].strip(',')

        except NoSuchElementException:
            self.logger.debug("No recording date found for: %s" % url)

        return genre


    def get_recording_episode(self, url):

        episode = None

        try:
            tmp = self.browser.find_element_by_class_name(
                "broadcast-details-header--content-channel-description")
            desc_list = tmp.text.split()
            for i in range(0, len(desc_list)):
                if desc_list[i].strip(',') in ['Episode', 'Folge']:
                    episode = desc_list[i+1]
        except NoSuchElementException:
            self.logger.debug("Can't find episode number: %s" % url)

        return episode


    def get_recording_season(self, url):

        season = None

        try:
            tmp = self.browser.find_element_by_class_name(
                "broadcast-details-header--content-channel-description")
            desc_list = tmp.text.split()
            for i in range(0, len(desc_list)):
                if desc_list[i].strip(',') in ['Staffel', 'Season']:
                    season = desc_list[i+1]
        except NoSuchElementException:
            self.logger.debug("Can't find season number: %s" % url)

        return season


    def get_recording_information(self, url):

        information = []

        try:
            information_tmp = self.browser.find_element_by_class_name(
                "broadcast-details--information")
            information_div = information_tmp.find_elements_by_tag_name("div")
            for i in information_div:
                information.append(i.text)
        except NoSuchElementException:
            self.logger.debug("No information found for: %s" % url)
        return information


    def get_recording_network(self, url):

        network = None
        try:
            nw_tag = self.browser.find_element_by_class_name(
                'broadcast-details-header--content-channel-logo')
            nw = nw_tag.find_element_by_tag_name("img")
            network = nw.get_attribute('alt')
        except NoSuchElementException:
            self.logger.debug("No network name found for: %s" % url)

        return network


    def get_recording_from_url(self, url):

        if not self.browser.current_url == url:
            self.browser.get(url)

        links = self.get_recording_links(url)
        name = self.get_recording_showname(url)
        title = self.get_recording_title(url)
        information = self.get_recording_information(url)
        recording_dates = self.get_recording_dates(url)
        genre = self.get_recording_genre(url)
        network = self.get_recording_network(url)
        episode = self.get_recording_episode(url)
        season = self.get_recording_season(url)

        recording = Recording(url, name, links, title, information,
            recording_dates[0], recording_dates[1], genre, network,
            season, episode)
        return recording


    def get_recordings(self, search=None):
        recordings = []
        recordings_urls= []

        if not self.browser.current_url == self.recorder_url:
            self.load_recordings_page()

        if search:
            recordings_urls = self.get_recordings_for_name(search)
        else:
            recordings_urls = self.get_available_recordings()

        for url in recordings_urls:
            recordings.append(self.get_recording_from_url(url))

        #reverse recordings list as the last one is the oldest one
        recordings.reverse()
        return recordings
