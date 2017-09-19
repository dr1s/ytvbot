from log import add_logger
import exporter

class Recording(object):

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

        self.logger = add_logger('recording %s' % self.id)


    def get_start_time(self, sep=':'):
        hour = self.start_date.strftime('%H')
        minute = self.start_date.strftime('%M')
        time = "%s%s%s" %(hour, sep, minute)

        return time


    def get_end_time(self, sep=':'):
        hour = self.stop_date.strftime('%H')
        minute = self.stop_date.strftime('%M')
        time = "%s%s%s" %(hour, sep, minute)

        return time


    def get_date(self, sep='-'):
        year = self.start_date.strftime('%Y')
        month = self.start_date.strftime('%m')
        day = self.start_date.strftime('%d')
        time = "%s%s%s%s%s" % (year, sep, month, sep, day)

        return time


    def get_attribute(self, name, sep=None):

        if name == 'date':
            return self.get_date()
        elif name == 'start_time':
            return self.get_start_time()
        elif name == 'end_time':
            return self.get_end_time()
        else:
            attr = getattr(self, name, None)
            return attr

    def dict(self):
        rec_dict = self.__dict__.copy()
        rec_dict['start_time'] = self.get_start_time()
        rec_dict['end_time'] = self.get_end_time()
        rec_dict['date'] = self.get_date()
        del rec_dict['stop_date']
        del rec_dict['start_date']
        del rec_dict['logger']
        return rec_dict

    def list(self, fields="name"):

        rec_list = []
        if isinstance(fields, list):
            for i in fields:
                value = self.get_attribute(i)
                rec_list.append(value)
        else:
            value = self.get_attribute(i)
            rec_list.append(value)

        return rec_list


    def write_information_file(self, output_file):
        exporter.write_information_file(self, output_file)


    def format_output_filename(self):
        fname = ("%s-%s-%s-%s-%s.mp4" % (self.show_name, self.title,
                self.get_attribute('date', '_'),
                self.get_attribute('start_time','_'),
                self.network))

        return fname
