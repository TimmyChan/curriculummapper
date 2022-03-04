#! python3

import re
import requests
import unicodedata
from bs4 import BeautifulSoup
from curriculum import Course, Curriculum
# import pandas as pd

# RegEx: course id is four capitals with space then three numbers
# with a possible letter after the numbers then stop with a non-word
course_search = re.compile(r"([A-Z]{4}\s\d{3}\w*)")
# get the subject code which is always the first four capitals
# preceeding a space, 3 digits and a possible word character
subject_search = re.compile(r"([A-Z]{4})(?=\s\d{3}\w*)")
# get the course_code which is the letters following the digits
code_search = re.compile(r"(?<=[A-Z]{4}\s)(\d{3}\w*)")


def course_id_to_list(course_id):
    ''' breaks course_id into subject and course codes '''
    return (re.findall(subject_search, course_id)[0],
            re.findall(code_search, course_id)[0])


def course_list_from_string(somewords):
    ''' extracts list of courses from a string'''
    course_list = []
    course_ids = re.findall(course_search, somewords)
    for course_id in course_ids:
        # FOR SOME REASON \xa0 started appearing so clean it...
        norm_id = unicodedata.normalize('NFKD', course_id)
        # getting the subject and code to initiate Course object
        subject_code, course_code = course_id_to_list(norm_id)
        course_list.append(Course(subject_code, course_code))
    return course_list


def main():
    '''A scraper for the case western MS Data Science program webpage'''
    # initiating an empty curriculum object
    cw_curriculum = Curriculum("Case Western", "MS in Data Science")
    try:
        # try to open output.html, where we cache the soup
        with open("case_western.html", "r") as file:
            soup = BeautifulSoup(file, "lxml")
    except Exception:
        res = requests.get("https://bulletin.case.edu/schoolofengineering/compdatasci/")  # noqa: E501
        # using lxml because of bs4 doc
        soup = BeautifulSoup(res.content, "lxml")
        with open("case_western.html", "w") as file:
            file.write(str(soup))

    # Getting prereq names from course tables first
    print("Scraping tables...")
    for table_tag in soup.find_all("table", {"class": "sc_courselist"}):
        for row_tag in table_tag.findChildren("tr"):
            cells = row_tag.findChildren("td")
            try:
                course_id = \
                    re.findall(course_search,
                               str(row_tag.findChildren("a")[0].string))[0]
                subject_code, course_code = course_id_to_list(course_id)
                course_title = str(cells[1].string)
                cw_curriculum.add_course(Course(subject_code,
                                                course_code,
                                                course_title))
            except Exception:
                pass

    # inpecting the source reveals that each course is neatly in div blocks of
    # courseblock class. Iterating through each courseblock
    print("Scraping courseblocks...")
    for course_tag in soup.find_all("div", {"class": "courseblock"}):
        # then the title contains the "AAAA 000?. COURSE TITLE. n Units."
        blocktitle_tag = course_tag.find("p", {"class": "courseblocktitle"}).find("strong")  # noqa: E501
        # convert the content to UNICODE to minimize memory use
        blocktitle_string = str(blocktitle_tag.string)
        # search for the first instance in blocktitle_string
        # that matches course_search
        course_match = re.findall(course_search, blocktitle_string)
        course_id = course_match[0]
        subject_code, course_code = course_id_to_list(course_id)
        # apparently some universitys have letters in their course codes best
        # to leave as string. Remove the spaces and periods tho.
        # course title
        title_search = re.compile(r"(?<=\s\s)([^!?]*)(?=\.\s\s)")
        title_match = re.findall(title_search, blocktitle_string)
        course_title = title_match[0]

        # Now Playing with the description part
        blockdesc_tag = course_tag.find("p", {"class": "courseblockdesc"})
        course_desc = blockdesc_tag.contents[0].split("Offered as")[0]\
                                               .split("Prereq:")[0]\
                                               .split("Recommended preparation:")[0]  # noqa: E501

        # Take everything in blockdesc, turn tem into strings and glue em up
        glued_string = ""
        for item in blockdesc_tag.contents:
            try:
                for z in item.string.split("\n"):
                    glued_string += z
            except Exception:
                pass
            finally:
                pass
        # Looking for the sentense that starts with Prereq: or preparation
        # print(glued_string)
        prereq_match = re.findall(r"(?<=Prereq: |ration: )([^!?.]*)",
                                  glued_string)

        # blink list to hold Course objects
        prereqs = []
        if prereq_match is not None:
            try:
                # find every instance of a course in the remaining string
                prereqs = course_list_from_string(prereq_match[0])
            except IndexError:
                # print("No prereqs.")
                pass
        # Looking for the sentense that starts with "Offered as"
        alias_match = re.findall(r"(?<=Offered as )([^!?.]*)",
                                 glued_string)
        aliases = []
        if alias_match is not None:
            try:
                # find every instance of a course in the remaining string
                aliases = course_list_from_string(alias_match[0])
            except IndexError:
                pass

        cw_curriculum.add_course(Course(subject_code, course_code,
                                        course_title, course_desc,
                                        prereqs, aliases))
        # print(new_course)

    cw_curriculum.print_all()
    cw_curriculum.generate_graph()
    file.close()


if __name__ == "__main__":
    main()
