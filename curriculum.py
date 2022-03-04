#! python3

from pyvis.network import Network
import networkx as nx
# import matplotlib.pyplot as plt


def printbreak(): print("----------")


class Course:
    '''Course object to handle course data'''
    def __init__(self,  subject_code="NONE", course_code="0",
                 course_title="",
                 course_description="",
                 prerequisites=None, alias_list=None):
        ''' subject_code (string)
            course_code (string or int)
            course_title (string)
            course_description (string)
            prerequisites [list of Course(s)]
            alias_list [list of strings]
        '''
        self.subject_code = subject_code
        self.course_code = course_code
        self.course_key = str(subject_code) + " " + str(course_code)
        self.course_title = course_title
        self.course_description = course_description
        self.prerequisites = []
        if prerequisites is None:
            prerequisites = []
        for course in prerequisites:
            self.add_prereq(course)
        self.alias_list = []
        if alias_list is None:
            alias_list = []
        for name in alias_list:
            self.add_alias(name)

    def __str__(self):
        '''all we need is subject and course code for an identifier'''
        return str(self.subject_code) + " " + str(self.course_code)

    def add_alias(self, course_id):
        self.alias_list.append(course_id)

    def full_desc(self):
        ''' returning a string that gives the full course description '''
        aka = " "
        if len(self.alias_list) > 0:
            aka = " (aka "
            for alias in self.alias_list:
                aka += alias + ", "
            aka = aka[:-2]+") "
        temp = (str(self) + aka + str(self.course_title) +
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
                if str(self) != str(x):
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
        '''
        University and degree name are for display
        course list is not really expected but you can initiate with a list of
        Course objects.
        '''
        self.university = university
        self.degree_name = degree_name
        if course_list is None:
            course_list = []
        self.course_dict = {}
        self.alias_dict = {}
        # this will stay empty until generate_graph is called!
        self.diGraph = nx.DiGraph()
        for course in course_list:
            self.add_course(course)
            for prereq in course.prerequisites:
                self.add_course(prereq)
        # using set on alias_dict will yield unique classes.
        # self.unique_classes = set(list(self.alias_dict.values()))
        # for a directed graph
        self.diGraph = nx.DiGraph()

    def add_course(self, x):
        '''
        Adds a Course object x to course_dict
        with str(x) as the key and iterates through all the prerequisites
        then also add them recursively to course_dict
        So what happens when ECSE 132 and CSDS is the same course...
        Currently adding both and keeping track of aliases
        '''
        if isinstance(x, Course):
            # first, only add to dict if it's not already there...
            key = str(x)
            if self.get_course(key) is None:
                # adding to dictionary
                self.course_dict[key] = x
                # loop through prerequisites list
                for prereq in x.prerequisites:
                    # recurison
                    self.add_course(prereq)
            # importing alias relationships
            if len(x.alias_list) > 0:
                # print("Found Aliases %s in Curriculum.add_course(x)" %
                #      x.alias_list)
                # generating alias_dict[key] : [alias_1, alias_2, etc]
                for alias in x.alias_list:
                    try:
                        self.alias_dict[alias] = \
                           list(set(self.alias_dict[alias]) |
                                set(x.alias_list))
                    except KeyError:
                        self.alias_dict[alias] = x.alias_list
                # self.unique_classes = set(list(self.alias_dict.values()))

            else:
                # replace the details only if it's longer (nonempty)
                if len(x.course_title) > \
                   len(self.course_dict[key].course_title):
                    self.course_dict[key].course_title = x.course_title
                if len(x.course_description) > \
                   len(self.course_dict[key].course_description):
                    self.course_dict[key].course_description = \
                                           x.course_description
                if len(x.prerequisites) > \
                   len(self.course_dict[key].prerequisites):
                    self.course_dict[key].prerequisites = x.prerequisites
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
        print(self.alias_dict)
        self.generate_graph()

    def get_course(self, course_id=""):
        ''' tries to retreive a Course object using the key, returns None
            if not in dict'''
        try:
            return self.course_dict[course_id]
        except KeyError:
            return None

    def generate_graph(self):
        if self.num_courses() > 0:
            print("Curriculum contains %d courses..." % self.num_courses())
            # self.unique_classes = set(list(self.alias_dict.values()))
            # print("Found %d courses that represent %d unique courses" %
            #     len(set(tuple(self.alias_dict.values()))))
            for course in self.course_dict:
                key = str(course)
                # print("Adding class %s" % key)
                self.diGraph.add_node(key)
                for prereq in self.course_dict[key].prerequisites:
                    # print("Adding link from %s to %s" % (str(prereq), key))
                    self.diGraph.add_node(str(prereq))
                    self.diGraph.add_edge(str(prereq), key)
            print("Found %d number of prerequisite relationships" %
                  self.diGraph.number_of_edges())
            net = Network('768px', '1024px')
            net.from_nx(self.diGraph)
            net.show_buttons(filter_=['physics'])
            net.show('nx.html')
        else:
            pass
