#! python3

import re
import requests
import unicodedata
from bs4 import BeautifulSoup
from curriculum import Course, Curriculum
# import pandas as pd

# RegEx: course id is four capitals with space then three numbers
# with a possible letter after the numbers then stop with a non-word
course_search = re.compile(r"([A-Z]{4}\s\d{3}\w*)\b")
# get the subject code which is always the first four capitals
# preceeding a space, 3 digits and a possible word character
subject_search = re.compile(r"([A-Z]{4})(?=\s\d{3}\w*)")
# get the course_code which is the letters following the digits
code_search = re.compile(r"(?<=[A-Z]{4}\s)(\d{3}\w*)")


def course_id_to_list(course_id):
    # search for the first instance that matches subject_search
    subject_match = re.findall(subject_search, course_id)
    subject_code = subject_match[0]
    # search for the first instance that matches code_search
    code_match = re.findall(code_search, course_id)
    course_code = code_match[0]
    return (subject_code, course_code)


def main():
    '''A scraper for the case western MS Data Science program webpage'''
    prereq_string = "Prereq: "

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

    # initiating an empty curriculum object
    cw_curriculum = Curriculum("Case Western", "MS in Data Science")

    # inpecting the source reveals that each course is neatly in div blocks of
    # courseblock class. Iterating through each courseblock
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
                                               .split("Prereq:")[0]

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
        # use this split to take what comes after
        temp = glued_string.split("Prereq: ")
        # blink list to hold Course objects
        prereqs = []
        if len(temp) > 1:
            # if the split created a list longer than 1, then there's prereqs
            prereq_string = temp[1]
            # find every instance of a course in the remaining string
            temp = re.findall(course_search, prereq_string)
            for t in temp:
                # FOR SOME REASON \xa0 started appearing so clean it...
                norm_t = unicodedata.normalize('NFKD', t)
                # getting the subject and code to initiate Course object
                prereq_subject, prereq_code = course_id_to_list(norm_t)
                # appending the course object for each prereq
                prereqs.append(Course(prereq_subject, prereq_code))

        new_course = Course(subject_code, course_code,
                            course_title, course_desc, prereqs)
        cw_curriculum.add_course(new_course)
        # print(new_course)

    cw_curriculum.print_all()
    file.close()


if __name__ == "__main__":
    main()
