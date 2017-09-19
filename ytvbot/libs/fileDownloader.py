"""Downloads files from http or ftp locations.

Copyright Joshua Banton"""
from __future__ import division
import os
import urllib2
import urlparse
import urllib
import sys
import socket
from log import add_logger

from tqdm import tqdm

from time import time, sleep

version = "0.4.0"

class DownloadFile(object):
    """This class is used for downloading files from the internet via http or ftp.
    It supports resuming downloads.
    It does not support https or sftp at this time.

    The main advantage of this class is it's ease of use, and pure pythoness. It only uses the Python standard library,
    so no dependencies to deal with, and no C to compile.

    #####
    If a non-standard port is needed just include it in the url (http://example.com:7632).

    #Rate Limiting:
        rate_limit = the average download rate in Bps
        rate_burst = the largest allowable burst in bytes

    Basic usage:
        Simple
            downloader = fileDownloader.DownloadFile('http://example.com/file.zip')
            downloader.download()
         Use full path to download
             downloader = fileDownloader.DownloadFile('http://example.com/file.zip', "C:/Users/username/Downloads/newfilename.zip")
             downloader.download()
         Resume
             downloader = fileDownloader.DownloadFile('http://example.com/file.zip')
            downloader.resume()
    """

    def __init__(self, url=None, localFileName=None, timeout=120.0, autoretry=False, retries=5,
                 fast_start=False, rate_limit_on=False, rate_limit=500, rate_burst=1000, progress_bar=None):
        self.url = url
        self.urlFileName = None
        self.progress = 0
        self.fileSize = None
        self.localFileName = localFileName
        self.url_type = self.getType()
        self.timeout = timeout
        self.retries = retries
        self.fast_start = fast_start
        self.curretry = 0
        self.cur = 0
        if not self.fast_start:
            try:
                self.urlFilesize = self.getUrlFileSize()
            except urllib2.HTTPError:
                self.urlFilesize = None
        else:
            self.urlFilesize = None
        if not self.localFileName: #if no filename given pulls filename from the url
            self.localFileName = self.getUrlFilename(self.url)
        self.rate_limit_on = rate_limit_on
        self.rate_limit = rate_limit
        self.rate_burst = rate_burst
        if self.rate_limit_on:
            self.bucket = TokenBucket(self.rate_burst, self.rate_limit)
        self.progress_bar = progress_bar
        self.logger = add_logger("filedownloader")

    def __downloadFile__(self, urlObj, fileObj, callBack=None):
        """starts the download loop"""
        pbar = None
        if not self.fast_start:
            self.fileSize = self.getUrlFileSize()
            #Progress bar only works if we have the fileSize
            curSize = self.getLocalFileSize()
            if self.progress_bar:
                if self.fileSize > sys.maxint:
                    pbar = tqdm(total=long(self.fileSize)//8192, unit_scale=True,
                            initial=curSize//8192, dynamic_ncols=True,
                            desc=os.path.basename(self.localFileName),
                            bar_format="{l_bar}{bar} | [{elapsed}<{remaining}]")
                else:
                    pbar = tqdm(total=int(self.fileSize), unit_scale=True,
                            initial=curSize, unit="b", dynamic_ncols=True,
                            desc=os.path.basename(self.localFileName))

        while 1:
            if self.rate_limit_on:
                if not self.bucket.spend(8192):
                    sleep(1)
                    continue
            try:
                data = urlObj.read(8192)
            except (socket.timeout, socket.error) as t:
                print "caught ", t
                self.__retry__()
                break
            if not data:
                fileObj.close()
                break
            fileObj.write(data)
            self.cur += 8192
            if pbar:
                if self.fileSize > sys.maxint:
                    pbar.update(1)
                else:
                    pbar.update(8192)
            if callBack:
                callBack(cursize=self.cur)
        pbar.close()


    def __retry__(self):
        """auto-resumes up to self.retries"""
        if self.retries > self.curretry:
                self.curretry += 1
                if self.getLocalFileSize() != self.urlFilesize:
                    self.resume()
        else:
            print 'retries all used up'
            return False, "Retries Exhausted"

    def __startHttpResume__(self, restart=None, callBack=None):
        """starts to resume HTTP"""
        curSize = self.getLocalFileSize()
        if curSize >= self.urlFilesize:
            return False
        self.cur = curSize
        if restart:
            f = open(self.localFileName , "wb")
        else:
            f = open(self.localFileName , "ab")
        req = urllib2.Request(self.url)
        req.headers['Range'] = 'bytes=%s-%s' % (curSize, self.getUrlFileSize())
        urllib2Obj = urllib2.urlopen(req, timeout=self.timeout)
        self.__downloadFile__(urllib2Obj, f, callBack=callBack)

    def getUrlFilename(self, url):
        """returns filename from url"""
        return urllib.unquote(os.path.basename(url))

    def getUrlFileSize(self):
        """gets filesize of remote file from ftp or http server"""
        if self.url_type == 'http':
            urllib2Obj = urllib2.urlopen(self.url, timeout=self.timeout)
            size = urllib2Obj.headers.get('content-length')
            return size

    def getLocalFileSize(self):
        """gets filesize of local file"""
        size = os.stat(self.localFileName).st_size
        return size

    def getType(self):
        """returns protocol of url (ftp or http)"""
        url_type = urlparse.urlparse(self.url).scheme
        return url_type

    def checkExists(self):
        """Checks to see if the file in the url in self.url exists"""
        try:
            urllib2.urlopen(self.url, timeout=self.timeout)
        except urllib2.HTTPError:
            return False
        return True

    def download(self, callBack=None):
        """starts the file download"""
        self.curretry = 0
        self.cur = 0
        f = open(self.localFileName , "wb")
        try:
            urllib2Obj = urllib2.urlopen(self.url, timeout=self.timeout)
            self.__downloadFile__(urllib2Obj, f, callBack=callBack)
        except urllib2.HTTPError:
            self.logger.debug("Can't download file: %s" % self.url)

        return True


    def resume(self, callBack=None):
        """attempts to resume file download"""
        url_type = self.getType()
        if url_type == 'http':
            self.__startHttpResume__(callBack=callBack)


class FileDownloaderError(Exception):
    def __init(self, message=''):
        self.message = message


class TokenBucket(object):
    """An implementation of the token bucket algorithm.
       Slightly modified from http://code.activestate.com/recipes/511490-implementation-of-the-token-bucket-algorithm/"""

    def __init__(self, bucket_size, fill_rate):
        """tokens is the total tokens in the bucket. fill_rate is the
        rate in tokens/second that the bucket will be refilled."""
        self.capacity = float(bucket_size)
        self._tokens = float(bucket_size)
        self.fill_rate = float(fill_rate)
        self.timestamp = time()

    def spend(self, tokens):
        """Spend tokens from the bucket. Returns True if there were
        sufficient tokens otherwise False."""
        if tokens <= self.get_tokens():
            self._tokens -= tokens
        else:
            return False
        return True

    def get_tokens(self):
        now = time()
        if self._tokens < self.capacity:
            delta = self.fill_rate * (now - self.timestamp)
            self._tokens = min(self.capacity, self._tokens + delta)
        self.timestamp = now
        return self._tokens
