#! python3


# import networkx as nx


def printbreak(): print("----------")


class Course:
    '''Course object to handle course data'''
    def __init__(self,  subject_code="NONE", course_code="0",
                 course_title="",
                 course_description="",
                 prerequisites=None):
        ''' subject_code (string)
            course_code (string or int)
            course_title (string)
            course_description (string)
            prerequisites [list of Course(s)]
        '''
        self.subject_code = subject_code
        self.course_code = course_code
        self.course_key = str(subject_code) + " " + str(course_code)
        self.course_title = course_title
        self.course_description = course_description
        if prerequisites is None:
            prerequisites = []
        self.prerequisites = []
        for course in prerequisites:
            self.add_prereq(course)

    def __str__(self):
        '''all we need is subject and course code for an identifier'''
        return str(self.subject_code) + " " + str(self.course_code)

    def full_desc(self):
        ''' returning a string that gives the full course description '''
        temp = (str(self) + " " + str(self.course_title) +
                "\nCourse Description: " + self.course_description)
        if len(self.prerequisites) > 0:
            ''' if the list of prerequists is not empty list them'''
            temp += "Prereqs:\n"
            for prereq in self.prerequisites:
                temp += str(prereq) + "\n"
        return temp

    def add_prereq(self, x):
        try:
            if isinstance(x, Course):
                self.prerequisites.append(x)
            else:
                raise ValueError
        except ValueError:
            print("Only course objects accepted in the prerequisites list.")
            # just ignore if x is something that isn't a course
            pass


class Curriculum:
    '''curriculum object to handle courses and generating a graph of
    prerequisites'''
    def __init__(self, university="",
                 degree_name="", course_list=None):
        self.university = university
        self.degree_name = degree_name
        if course_list is None:
            course_list = []
        self.course_dict = {}
        for course in course_list:
            self.add_course(course)
            for prereq in course.prerequisites:
                self.add_course(prereq)

    def add_course(self, x):
        '''
        Adds a Course object x to course_dict
        with str(x) as the key and iterates through all the prerequisites
        then also add them recursively to course_dict
        '''
        if isinstance(x, Course):
            # first, only add to dict if it's not already there...
            if self.get_course(str(x)) is None:
                # adding to dictionary
                self.course_dict[str(x)] = x
                # loop through prerequisites list
                for prereq in x.prerequisites:
                    # recurison
                    self.add_course(prereq)
            else:
                # replace the details only if it's longer (nonempty)
                if len(x.course_title) > \
                   len(self.course_dict[str(x)].course_title):
                    self.course_dict[str(x)].course_title = x.course_title
                if len(x.course_description) > \
                   len(self.course_dict[str(x)].course_description):
                    self.course_dict[str(x)].course_description = \
                                           x.course_description
                if len(x.prerequisites) > \
                   len(self.course_dict[str(x)].prerequisites):
                    self.course_dict[str(x)].prerequisites = x.prerequisites
        else:
            raise TypeError("tried to add an object that is \
                             not a Course to course_list")

    def __str__(self):
        return self.university + " " + self.degree_name + " Curriculum"

    def num_courses(self):
        ''' returns total number of unique courses'''
        return len(self.course_dict)

    def print_all(self):
        ''' purely for CLI debug use'''
        print(str(self))
        printbreak()
        for x in self.course_dict:
            printbreak()
            print(self.course_dict[x].full_desc())
        printbreak()

    def get_course(self, course_id=""):
        ''' tries to retreive a Course object using the key, returns None
            if not in dict'''
        try:
            return self.course_dict[course_id]
        except KeyError:
            return None

    def generate_graph(self):
        if self.num_courses() > 0:
            pass
        else:
            pass
