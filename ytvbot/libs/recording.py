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

    def get_attribute(self, name, sep=None):

        if name == 'name':
            return self.show_name
        elif name == 'id':
            return self.id
        elif name == 'url':
            return self.url
        elif name == 'links':
            return self.links
        elif name == 'date':
            if not sep:
                sep = '-'
            year = self.start_date.strftime('%Y')
            month = self.start_date.strftime('%m')
            day = self.start_date.strftime('%d')
            return "%s%s%s%s%s" %(year, sep, month, sep, day)
        elif name == 'start_time':
            if not sep:
                sep = ':'
            hour = self.start_date.strftime('%H')
            minute = self.start_date.strftime('%M')
            return "%s%s%s" % (hour, sep, minute)
        elif name == 'end_time':
            if not sep:
                sep = ':'
            hour = self.start_date.strftime('%H')
            minute = self.start_date.strftime('%M')
            return "%s%s%s" % (hour, sep, minute)
        elif name == 'genre':
            return self.genre
        elif name == 'network':
            return self.network
        elif name == 'information':
            return self.information
        elif name == 'title':
            return self.title
        elif name == 'episode':
            return self.episode
        elif name == 'season':
            return self.season
        else:
            return None


    def list(self, fields="name"):

        rec_list = []
        if type(fields) == list:
            for i in fields:
                value = self.get_attribute(i)
                rec_list.append(value)
        else:
            value = self.get_attribute(i)
            rec_list.append(value)

        return rec_list


    def write_information_file(self, output_file):

        date = self.get_attribute('date')
        start_time = self.get_attribute('start_time')
        end_time = self.get_attribute('end_time')

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


    def format_output_filename(self):
        fname = ("%s-%s-%s-%s-%s.mp4" % (self.show_name, self.title,
                self.get_attribute('date', '_'),
                self.get_attribute('start_time','_'),
                self.network))

        return fname
