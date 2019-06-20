import textwrap
import codecs
import os

from prettytable import PrettyTable


def __write_data_to_file__(item, f):

    date = item.get_attribute("date")
    start_time = item.get_attribute("start_time")
    end_time = item.get_attribute("end_time")

    f.write("%s\n" % item.show_name)
    if item.title:
        f.write("%s" % item.title)
    if item.season:
        f.write("Staffel: %s" % item.season)
    if item.episode:
        f.write("Episode: %s" % item.episode)
    if item.episode or item.season:
        f.write("\n")

    f.write("\n")
    f.write("Sender: %s\n" % item.network)
    f.write("Sendezeit: %s %s - %s\n" % (date, start_time, end_time))
    f.write("Genre: %s\n\n" % item.genre)

    for i in item.information:
        f.write("%s\n\n" % textwrap.fill(i))


def write_information_file(item, output_file):

    if not os.path.isfile(output_file):
        with codecs.open(output_file, "w", "utf-8") as f:
            __write_data_to_file__(item, f)
    else:
        item.logger.debug("information file already exists: %s" % output_file)


def print_recordings(recordings, fields="id"):
    pt = PrettyTable(fields)
    if isinstance(fields, list):
        for recording in recordings:
            pt.add_row(recording.list(fields))
    else:
        pt.add_row(recording.list(fields))
    print(pt)


def write_links_to_file(recordings, output):

    logger.info("Wrtiting links to file: %s" % output)
    for recording in recordings:
        download_link = select_download_link(recording)
        if download_link:
            if download_link not in open(output).read():
                recroding.logger.debug(
                    "Link not found in file adding: %s" % download_link
                )
                with open(output, "a") as f:
                    f.write("%s\n" % download_link)
            else:
                recording.logger.debug("Link already found in file %s" % download_link)
