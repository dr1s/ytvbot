import os
import logging
import fileDownloader

from urllib2 import HTTPError



def download(links, output_dir=None, progress_bar=False):

    for item in links:
        filename = item.split('/')[len(item.split('/'))-1]
        output_file = filename
        tmp_file = filename + ".download"
        if output_dir:
            output_file = os.path.join(output_dir, filename)

        downloader = fileDownloader.DownloadFile(item, output_file,
                    progress_bar=progress_bar)
        if os.path.isfile(output_file):
            if (os.path.isfile(tmp_file)):
                logger.info('Resuming download: %s' % item)
                try:
                    downloader.resume()
                    os.remove(tmp_file)
                except HTTPError:
                    logger.debug(
                        "Can't resume. File already finished downloading")
        else:
            logger.info('Downloading: %s' % item)
            with open(tmp_file, 'w'):
                    os.utime(tmp_file, None)
            downloader.download()
            os.remove(tmp_file)


def write_links_to_file(links, output):

    logger.info("Wrtiting links to file: %s" % output)
    #output_file = open(output, 'w')
    for link in links:
        if link not in open(output).read():
            logger.debug('Link not found in file adding: %s' % link)
            with open(output, "a") as f:
                f.write("%s\n" % link)
        else:
            logger.debug('Link already found in file %s' % link)
    #output_file.close()
