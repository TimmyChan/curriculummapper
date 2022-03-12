#! python3

import re
import os
import requests
from bs4 import BeautifulSoup
import matplotlib.pyplot as plt
import matplotlib.colors
import networkx as nx
from pyvis.network import Network


def printbreak(): print("----------")


class Course:
    '''Course object to handle course data'''
    def __init__(self, subject_code="NONE", course_code="0",
                 course_title="",
                 course_description="",
                 prerequisites=None, alias_list=None):
        ''' subject_code (string)
            course_code (string)
            course_key (string) = subject_code + " " + course_code
            course_title (string)
            course_description (string)
            prerequisites [SET of Course(s)] somewhat like a linked list
            alias_list [SET of strings]
        '''
        self.subject_code = subject_code
        self.course_code = course_code
        self.course_key = str(subject_code) + " " + str(course_code)
        self.course_title = course_title
        self.course_description = course_description
        self.prerequisites = set()
        if prerequisites is None:
            prerequisites = []
        for course in prerequisites:
            self.add_prereq(course)
        self.alias_set = set()
        if alias_list is None:
            alias_list = []
        else:
            for name in alias_list:
                self.add_alias(name)
        # self.add_alias(self.course_key)

    def __str__(self):
        '''all we need is subject and course code for an identifier'''
        return self.course_key

    def add_alias(self, course_id):
        self.alias_set.add(course_id)

    def add_prereq(self, x):
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
        if isinstance(self.course_code, int):
            return self.course_code
        else:
            try:
                return int(re.findall(r'([0-9]+)', self.course_code)[0])
            except Exception:
                return int(self.course_code)

    def append_course_title(self, course_title=""):
        if len(course_title) >= len(self.course_title):
            self.course_title = course_title

    def append_course_description(self, course_description=""):
        if len(course_description) >= len(self.course_description):
            self.course_description = course_description

    def append_prerequisites(self, prerequisites=[]):
        if len(prerequisites) > 0:
            for prereq in prerequisites:
                if isinstance(prereq, Course):
                    self.prerequisites.add(prereq)

    def append_alias_list(self, alias_list=[]):
        for alias in alias_list:
            self.alias_set.add(alias)

    def full_desc(self):
        ''' returning a string that gives the full course description '''
        aka = " "
        if len(self.alias_set) > 0:
            aka = " (aka "
            for alias in self.alias_set:
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


