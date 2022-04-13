#! python3
''' a simple example script for scrapping a bulletin '''

import json
import validators
import requests
import pprint
import os
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from pathlib import Path


def bulletincrawler(school_short_name="SCHOOL",
                    URL=None,
                    data_dir="canned_soup/bulletin_data/",
                    container_tag_type='div',
                    container_tag_attrs_dict={"class": "page_content"}):
    ''' saves a copy of the html to not overping '''
    data_dir_path = Path(data_dir)

    # Empty string
    bulletin_URL = ""
    if URL is not None:
        bulletin_URL = URL
    else:
        while True:
            try:
                temp = input("Enter bulletin URL:")
                if validators.url(temp):
                    bulletin_URL = temp
                    break
                else:
                    raise ValueError('Enter a valid URL')
            except Exception as e:
                print(e)

    filename = school_short_name + "_bulletin" + ".html"
    # print("Trying %s/%s" % (data_dir, filename))
    try:
        os.makedirs(data_dir_path)
    except Exception:
        # only here if already have the directory
        # do nothing safely
        pass
    try:
        # try to open html, where we cache the soup
        print("Reading from '%s'..." %
              os.path.join(data_dir_path, filename))
        with open(os.path.join(data_dir_path, filename), "r") as file:
            soup = BeautifulSoup(file, "lxml")
    except Exception:
        try:
            print("\t\tPinging Server")
            res = requests.get(bulletin_URL)
            # using lxml because of bs4 doc
            soup = BeautifulSoup(res.content, "lxml")
            print("Writing to '%s'..." %
                  os.path.join(data_dir_path, filename))
            with open(os.path.join(data_dir_path, filename), 'w+') as file:
                file.write(str(soup))
        except Exception:
            print("Why are you even here?")
            print(str(Exception))
            soup = BeautifulSoup(requests.get(bulletin_URL), "lxml")

    url_list = []
    for tag in soup.find(container_tag_type,
                         attrs=container_tag_attrs_dict).find_all('a', href=True):  # noqa: E501
        url = tag['href']
        full_url = urljoin(bulletin_URL, url)
        if validators.url(full_url) and not url.startswith('#'):
            url_list.append(full_url)
    json_filename = os.path.join(data_dir_path, school_short_name + ".json")
    with open(json_filename, "w+") as file:
        json.dump(url_list, file)
    return soup


if __name__ == "__main__":
    pp = pprint.PrettyPrinter()
    bulletin = "https://bulletin.sfsu.edu/courses/"
    soup = bulletincrawler(school_short_name="SFSU", URL=bulletin)
