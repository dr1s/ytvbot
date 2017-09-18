# ytvbot

[![Codacy Badge](https://api.codacy.com/project/badge/Grade/c19662d802b14473b06a6db8b97f3950)](https://www.codacy.com/app/dr1s/ytvbot?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=dr1s/ytvbot&amp;utm_campaign=Badge_Grade)

Download recordings form youtv.de

## Dependencies
* selenium
* pyvirtualdisplay
* fileDownloader.py
* psutil
* geckodriver (https://github.com/mozilla/geckodriver/releases)
* firefox
* Xvfb
* xauth

## Install
* Install geckodriver from https://github.com/mozilla/geckodriver/releases
* Install firefox
    `sudo apt install firefox`
    `brew install firefox`
    etc.
* Install Xvfb and xauth for headless mode on Linux
    `sudo apt install Xvfb xauth`
* `pip2 install git+https://github.com/dr1s/ytvbot.git@master`

## Usage
    ytvbot --help

    usage: ytvbot [arguments]
    -u | --user [email]: email adress of the account
    -p | --password [password]: password ouf the account
    -c | --config-dir [config-dir]: path to configuration directory
    -o | --output [output_dir]: output directory
    -h | --help: shows this message
    -n | --no-download: Don't download anything
    -l | --links [output_file]: Save links in this file
    -# | --progress: show progress bar when downloading files
    -s | --search [show_name]: only look for show_name
    -j | --json [output_file]: save results as json file


## Thanks

* bantonj for fileDownloader.py (https://github.com/bantonj/fileDownloader)
