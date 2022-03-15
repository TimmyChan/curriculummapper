#! python3


import re
import unicodedata
from curriculum import Course, Curriculum


def main():
    '''
    An example scraper for the case western MS Data Science program webpage
    '''
    # initiating an empty curriculum object
    school_name = "San Francisco State University"
    degree_name = "MA in Mathematics"
    curriculum = Curriculum(school_name, degree_name, "MATH",
                            colored_subjects=["CSC"],
                            course_search=r"([A-Z]{3}[A-Z]*\s\d{3}\w*)\b",
                            subject_search=r"([A-Z]{3}[A-Z]*)")
    url_list = ["https://bulletin.sfsu.edu/courses/math/",
                "https://bulletin.sfsu.edu/courses/csc/"]
    for URL in url_list:
        print("Connecting: %s..." % URL)
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
            split_blocktitle_list = blocktitle_string.split(" ", 3)
            subject_code = split_blocktitle_list[0]
            course_code = split_blocktitle_list[1]
            course_title = split_blocktitle_list[-1].split("(")[0]
            # print("Course_ID: %s %s \nCourse Title: %s" %
            #       (subject_code, course_code, course_title.split("(")[0]))
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
                prereqs = \
                    [Course(p.split()[0], p.split()[1]) for p in prereqs]
            except Exception:
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

            # print(aliases)
            curriculum.add_course(Course(subject_code, course_code,
                                         course_title, course_description,
                                         prereqs, aliases))

    curriculum.print_all()


if __name__ == "__main__":
    main()
