# -*- coding: utf-8 -*-

import sys
import logging
import platform
import psutil
import pickle
import os

from pyvirtualdisplay import Display

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile

from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import NoSuchElementException


class Browser:

    def __init__(self, timeout=20, config_dir=None,
                    loglevel=logging.DEBUG):

        reload(sys)
        sys.setdefaultencoding('utf8')

        logger = logging.getLogger('browser')
        logger.setLevel(loglevel)
        ch = logging.StreamHandler()
        ch.setLevel(loglevel)
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        ch.setFormatter(formatter)
        logger.addHandler(ch)
        self.logger = logger

        if 'Linux' in platform.uname():
            self.logger.info('starting headless mode')
            self.display = Display(visible=0, size=(1024, 768))
            self.display.start()
        else:
            self.logger.info(
                'MacOS or Windows detected, can\'t start headless mode')

        #Disable images to speed up loading times
        firefox_profile = FirefoxProfile()
        firefox_profile.set_preference('permissions.default.image', 2)
        firefox_profile.set_preference('permissions.default.stylesheet', 2)
        self.browser = webdriver.Firefox(firefox_profile)

        self.logged_in = False

        self.timeout = timeout
        self.config_dir = config_dir

    def __import_cookies_file__(self, cookies_file):

        self.logger.debug('cookies file: %s' % cookies_file)
        self.logger.debug(
            "cookies found, adding to current browser session")
        cookies = pickle.load(open(cookies_file, "rb"))
        for cookie in cookies:
            self.browser.add_cookie(cookie)
        self.browser.get('https://www.youtv.de/')

    def __check_logged_in__(self):
        try:
            element_present = EC.presence_of_element_located((
                By.LINK_TEXT,'Mein Account'))
            WebDriverWait(self.browser, self.timeout).until(element_present)
            self.logger.info('Logged in.')
            self.logged_in = True
        except TimeoutException:
            self.logger.info("Timed out waiting for page to load")

    def login(self, email, password):

        self.logger.info('Loggin in')
        self.browser.get('https://www.youtv.de/login')

        cookies_file = "cookies"
        if self.config_dir:
            cookies_file = os.path.join(self.config_dir, cookies_file)

        if os.path.isfile(cookies_file):
            self.__import_cookies_file__(cookies_file)
        else:
            self.logger.debug('No cookies found, logging in')
            login_email = self.browser.find_element_by_id("session_email")
            login_email.send_keys(email)
            login_password = self.browser.find_element_by_id(
                'session_password')
            login_password.send_keys(password)

            self.browser.find_element_by_xpath(
                "//input[@value='Anmelden']").click()

        self.__check_logged_in__()
        pickle.dump( self.browser.get_cookies() , open(cookies_file,"wb"))



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
