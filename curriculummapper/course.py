#! python3

import re

'''
course_id: r"([A-Z]+\s*[A-Z]+\s\d+\w*\b)"  # noqa: W605
subject_code: r"([A-Z]+\s*[A-Z]+)(?=\s\d+\w*\b)" # noqa: W605
course_code: r"(?<=[A-Z]+\s*[A-Z]+\s)(\d+\w*)(?=\b)" # noqa: W605
'''


class Course:
    '''Course object to handle course data'''
    def __init__(self, subject_code="NONE", course_code="0",
                 course_title="",
                 course_description="",
                 prerequisites=None, alias_list=None,
                 course_id_search=r"([A-Z]+\s*[A-Z]+\s\d+\w*)(?=\b)",
                 subject_code_search=r"([A-Z]+\s*[A-Z]+)(?=\s\d+\w*)(?=\b)",
                 course_code_search=r"(?<=[A-Z]+\s*[A-Z]+\s)(\d+\w*)(?=\b)"):
        ''' * subject_code (string): Example "CSDS"
            * course_code (string): Example "498"
            course_key (string) = subject_code + " " + course_code = "CSDS 498"
            * course_title (string)
            * course_description (string)
            * prerequisites SET of string objects # Changed to strings
            * alias_set SET of strings
        '''
        self.subject_code = subject_code
        self.course_code = course_code
        self.course_key = str(subject_code) + " " + str(course_code)
        self.course_title = course_title
        self.course_description = course_description
        self.prerequisites = set()
        self.alias_set = set()

        self.course_id_search = course_id_search
        self.subject_search = subject_code_search
        self.course_code_search = course_code_search

        if prerequisites is None:
            prerequisites = []
        for course in prerequisites:
            self.add_prereq(course)
        if alias_list is None:
            alias_list = []
        else:
            for name in alias_list:
                self.add_alias(name)
        # self.add_alias(self.course_key)

    def __str__(self):
        '''all we need is subject and course code for an identifier'''
        return self.course_key

    def __repr__(self):
        ''' Give stable repr for hash for set operations '''
        return ("Course(%s, %s, %s)" %
                (self.subject_code, self.course_code, self.course_title))

    def __hash__(self):
        ''' Give a hash based on representation '''
        return hash(self.__repr__())

    def __eq__(self, other):
        ''' needed to evaulate equality for set operations '''
        if isinstance(other, Course):
            return ((self.subject_code == other.subject_code) and
                    (self.course_code == other.course_code))
        else:
            return False

    def add_alias(self, course_id):
        ''' adds an alias to the course id '''
        self.alias_set.add(course_id)

    def add_prereq(self, x):
        ''' adds a prereq after confirming it's a Course object '''
        try:
            if isinstance(x, Course):
                self.prerequisites.add(x)
            else:
                raise ValueError
        except ValueError:
            print("Only course objects accepted in the prerequisites list.")
            # just ignore if x is something that isn't a course
            pass

    def get_course_code_int(self):
        ''' used for color maps, strips letters from course_code '''
        if isinstance(self.course_code, int):
            return self.course_code
        else:
            try:
                return int(re.findall(r"(\d+)", str(self.course_code))[0])
            except Exception:
                return int(self.course_code)

    def append_course_title(self, course_title=""):
        ''' add a course_title string if and only if it's longer '''
        if len(course_title) >= len(self.course_title):
            self.course_title = course_title

    def append_course_description(self, course_description=""):
        ''' add course_desc if and only if it's longer '''
        if len(course_description) >= len(self.course_description):
            self.course_description = course_description

    def append_prerequisites(self, prerequisites=[]):
        ''' add prerequisits indivdually '''
        if len(prerequisites) > 0:
            for prereq in prerequisites:
                if isinstance(prereq, Course):
                    self.prerequisites.add(prereq)

    def append_alias_list(self, alias_list=[]):
        ''' going from list to the set '''
        for alias in alias_list:
            self.alias_set.add(alias)

    def full_desc(self, tooltip=False, heading=False):
        ''' returning a string that gives the full course description '''
        temp = ""
        newline = "\n"
        if tooltip:
            newline = r"<br>"
        if heading:
            temp += str(self) + " "
            if len(self.alias_set) > 0:
                aka = "(aka "
                for alias in self.alias_set:
                    aka += alias + ", "
                aka = aka[:-2]+") "
                temp += aka
        temp += self.course_title
        course_desc = self.course_description
        if tooltip:
            course_desc = self.tooltip(course_desc)
        if len(self.course_description) > 0:
            temp += newline + course_desc
        if len(self.prerequisites) > 0:
            ''' if the list of prerequists is not empty list them'''
            temp += newline + "Prereqs:"
            for prereq in self.prerequisites:
                temp += newline + str(prereq)
        if tooltip:
            return r"<small>" + temp + r"</small>"
        return temp

    def tooltip(self, longstring):
        long_list = longstring.split(" ")
        temp = ""
        i = 0
        for word in long_list:
            temp += word
            i += len(word)
            if i >= 23:
                temp += r"<br>"
                i = 0
            else:
                temp += " "

        return temp

    def absorb(self, other):
        self.append_course_title(other.course_title)
        self.append_course_description(other.course_description)  # noqa: E501
        self.append_prerequisites(other.prerequisites.copy())
        self.append_alias_list(list(other.alias_set))

    def copypasta(self, other):
        self.absorb(other)
        other.absorb(self)