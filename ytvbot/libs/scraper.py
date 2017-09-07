# -*- coding: utf-8 -*-

import sys
import logging
import platform
import psutil

from pyvirtualdisplay import Display

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import NoSuchElementException


class Scraper:

    def __init__(self, timeout=20,loglevel='DEBUG'):

        reload(sys)
        sys.setdefaultencoding('utf8')

        logger = logging.getLogger('scraper')
        logger.setLevel(logging.DEBUG)
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        ch.setFormatter(formatter)
        logger.addHandler(ch)
        self.logger = logger

        if 'Linux' in platform.uname():
            self.logger.info('starting headless mode')
            self.display = Display(visible=0, size=(1024, 768))
            self.display.start()
        else:
            self.logger.info('MacOS or Windows detected, can\'t start headless mode')

        self.browser = webdriver.Firefox()
        logged_in = False

        self.timeout = timeout



    def login(self, email, password):

        self.logger.info('Loggin in')
        self.browser.get('https://www.youtv.de/login')

        login_email = self.browser.find_element_by_id("session_email")
        login_email.send_keys(email)
        login_password = self.browser.find_element_by_id('session_password')
        login_password.send_keys(password)

        self.browser.find_element_by_xpath("//input[@value='Anmelden']").click()

        self.logged_in = False
        try:
            element_present = EC.presence_of_element_located((By.LINK_TEXT,
                'Mein Account'))
            WebDriverWait(self.browser, self.timeout).until(element_present)
            self.logger.info('Logged in.')
            self.logged_in = True
        except TimeoutException:
            self.logger.info("Timed out waiting for page to load")




    def get_available_recordings(self):

        self.logger.info('Getting available recordings')
        self.browser.get('https://www.youtv.de/videorekorder')
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


    def destroy(self):

        self.browser.close()

        if 'Linux' in platform.uname():
            self.display.popen.kill()

        for proc in psutil.process_iter():
            if proc.name() == 'geckodriver':
                try:
                    proc.kill()
                except NoSuchProcess:
                    pass
