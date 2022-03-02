#! python3


from bs4 import BeautifulSoup
import requests
from curriculum import Course, Curriculum
# import pandas as pd


# A scraper for the case western MS Data Science program webpage


def main():
    prereq_string = "Prereq:"
    punc = '''!()-[]{};:'"\,<>./?@#$%^&*_~'''  # noqa: W605
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

    # initiating an empty list for courses
    cw_curriculum = Curriculum("Case Western")

    for course_tag in soup.find_all("div", {"class": "courseblock"}):
        blocktitle_tag = course_tag.find("p", {"class": "courseblocktitle"})\
                           .find("strong")
        subject_code = blocktitle_tag.string.split()[0]
        # apparently some universitys have letters in their course codes best
        # to leave as string
        course_code = blocktitle_tag.string.split()[1][:-1]
        course_title = blocktitle_tag.string.split('.')[1][2:]
        blockdesc_tag = course_tag.find("p", {"class": "courseblockdesc"})
        new_course = Course(subject_code, course_code,
                            course_title, blockdesc_tag.contents[0]
                            .split("Offered as")[0].split("Prereq:")[0])
        cw_curriculum.add_course(new_course)
        # print(new_course)
        temp = ""
        for item in blockdesc_tag.contents:
            try:
                for z in item.string.split("\n"):
                    temp += z
            except Exception:
                pass
            finally:
                pass

        index = temp.find(prereq_string)
        if index > -1:
            print(new_course)
            temp = temp[index+len(prereq_string)+1:]
            for ele in temp:
                if ele in punc:
                    temp = temp.replace(ele, "")
            print("\t" + temp)
    cw_curriculum.print_all()
    file.close()


if __name__ == "__main__":
    main()
