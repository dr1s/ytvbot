import fileDownloader
import os
from log import add_logger
from utils import check_dir
from urllib2 import HTTPError


class Manager(object):
    def __init__(self, output_dir, recordings, progress_bar=None):
        self.output_dir = output_dir
        self.downloads = []
        self.logger = add_logger('dlmanager')
        self.pbar = progress_bar

        for recording in recordings:
            download_link = recording.select_download_link(['hd', 'hq'])
            filename = recording.format_output_filename()
            output_file = filename
            if self.output_dir:
                if recording.show_name:
                    output_tmp = os.path.join(self.output_dir,
                                              recording.show_name)
                    output_file = os.path.join(output_tmp, filename)
                else:
                    output_file = os.path.join(self.output_dir, filename)
            else:
                if recording.show_name:
                    output_file = os.path.join(recording.show_name, filename)

            out_dir = os.path.dirname(output_file)
            check_dir(str(out_dir))

            if recording.information:
                info_file = os.path.splitext(output_file)[0] + ".txt"
                recording.write_information_file(info_file)
                nfo_file = os.path.splitext(output_file)[0] + ".nfo"
                recording.write_kodi_nfo(nfo_file, output_file)

            downloader = fileDownloader.DownloadFile(
                download_link, output_file, progress_bar=self.pbar)
            self.downloads.append(downloader)

    def start(self):
        for downloader in self.downloads:
            if os.path.isfile(downloader.localFileName):
                self.__resume__(downloader)
            else:
                self.logger.info('Downloading: %s' % downloader.url)
                tmp_file = downloader.localFileName + ".download"
                with open(tmp_file, 'w'):
                    os.utime(tmp_file, None)
                downloader.download()
                os.remove(tmp_file)

    def __resume__(self, downloader):

        tmp_file = downloader.localFileName + ".download"

        if (os.path.isfile(tmp_file)):
            self.logger.debug('Resuming download: %s' % downloader.url)
            try:
                downloader.resume()
                os.remove(tmp_file)
            except HTTPError:
                self.logger.debug(
                    "Can't resume. File already finished downloading")
        else:
            self.logger.debug("File already finished downloading: %s" %
                              os.path.basename(downloader.localFileName))
