import json
import datetime
import codecs
from scraper import Recording

def import_dict_recording(rec):
    start_date = datetime.datetime.strptime(
        rec['start_date'], "%Y-%m-%d:%H:%M")
    stop_date = datetime.datetime.strptime(
        rec['stop_date'], "%Y-%m-%d:%H:%M")
    recording = Recording(rec['url'], rec['show_name'], rec['links'],
        rec['title'], rec['information'], start_date, stop_date,
        rec['genre'], rec['network'],
        rec['episode'], rec['season'])

    return recording

def import_json_file(json_file):
    with codecs.open(json_file, "r", "utf-8") as f:
        rec_list = json.load(f)
    recordings = []
    for rec in rec_list:
        recordings.append(import_dict_recording(rec))

    return recordings
