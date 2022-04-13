#! python3


from time import perf_counter
# from pathlib import Path
import json
import re
import unicodedata
from curriculummapper import Course, Curriculum


def main():
    '''
    An example scraper for the case western MS Data Science program webpage
    '''
    try:
        with open("canned_soup/bulletin_data/SFSU.json") as file:
            url_list = json.load(file)
            for url in url_list:
                print(url)
    except Exception as e:
        print(e)
        url_list = ["https://bulletin.sfsu.edu/courses/math/",
                    "https://bulletin.sfsu.edu/courses/csc/"]
    # initiating an empty curriculum object
    true_start_time = perf_counter()
    school_name = "San Francisco State University"
    degree_name = "Full Bulletin"
    curriculum = Curriculum(school_name, degree_name, "MATH",
                            colored_subjects=["CSC"],
                            course_search=r"([A-Z]+\s*[A-Z]*\s\d{3}\w*)\s",
                            subject_search=r"([A-Z]+\s*[A-Z]*)\s\d{3}")
    for URL in url_list:
        print("Politely Checking: %s..." % URL)
        soup = curriculum.get_soup(URL)
        # inpecting the source reveals that each course is neatly in div blocks
        # courseblock class. Iterating through each courseblock
        print("Scraping courseblocks...")
        # This was the same label for case western...
        for course_tag in soup.find_all("div", {"class": "courseblock"}):
            # Grabbing the bolded titled bit
            blocktitle_tag = course_tag.find("p", {"class": "courseblocktitle"}).find("strong")  # noqa: E501
            # convert the content to UNICODE
            blocktitle_string = unicodedata.normalize(
                'NFKD', str(blocktitle_tag.string))
            course_id = curriculum.course_id_list_from_string(blocktitle_string)[0]  # noqa: E501
            subject_code, course_code = curriculum.course_id_to_list(course_id)
            course_title = re.findall(r"\d\s(.*)\s\(", blocktitle_string)
            # split_blocktitle_list = blocktitle_string.split(" ", 3)
            # subject_code = split_blocktitle_list[0]
            # course_code = split_blocktitle_list[1]
            # course_title = split_blocktitle_list[-1].split("(")[0]
            prereqs = []
            print("subject_code: %s\t\tcourse_code: %s \ncourse_title: %s" %
                  (subject_code, course_code, course_title))
            try:
                courseblockextra_tag = \
                    course_tag.find("p", {"class": "courseblockextra"})
            # For some reason the course description is the text behind the
            # courseblockextra outside of any tags >.>
                course_description = courseblockextra_tag.next_sibling
                prereqs = \
                    courseblockextra_tag.find_all("a",
                                                  {"class": "bubblelink code"})
                # normalize the strings
                prereqs = \
                    [unicodedata.normalize('NFKD', p.string) for p in prereqs]
            except Exception:
                pass
            courseblockdesc = \
                course_tag.find("p", {"class": "courseblockdesc"})
            course_description = \
                unicodedata.normalize('NFKD', str(courseblockdesc.string))

            c = [child for child in course_tag.children]
            aliases = []
            if re.search(r"(paired\scourse)", str(c[-1])):
                # print("\tALIAS FOUND")
                # print(c[-2].string)
                # print(c[-4].string)
                aliases.append(unicodedata.normalize('NFKD',
                                                     str(c[-2].string)))
                aliases.append(unicodedata.normalize('NFKD',
                                                     str(c[-4].string)))
            prereqs = [p for p in prereqs if p not in aliases]
            prereqs_string = '. '.join(prereqs)
            prereqs = curriculum.course_list_from_string(prereqs_string)
            # print(aliases)
            curriculum.add_course(Course(subject_code, course_code,
                                         course_title, course_description,
                                         prereqs, aliases))

    curriculum.print_all()
    true_finish_time = perf_counter()
    print("\t\tTOTAL TIME: %.6f" % (true_finish_time - true_start_time))


if __name__ == "__main__":
    main()
