#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import time
import simplejson as json
import logging
import requests
from glob import glob
from datetime import datetime
import pyfscache


def dt_now():
    return str(datetime.now())[:19].replace(" ", "_").replace(":", ".")


def make_cache_it(
    folder="./cache", years=0, months=0, weeks=0, days=10, hours=0, minutes=0, seconds=0
):
    _cache_it = pyfscache.FSCache(
        folder,
        years=years,
        months=months,
        weeks=weeks,
        days=days,
        hours=hours,
        minutes=minutes,
        seconds=seconds,
    )
    return _cache_it


cache_it = make_cache_it()


def make_get_page(sleep_time=0, encoding="utf-8"):
    def _get_page(url):
        r = requests.get(url)
        r.encoding = encoding
        if sleep_time:
            time.sleep(sleep_time)
        return r.text

    return _get_page


def get_current_grab_folder_name(domain, dt=None):
    if dt is None:
        dt = str(datetime.now())[:19].replace(" ", "_").replace(":", ".")
    return "./{domain}/{dt}".format(domain=domain, dt=dt)


def get_grab_folders_list(domain):
    return sorted(filter(os.path.isdir, glob("./{domain}/*".format(domain=domain))))


def get_last_grab_folder_name(domain):
    return get_grab_folders_list(domain)[-1]


def make_dirs_for_file(filename):
    folder = os.path.dirname(filename)
    if not os.path.exists(folder):
        os.makedirs(folder)


def make_dumper(domain, folder=None):
    if folder is None:
        folder_pattern = ""
    else:
        folder_pattern = "/{}".format(folder)

    def _dump(data, file_name, encoding="UTF-8"):
        if domain in file_name:
            full_file_name = file_name
        else:
            full_file_name = "{}{}/{}".format(
                get_last_grab_folder_name(domain), folder_pattern, file_name
            )
        make_dirs_for_file(full_file_name)
        with open(full_file_name, "w") as dump_file:
            if encoding is None:
                dump_file.write(data)
            else:
                dump_file.write(data.encode(encoding))

    return _dump


def make_converter_to_json(domain, folder):
    files_iter = make_files_iter(domain, folder)
    dumper = make_dumper(domain)

    def _convert_to_json(parser):
        for html_file_name in files_iter("*.html"):
            parsing_result = parser(html_file_name)
            json_file_name = html_file_name.replace("html", "json")
            dumper(
                json.dumps(parsing_result, indent=4).decode("raw-unicode-escape"),
                json_file_name,
            )
            logging.info("{} - [done]".format(json_file_name))

    return _convert_to_json


def make_files_iter(domain, folder):
    def _files_iter(mask):
        files = glob("{}/{}/{}".format(get_last_grab_folder_name(domain), folder, mask))
        for f in files:
            yield f

    return _files_iter


def load_json_files_iter(files):
    for json_loads in json_loads_iter(load_files_iter(files)):
        yield json_loads


def load_files_iter(files):
    for file_name in files:
        with open(file_name) as file_object:
            yield file_object.read()


def json_loads_iter(raw_data_iter):
    for raw_data in raw_data_iter:
        yield json.loads(raw_data)


def lists_iter(lists):
    for item in lists:
        for subitem in item:
            yield subitem
