#! python3


from time import perf_counter
import re
import unicodedata
from curriculummapper import Course, Curriculum


def main():
    '''
    An example scraper for the case western MS Data Science program webpage
    '''
    # initiating an empty curriculum object
    true_start_time = perf_counter()
    school_name = "University of California Irvine"
    degree_name = "BA in Business Administration"
    curriculum = Curriculum(school_name, degree_name, "MGMT",
                            colored_subjects=["MGMT","ECON","STATS"],
                            course_search=r"([A-Z]{3}[A-Z]*\s\d\d*[A-Z]*)\b", ##########
                            subject_search=r"([A-Z]{3}[A-Z]*)")
    url_list = ["https://catalogue.uci.edu/allcourses/mgmt/",
                "https://catalogue.uci.edu/allcourses/econ/",
                "https://catalogue.uci.edu/allcourses/stats/",
                "https://catalogue.uci.edu/allcourses/math/"]
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
            split_blocktitle_list = blocktitle_string.split(" ", 3)
            subject_code = split_blocktitle_list[0]
            course_code = split_blocktitle_list[1].split(".")[0]
            course_title = split_blocktitle_list[-1].split(".")[0]
            # print("Course_ID: %s %s \nCourse Title: %s" %
            #      (subject_code, course_code, course_title.split("(")[0]))

            # grab the coruse describ tag
            courseblockdesc_tag = \
                course_tag.find("div", {"class": "courseblockdesc"})
            # grab all the paragraph tags inside each course block description
            paragraph_tags = courseblockdesc_tag.find_all("p")
            # first paragraph is the course description
            course_description = paragraph_tags[0].text
            # print(course_description)
            prereqs = []
            aliases = []
            for tag in paragraph_tags:
                # print(tag.text)
                if re.search("Prereq", tag.text):
                    prereqs += curriculum.course_id_list_from_string(tag.text)
                if re.search("Overlaps", tag.text):
                    aliases += curriculum.course_id_list_from_string(tag.text)

            prereqs = [curriculum.course_list_from_string(p)[0] for p in prereqs if p not in aliases]
            # print(prereqs)

            # print(aliases)
            curriculum.add_course(Course(subject_code, course_code,
                                         course_title, course_description,
                                         prereqs, aliases))

    curriculum.print_all()
    true_finish_time = perf_counter()
    print("\t\tTOTAL TIME: %.6f" % (true_finish_time - true_start_time))


if __name__ == "__main__":
    main()
