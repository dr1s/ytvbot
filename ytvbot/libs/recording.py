import datetime
import codecs
import os
import textwrap
import logging

class Recording:

    def __init__(   self, url, show_name, links, title=None,
                    information=None, start_date=None,
                    stop_date=None, genre=None,
                    network=None, season=None, episode=None):
        self.url = url
        self.show_name = show_name
        self.links = links
        self.title = title
        self.information = information
        self.start_date = start_date
        self.stop_date = stop_date
        self.genre = genre
        self.network = network
        self.id = url.rsplit('/', 1)[-1]
        self.season = season
        self.episode = episode

        logger = logging.getLogger('recording')
        logger.setLevel(logging.INFO)
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        ch.setFormatter(formatter)
        logger.addHandler(ch)
        self.logger = logger

    def dict(self):

        recording_list = {}

        recording_list[u'show_name'] = self.show_name
        recording_list[u'url'] = self.url
        recording_list[u'links'] = self.links
        recording_list[u'start_date'] = unicode(
            self.start_date.strftime('%Y-%m-%d:%H:%M'))
        recording_list[u'stop_date'] = unicode(
            self.stop_date.strftime('%Y-%m-%d:%H:%M'))
        recording_list[u'genre'] = self.genre
        recording_list[u'network'] = self.network
        recording_list[u'information'] = self.information
        recording_list[u'season'] = self.season
        recording_list[u'episode'] = self.episode
        recording_list[u'title'] = self.title

        return recording_list


    def list(self, fields=[ 'id', 'show_name', 'title',
                            'start_time', 'end_time']):

        rec_list = []
        start_date = self.start_date.strftime('%Y-%m-%d')
        start_time = self.start_date.strftime('%H:%M')
        end_time = self.start_date.strftime('%H:%M')

        for i in fields:
            if i == 'name':
                rec_list.append(self.show_name)
            elif i == 'id':
                rec_list.append(self.id)
            elif i == 'url':
                rec_list.append(self.url)
            elif i == 'links':
                rec_list.append(self.links)
            elif i == 'date':
                rec_list.append(start_date)
            elif i == 'start_time':
                rec_list.append(start_time)
            elif i == 'end_time':
                rec_list.append(end_time)
            elif i == 'genre':
                rec_list.append(self.genre)
            elif i == 'network':
                rec_list.append(self.network)
            elif i == 'information':
                rec_list.append(self.information)
            elif i == 'title':
                rec_list.append(self.title)
            elif i == 'episode':
                rec_list.append(self.episode)
            elif i == 'season':
                rec_list.append(self.season)

        return rec_list


    def write_information_file(self, output_file):

        date = self.start_date.strftime('%d.%m.%Y')
        start_time = self.start_date.strftime('%H:%M')
        end_time = self.stop_date.strftime('%H:%M')
        if not os.path.isfile(output_file):
            with codecs.open(output_file, "w", "utf-8") as f:
                f.write("%s\n" % self.show_name)
                if self.title:
                    f.write("%s" % self.title)
                if self.season:
                    f.write("Staffel: %s" % self.season)
                if self.episode:
                    f.write("Episode: %s" % self.episode)
                if self.episode or self.season:
                    f.write("\n")
                f.write("\n")
                f.write("Sender: %s\n" % self.network)
                f.write("Sendezeit: %s %s - %s\n" %
                    (date, start_time, end_time))
                f.write("Genre: %s\n\n" % self.genre)

                for i in self.information:
                    f.write("%s\n\n" % textwrap.fill(i))
        else:
            self.logger.debug("information file already exists: %s" % output_file)
