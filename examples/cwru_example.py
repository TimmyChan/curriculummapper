#! python3


from time import perf_counter
import re
from curriculummapper import Course, Curriculum


def main():
    '''
    An example scraper for the case western MS Data Science program webpage
    '''
    # initiating an empty curriculum object
    true_start_time = perf_counter()
    school_name = "Case Western"
    degree_name = "MS in Data Science"
    curriculum = Curriculum(school_name, degree_name, "CSDS",
                            colored_subjects=["STAT", "MATH"])
    url_list = ["https://bulletin.case.edu/schoolofengineering/compdatasci/",   # COMPSCI  # noqa: E501
                "https://bulletin.case.edu/collegeofartsandsciences/mathematics/",  # MATH # noqa: E501
                "https://bulletin.case.edu/schoolofengineering/eleccompsyseng/",  # COMPSCI # noqa: E501
                "https://bulletin.case.edu/course-descriptions/dsci/",
                "https://bulletin.case.edu/course-descriptions/stat/"
                ]
    for URL in url_list:
        print("Politely checking: %s..." % URL)
        soup = curriculum.get_soup(URL)
        # Getting prereq names from course tables first
        print("Scraping tables...")
        for table_tag in soup.find_all("table", {"class": "sc_courselist"}):
            for row_tag in table_tag.findChildren("tr"):
                cells = row_tag.findChildren("td")
                try:
                    course_title = str(cells[1].string)
                    course_id = curriculum.course_id_list_from_string(
                        str(row_tag.findChildren("a")[0].string))[0]
                    '''
                    subject_code, course_code = course_id_to_list(course_id)
                    curriculum.add_course(Course(subject_code,
                                                      course_code,
                                                      course_title))
                    '''
                    curriculum.add_courses_from_string(course_id)
                    curriculum.course_dict[course_id].append_course_title(
                        course_title)
                except Exception:
                    pass

        # inpecting the source reveals that each course is neatly in div blocks
        # courseblock class. Iterating through each courseblock
        print("Scraping courseblocks...")
        for course_tag in soup.find_all("div", {"class": "courseblock"}):
            # then the title contains the "AAAA 000?. COURSE TITLE. n Units."
            blocktitle_tag = course_tag.find("p", {"class": "courseblocktitle"}).find("strong")  # noqa: E501
            # convert the content to UNICODE to minimize memory use
            blocktitle_string = str(blocktitle_tag.string)
            # print(blocktitle_string)
            # search for the first instance in blocktitle_string
            # that matches course_search
            course_id = curriculum.course_id_list_from_string(
                blocktitle_string)[0]
            subject_code, course_code = curriculum.course_id_to_list(
                course_id)
            # apparently some universitys have letters in their course codes
            # so leave as string. Remove the spaces and periods tho.
            # course title
            title_search = re.compile(r"(?<=\s\s)([^!]*)(?=\.\s\s)")
            title_match = re.findall(title_search, blocktitle_string)
            course_title = title_match[0]

            # Now extracting course desc
            blockdesc_tag = course_tag.find("p", {"class": "courseblockdesc"})
            course_description = blockdesc_tag.contents[0].split("Offered as")[0]\
                                                          .split("Prereq:")[0]\
                                                          .split("Recommended preparation:")[0]  # noqa: E501
            # Take everything in blockdesc, stitch into one long string
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
                    prereqs = curriculum.course_list_from_string(
                        prereq_match[0])
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
                    aliases = curriculum.course_id_list_from_string(
                        str(alias_match[0]))
                except IndexError:
                    pass
            curriculum.add_course(Course(subject_code, course_code,
                                         course_title, course_description,
                                         prereqs, aliases))

    curriculum.print_all()
    true_finish_time = perf_counter()
    print("\t\tTOTAL TIME: %.6f" % (true_finish_time - true_start_time))


if __name__ == "__main__":
    main()
