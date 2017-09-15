import datetime


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


    def list(self):

        start_date = self.start_date.strftime('%Y-%m-%d')
        start_time = self.start_date.strftime('%H:%M')
        stop_time = self.stop_date.strftime('%H:%M')

        rec_list = []
        rec_list.append(self.id)
        rec_list.append(self.show_name)
        rec_list.append(self.title)
        rec_list.append(start_date)
        rec_list.append(start_time)
        rec_list.append(stop_time)
        rec_list.append(self.network)
        rec_list.append(self.genre)
        rec_list.append(self.season)
        rec_list.append(self.episode)

        return rec_list