class Curriculum:
    '''curriculum object to handle courses and generating a graph of
    prerequisites'''
    def __init__(self, university="",
                 degree_name="", preferred_subject_code="", course_list=None,
                 URL="", data_directory=None):
        '''
        University and degree name are for display
        course_list is not really expected but you can initiate with a list of
        Course objects.
        Course dict: {course_id (str): Course}
        alias_dict: {alias (str): set of str}
        '''
        self.university = university
        self.degree_name = degree_name
        self.preferred_subject_code = preferred_subject_code
        if course_list is None:
            course_list = []
        self.course_dict = {}
        self.url = URL
        self.data_dir = "canned_soup"
        if data_directory is not None:
            self.data_dir = data_directory
        self.alias_dict = {}
        # for a directed graph
        # this will stay empty until generate_graph is called!
        self.diGraph = nx.DiGraph()
        self.soup = self.polite_crawler()

        if len(course_list) > 0:
            for course in course_list:
                self.add_course(course)

    def add_alias_group(self, alias_group=[]):
        for alias in alias_group:
            try:
                for i in alias_group:
                    self.alias_dict[alias].add(i)
            except KeyError:
                self.alias_dict[alias] = set(alias_group)

    def add_course(self, x):
        '''
        Adds a Course object x to course_dict
        with str(x) as the key and iterates through all the prerequisites
        then also add them recursively to course_dict
        So what happens when ECSE 132 and CSDS is the same course...
        Currently adding both and keeping track of aliases
        '''
        if isinstance(x, Course):
            # print("Adding %s" % str(x))
            # first, only add to dict if it's not already there...
            key = str(x)

            if self.course_dict.get(key) is None:
                # adding to dictionary
                self.course_dict[key] = x

                # importing alias relationships
                if len(x.alias_set) > 0:
                    # print("Found Aliases %s in Curriculum.add_course(x)" %
                    #      x.alias_list)
                    # generating alias_dict[key] : [alias_1, alias_2, etc]
                    self.add_alias_group(x.alias_set)
            else:
                # replace the details only if it's longer (nonempty)
                self.course_dict[key].append_course_title(x.course_title)
                self.course_dict[key].append_course_description(x.course_description)  # noqa: E501
                self.course_dict[key].append_prerequisites(x.prerequisites)
                self.course_dict[key].append_alias_list(list(x.alias_set))
                self.add_alias_group(self.course_dict[key].alias_set)
            # loop through prerequisites list
            for prereq in x.prerequisites:
                # recurison
                # print("Found prereq %s, adding it" % str(prereq))
                self.add_course(prereq)
            if len(x.alias_set) > 1:
                # print("Alias Found")
                for alias in x.alias_set:
                    # print("Attempting to split %s" % alias)
                    self.add_course(Course(alias.split()[0], alias.split()[1]))
                    self.course_dict[alias].append_alias_list(x.alias_set)
        else:
            raise TypeError("tried to add an object that is \
                             not a Course to course_list")

    def __str__(self):
        return self.university + " " + self.degree_name + " Curriculum"

    def num_courses(self):
        ''' returns total number of unique courses'''
        return len(self.course_dict)

    def print_all(self, notebook=False):
        '''
        no unit test for this one
        since it's rly just printing things out
        for debugging purposes
        '''
        print(str(self))
        printbreak()
        print("Course Inventory contains %d courses..." %
              self.num_courses())
        if self.num_courses() > 0:
            for x in self.course_dict:
                printbreak()
                print(self.course_dict[x].full_desc())
            printbreak()
            print(self.alias_dict)
            self.print_graph(notebook)

    def get_course(self, course_id=""):
        ''' tries to retreive a Course object using the key (subj_code course_code)
            scans thru alias list and returns one.
            returns None if not in dict
            '''
        print("\tseeking %s" % course_id)
        if self.alias_dict.get(course_id) is not None:
            # print("\t\tAlias found")
            for alias in self.alias_dict[course_id]:
                print("checking %s" % alias)
                if re.match(self.preferred_subject_code, alias):
                    print("returning %s" % self.course_dict[alias])
                    return self.course_dict[alias]
        else:
            print("No Alias found returning %s" % course_id)
            return self.course_dict[course_id]

    def generate_nx(self, emphasize_in_degree=False):
        '''
        Generates internal NetworkX object.
        '''
        if self.num_courses() > 0:
            print("Course Inventory contains %d courses..." %
                  self.num_courses())
            # Looping through every course:
            for course in self.course_dict.values():
                print("In generate_nx Looking for %s" % str(course))
                course_key = str(self.get_course(str(course)))
                print("Adding class %s as node" % course_key)

                self.diGraph.add_node(course_key,
                                      label=course_key,
                                      title=self.course_dict[course_key].full_desc(),  # noqa: E501,
                                      group=(1 if
                                             re.match(self.preferred_subject_code, course_key)  # noqa: E501
                                             else 0))
                if len(course.prerequisites) > 0:
                    for prereq in course.prerequisites:
                        prereq_key = str(self.get_course(str(prereq)))
                        # Adding node prereq_key
                        self.diGraph.add_node(prereq_key,
                                              label=prereq_key,
                                              title=self.course_dict.get(prereq_key).full_desc(),  # noqa: E501,
                                              group=(1 if
                                                     re.match(self.preferred_subject_code, prereq_key)  # noqa: E501
                                                     else 0))
                        # Adding edge (prereq_key => course_key)
                        self.diGraph.add_edge(prereq_key, course_key)
            # DiGraph populated.
            preferred_nodes = [x for x, y in self.diGraph.nodes(data=True)
                               if y['group'] == 1]
            course_ints = [self.course_dict[node].get_course_code_int() for
                           node in preferred_nodes]
            color_min, color_max = min(course_ints), max(course_ints)
            # print(color_min, color_max)
            for node in self.diGraph:
                # setting the size of each node to depend
                # on the in_degree or out degree based on emphasize_in_degree
                self.diGraph.nodes[node]['size'] = \
                    (2*(self.diGraph.in_degree(node) + 5)
                     if emphasize_in_degree else
                     2*(self.diGraph.out_degree(node) + 5))
                norm = matplotlib.colors.Normalize(color_min, color_max)
                if self.diGraph.nodes[node]['group'] == 1:
                    cmap = plt.cm.Blues
                else:
                    cmap = plt.cm.Greys
                # 1) get the course #
                # 2) normalize from
                self.diGraph.nodes[node]['color'] = \
                    matplotlib.colors.rgb2hex(cmap(norm(
                        self.course_dict[node].get_course_code_int())))
        else:
            print("Add courses first!")

    def get_nx(self):
        self.generate_graph()
        return self.diGraph

    def print_graph(self, notebook=False, emphasize_in_degree=False):

        self.generate_nx(emphasize_in_degree=emphasize_in_degree)

        if notebook:
            net = Network(notebook=True)
        else:
            net = Network('768px', '1024px')
        net.from_nx(self.diGraph)
        net.set_options('''
            var options = {
              "edges": {
                "arrows": {
                  "to": {
                    "enabled": true
                  }
                },
                "color": {
                  "inherit": true
                },
                "smooth": false
              },
              "physics": {
                "forceAtlas2Based": {
                  "springLength": 100,
                  "avoidOverlap": 1
                },
                "minVelocity": 0.75,
                "solver": "forceAtlas2Based"
              }
            }
            ''')
        # net.show_buttons(filter_=['physics'])
        # net.enable_physics(True)
        net.show("%s.html" % self.preferred_subject_code)

    def set_url(self, str):
        self.url = str

    def polite_crawler(self, URL=None):
        ''' saves a copy of the html to not overping '''
        if self.url == "" and URL is None:
            print("Initiate with a URL")
            return None

        current_url = self.url
        if URL is not None:
            current_url = URL

        else:
            data_dir = "canned_soup"
            if self.data_dir != "":
                data_dir = self.data_dir
            filename = "DATA"
            if self.preferred_subject_code != "":
                filename = self.preferred_subject_code
            try:
                os.makedirs(data_dir)
            except Exception:
                # only here if already have the directory
                # do nothing safely
                pass
            try:
                # try to open html, where we cache the soup
                with open(data_dir + "/" + filename, "r") as file:
                    soup = BeautifulSoup(file, "lxml")
                return soup
            except Exception:
                try:
                    res = requests.get(current_url)
                    # using lxml because of bs4 doc
                    soup = BeautifulSoup(res.content, "lxml")
                    with open("canned_soup/"+filename, "w") as file:
                        file.write(str(soup))
                    return soup
                except Exception:
                    print("Probably had an issue connecting or writing to file.")
                    return None

    def get_soup(self):
        self.soup = self.polite_crawler()
        return self.soup