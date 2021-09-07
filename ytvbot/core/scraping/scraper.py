# -*- coding: utf-8 -*-

import os
import datetime
import time

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC

from .recording import Recording
from ..log import add_logger


class Scraper:
    def __init__(self, browser):

        self.logger = add_logger("scraper")

        self.browser = browser
        self.logged_in = False
        self.recorder_url = "https://www.youtv.de/videorekorder"

    def get_recording_link(self, title):

        href = None
        try:
            recording = title.find_element_by_tag_name("a")
            href = recording.get_attribute("href")
        except NoSuchElementException:
            pass

        if href:
            self.logger.debug("recording found: %s" % href)
            return href
        else:
            return None

    def load_recordings_page(self):

        self.logger.info("Getting available recordings")
        self.browser.get(self.recorder_url)
        # Scroll to bottom to load all recordings
        self.browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")

    def get_available_recordings(self, name=None):

        recordings = []

        titles = self.browser.find_elements_by_class_name("broadcasts-table-cell-title")

        for title in titles:
            if name:
                title_tmp = None
                try:
                    title_tmp = title.find_element_by_tag_name("b")
                except NoSuchElementException:
                    pass
                if title_tmp:
                    if name in title_tmp.text:
                        recordings.append(self.get_recording_link(title))
            else:
                recording_tmp = self.get_recording_link(title)
                if recording_tmp:
                    recordings.append(recording_tmp)

        return recordings

    def get_stream_url(self, url):
        stream_url = "%s/streamen" % url
        self.logger.debug("Trying to find the stream url: %s" % url)
        self.browser.get(stream_url)
        if self.browser.current_url == self.recorder_url:
            self.logger.debug("Can't use stream url: %s" % stream_url)
            return None
        self.logger.debug("Trying to find the video element")
        stream_video = self.browser.find_element_by_id("youtv-video")
        download_url = stream_video.get_attribute("src")
        # self.logger.debug(url_tmp)
        # self.logger.debug(download_url)
        return download_url

    def get_recording_links(self, url):

        self.logger.info("Getting links from: %s" % url)

        self.browser.find_element_by_class_name("download-button").click()


        downloads = self.browser.find_elements_by_partial_link_text("Definition")
        downloads += self.browser.find_elements_by_partial_link_text("Qualität")

        links = []
        for d in downloads:
            links.append(d.get_attribute("href").split("?")[0])
        self.logger.debug("links for recording %s found %s" % (url, str(links)))

        return links

    def get_recording_showname(self, url):

        show_name = None

        try:
            show_tmp = self.browser.find_element_by_class_name(
                "broadcast-details-header--content"
            )
            show_name = show_tmp.find_element_by_tag_name("a").text.title()
        except NoSuchElementException:
            self.logger.debug("Cant find show link for: %s" % url)

        if not show_name:
            try:
                show_tmp = self.browser.find_element_by_class_name(
                    "broadcast-details-header--content"
                )
                show_name = show_tmp.find_element_by_tag_name("h3").text.title()
            except NoSuchElementException:
                self.logger.debug("Can't find any show name for: %s" % url)
        return show_name

    def get_recording_title(self, url):

        title = None

        try:
            title_tmp = self.browser.find_element_by_class_name(
                "broadcast-details-header--content"
            )
            title = title_tmp.find_element_by_tag_name("small").text
        except NoSuchElementException:
            self.logger.debug("Cant find title: %s" % url)

        return title

    def __get_desc_list__(self, url):

        desc_list = None

        try:
            date_tmp = self.browser.find_element_by_class_name(
                "broadcast-details-header--content-channel-description"
            )
            desc_list = date_tmp.text.split()
        except NoSuchElementException:
            self.logger.debug("Can't find desc list: %s" % url)
        return desc_list

    def get_recording_dates(self, url):

        desc_list = self.__get_desc_list__(url)

        if desc_list:
            date = desc_list[4]
            start_time = desc_list[1]
            stop_time = desc_list[3].strip(",")

            start_tmp = date + ":" + start_time
            stop_tmp = date + ":" + stop_time

            start_date = datetime.datetime.strptime(start_tmp, "%d.%m.%Y:%H:%M")
            stop_date = datetime.datetime.strptime(stop_tmp, "%d.%m.%Y:%H:%M")

        else:
            self.logger.debug("No recording date found for: %s" % url)

        return [start_date, stop_date]

    def get_recording_genre(self, url):

        genre = None
        desc_list = self.__get_desc_list__(url)

        if desc_list:
            genre = desc_list[6].strip(",")
            if len(desc_list) > 7:
                for i in range(7, len(desc_list)):
                    if desc_list[i] in ["Episode", "Folge", "Staffel"]:
                        break
                    else:
                        genre += " " + desc_list[i].strip(",")

        else:
            self.logger.debug("No recording date found for: %s" % url)

        return genre

    def __get__next_item_from_desc_list__(self, url, search):

        item = None
        search_list = []

        if not isinstance(search, list):
            search_list.append(search)
        else:
            search_list = search

        desc_list = self.__get_desc_list__(url)
        if desc_list:
            for i in range(0, len(desc_list)):
                if desc_list[i].strip(",") in search_list:
                    item = desc_list[i + 1]
        else:
            self.logger.debug("Can't find %s in desc list: %s" % (str(search), url))

        return item

    def get_recording_episode(self, url):

        episode = self.__get__next_item_from_desc_list__(url, ["Episode", "Folge"])
        return episode

    def get_recording_season(self, url):

        season = self.__get__next_item_from_desc_list__(url, ["Season", "Staffel"])
        return season

    def get_recording_information(self, url):

        information = []

        try:
            information_tmp = self.browser.find_element_by_class_name(
                "broadcast-details--information"
            )
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
                "broadcast-details-header--content-channel-logo"
            )
            nw = nw_tag.find_element_by_tag_name("img")
            network = nw.get_attribute("alt")
        except NoSuchElementException:
            self.logger.debug("No network name found for: %s" % url)

        return network

    def get_recording_from_url(self, url, get_links=True):

        if not self.browser.current_url == url:
            self.browser.get(url)

        links = self.get_recording_links(url)
        if get_links:
            if len(links) < 1:
                links_new = self.get_stream_url(url)
                if links_new:
                    links.append(links_new)
                self.browser.get(url)
                if len(links) < 1:
                    self.logger.debug("No downloadable link found for %s" % url)
                    return None
        else:
            links = None
        name = self.get_recording_showname(url)
        title = self.get_recording_title(url)
        information = self.get_recording_information(url)
        recording_dates = self.get_recording_dates(url)
        genre = self.get_recording_genre(url)
        network = self.get_recording_network(url)
        episode = self.get_recording_episode(url)
        season = self.get_recording_season(url)

        recording = Recording(
            url,
            name,
            links,
            title,
            information,
            recording_dates[0],
            recording_dates[1],
            genre,
            network,
            season,
            episode,
        )
        return recording

    def get_recordings(self, search=None, network=None, get_links=True):
        recordings = []
        recordings_urls = []

        if not self.browser.current_url == self.recorder_url:
            self.load_recordings_page()

        recordings_urls = self.get_available_recordings(search)

        self.logger.debug("recording_urls: %s" % recordings_urls)
        for url in recordings_urls:
            self.logger.debug("Getting recording from url: %s" % url)
            rec = self.get_recording_from_url(url, get_links)
            if rec:
                recordings.append(rec)

        # reverse recordings list as the last one is the oldest one
        recordings.reverse()
        if network:
            rec_nw = []
            for rec in recordings:
                if network == rec.network:
                    rec_nw.append(rec)
            return rec_nw
        else:
            return recordings

    def delete_recordings(self, recordings, output_dir):
        for r in recordings:
            filename = r.format_output_filename()
            output_file = None
            if output_dir:
                if r.show_name:
                    output_file = os.path.join(output_dir, r.show_name, filename)
                else:
                    output_file = os.path.join(output_dir, filename)
            else:
                if r.show_name:
                    output_file = os.path.join(r.show_name, filename)

            if os.path.isfile(output_file):
                self.logger.debug("Recording file found: %s" % output_file)
                if not self.browser.current_url == r.url:
                    self.logger.debug("Loading recording url: %s" % r.url)
                    self.browser.get(r.url)
                self.browser.find_element_by_class_name("delete-button").click()
                try:
                    self.logger.debug("Accepting confirmation dialog")
                    WebDriverWait(self.browser, 5).until(
                        EC.alert_is_present(), "Waiting for alert timed out"
                    )
                    alert = self.browser.switch_to.alert
                    alert.accept()
                except TimeoutException:
                    self.logger.debug("Can't confirm deletion")
            time.sleep(10)
