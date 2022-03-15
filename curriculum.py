#! python3

# Scraping and logic
from time import perf_counter
import sys
import os
import re
import requests
import unicodedata
from bs4 import BeautifulSoup

# Visualization
import matplotlib.pyplot as plt
import matplotlib.colors
import networkx as nx
from pyvis.network import Network
import numpy as np


def printbreak(): print("----------")


class Course:
    '''Course object to handle course data'''
    def __init__(self, subject_code="NONE", course_code="0",
                 course_title="",
                 course_description="",
                 prerequisites=None, alias_list=None):
        ''' * subject_code (string): Example "CSDS"
            * course_code (string): Example "498"
            course_key (string) = subject_code + " " + course_code = "CSDS 498"
            * course_title (string)
            * course_description (string)
            * prerequisites SET of Course objects
            * alias_set SET of strings
        '''
        self.subject_code = subject_code
        self.course_code = course_code
        self.course_key = str(subject_code) + " " + str(course_code)
        self.course_title = course_title
        self.course_description = course_description
        self.prerequisites = set()
        self.alias_set = set()
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
        return ("curriculum.Course(%s, %s, %s)" %
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
                return int(re.search(r'([0-9]{3}[0-9]*)', self.course_code)[0])
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


class Curriculum:
    '''curriculum object to handle courses and generating a graph of
    prerequisites'''
    def __init__(self, university="",
                 degree_name="", preferred_subject_code="", course_list=None,
                 URL=None, data_directory="canned_soup",
                 # RegEx: course id is four capitals with space then three
                 # numbers with a possible letter after the numbers then stop
                 # with a non-word
                 course_search=r"([A-Z]{4}\s\d{3}\w*)",
                 # get the subject code which is by default first 4 capitals
                 subject_search=r"([A-Z]{4})",
                 # get the course_code which are the digits
                 code_search=r"(\d{3}\w*)", colored_subjects=None
                 ):
        '''
        university (string)
        degree_name (string)
        preferred_subject_code (string)
        course_dict = {course_code : Course}
        url = ""
        url_list = [] # for history
        data_dir = data_directory
        alias_dict = (str: [list of str])
        diGraph nx.DiGraph
        soup = ""
        course_search (re.Match Object)
        subject_search (re.Match Object)
        code_search (re.Match Object)
        colored_subjects [list of str]
        '''
        self.university = university
        self.degree_name = degree_name
        self.preferred_subject_code = preferred_subject_code
        if course_list is None:
            course_list = []
        self.course_dict = {}
        self.url = ""
        self.url_list = []
        if URL is not None:
            self.set_url(URL)

        self.data_dir = data_directory
        self.alias_dict = {}
        # for a directed graph
        # this will stay empty until generate_graph is called!
        self.diGraph = nx.DiGraph()
        self.soup = None

        ''' RegEx compiled searches '''
        if isinstance(course_search, str):
            self.course_search = re.compile(course_search)
        if isinstance(subject_search, str):
            self.subject_search = re.compile(subject_search)
        if isinstance(code_search, str):
            self.code_search = re.compile(code_search)

        self.colored_subjects = []
        if len(self.preferred_subject_code) > 0:
            self.colored_subjects.append(self.preferred_subject_code)
        if colored_subjects is not None and isinstance(colored_subjects, list):
            for subj in colored_subjects:
                self.add_subject(subj)
        # ADDING COURSES
        self.course_codes_set = set()
        if len(course_list) > 0:
            for course in course_list:
                self.add_course(course)

    def add_subject(self, subj):
        if re.match(self.subject_search, subj):
            self.colored_subjects.append(subj)

    def add_alias_group(self, alias_group=[]):
        ''' Makes sure that aliases are all added to every possible position'''
        for alias in alias_group:
            try:
                for i in alias_group:
                    self.alias_dict[alias].add(i)
            except KeyError:
                self.alias_dict[alias] = set(alias_group)

    def add_course_object(self, x):
        '''
        Adds a Course object x to course_dict
        with str(x) as the key and iterates through all the prerequisites
        then also add them recursively to course_dict
        '''
        try:
            # first, only add to dict if it's not already there...
            key = str(x)
            self.course_codes_set.add(x.get_course_code_int())
            # print("Attempting to add %s" % key)
            if self.course_dict.get(key) is None:
                # print("\tAdding %s as a new key" % key)
                # adding to dictionary
                self.course_dict[key] = x
                # print("\tNew course added.")
                # importing alias relationships
                if len(x.alias_set) > 0:
                    # print("Found Aliases %s in Curriculum.add_course(x)" %
                    #      x.alias_list)
                    # generating alias_dict[key] : [alias_1, alias_2, etc]
                    x.alias_set.add(str(x))
                    self.add_alias_group(x.alias_set)
            else:
                # print("\tUpdating %s as existing key" % key)
                # print("\tAlready in dictionary, appending details...")
                # replace the details only if it's longer (nonempty)
                self.course_dict[key].absorb(x)
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
                    alias = unicodedata.normalize('NFKD', alias)
                    self.add_course_by_id(alias)
                    self.course_dict[alias].append_alias_list(x.alias_set)
        except Exception:
            raise TypeError("tried to add an object that is \
                             not a Course to course_list")

    def add_course(self, x):
        # print("add %s" % str(x))
        if isinstance(x, Course):
            self.add_course_object(x)
        if isinstance(x, str):
            self.add_courses_from_string(x)

    def course_id_to_list(self, course_id):
        ''' breaks course_id into subject and course codes '''
        course_id = unicodedata.normalize('NFKD', course_id)
        return (re.findall(self.subject_search, course_id)[0],
                re.findall(self.code_search, course_id)[0])

    def course_list_from_string(self, somewords):
        '''
        extracts list of courses from a string'
        returns them as a list of Course objects
        '''
        course_list = []
        course_ids = re.findall(self.course_search, str(somewords))
        for course_id in course_ids:
            # FOR SOME REASON \xa0 started appearing so clean it...
            norm_id = unicodedata.normalize('NFKD', course_id)
            # getting the subject and code to initiate Course object
            subject_code, course_code = self.course_id_to_list(norm_id)
            course_list.append(Course(subject_code, course_code))
        return course_list

    def course_id_list_from_string(self, somewords):
        '''
        extracts list of courses from a string
        returns the courses as a list of course_id.
        '''
        course_ids = re.findall(self.course_search, somewords)
        return [unicodedata.normalize('NFKD', course_id) for
                course_id in course_ids]

    def add_course_by_id(self, x):
        x = unicodedata.normalize('NFKD', x)
        if re.match(self.course_search, x):
            # print("Adding %s to curriculum" % str(x))
            subject_code, course_code = self.course_id_to_list(x)
            self.add_course(Course(subject_code, course_code))

    def add_courses_from_string(self, somewords):
        # print("\tParsing: '%s'" % somewords)
        somewords = unicodedata.normalize('NFKD', somewords)
        for c in self.course_list_from_string(somewords):
            # print("Adding %s to curriculum" % str(c))
            self.add_course(c)

    def __str__(self):
        ''' uni name, degree, curriculum '''
        return self.university + " " + self.degree_name + " Curriculum"

    def num_courses(self):
        ''' returns total number of unique courses'''
        return len(self.course_dict)

    def print_all(self, notebook=False, logging=True, defaults=True):
        '''
        no unit test for this one
        since it's rly just printing things out
        for debugging purposes
        '''
        # Save a reference to the original standard output
        init_time = perf_counter()
        original_stdout = sys.stdout

        with open(str(self)+' output.txt', 'w') as f:
            # Change the standard output to the file we created.
            if logging:
                sys.stdout = f
            print('Sources:')
            for u in self.url_list:
                print("\t" + str(u) + "\n")
            print(str(self))
            printbreak()
            print("Course Inventory contains %d courses..." %
                  self.num_courses())
            if self.num_courses() > 0:
                for x in self.course_dict:
                    printbreak()
                    print(self.course_dict[x].full_desc(heading=True))
                printbreak()
                # print(self.alias_dict)
        # Reset the standard output to its original value
        sys.stdout = original_stdout
        self.print_graph(notebook=notebook, defaults=defaults)
        finish_time = perf_counter()
        print("Printing time: %s" % str(finish_time - init_time))

    def get_course(self, course_id=""):
        ''' tries to retreive a Course object using the key (subj_code course_code)
            scans thru alias list and returns one.
        '''
        course_id = unicodedata.normalize('NFKD', course_id)
        # print("\t\tTrying to retreive %s" % course_id)
        # DEBUG print("\tseeking %s" % course_id)
        if self.alias_dict.get(course_id) is not None:
            # print("\t\tAlias entry found in alias dict")
            for alias in self.alias_dict[course_id]:
                # DEBUG print("checking %s" % alias)
                if re.match(self.preferred_subject_code, alias):
                    # print("returning %s" % self.course_dict[alias])
                    return self.course_dict[alias]
            key = list(self.alias_dict[course_id])[0]
            return self.course_dict[key]
        else:
            # DEBUG print("No Alias found returning %s" % course_id)
            try:
                return self.course_dict[course_id]
            except Exception:
                self.add_course_by_id(course_id)
                return self.course_dict[course_id]

    def generate_nx(self, emphasize_in_degree=False):
        '''
        Generates internal NetworkX object.
        '''
        self.update()
        if self.num_courses() > 0:
            print("Course Inventory contains %d courses..." %
                  self.num_courses())
            # Looping through every course:
            for course in self.course_dict.values():
                # DEBUG print("In generate_nx Looking for %s" % str(course))
                chosen = (self.get_course(str(course)))
                course_key = str(chosen)
                subject_code, course_code = self.course_id_to_list(course_key)
                # DEBUG print("Adding class %s as node" % course_key)
                color_group = 0
                try:
                    color_group = self.colored_subjects.index(subject_code) + 1
                except Exception:
                    pass
                self.diGraph.add_node(course_key,
                                      label=course_key,
                                      title=self.course_dict[course_key].full_desc(tooltip=True),  # noqa: E501,
                                      group=color_group)
                if len(course.prerequisites) > 0:
                    for prereq in course.prerequisites:
                        # print("Scanning for %s" % str(prereq))
                        prereq_true_self = self.get_course(str(prereq))
                        prereq_key = str(prereq_true_self)
                        if prereq_key != course_key:
                            subject_code = prereq_true_self.subject_code
                            # Adding node prereq_key
                            color_group = 0
                            try:
                                color_group = 1 + self.colored_subjects.index(
                                      subject_code)
                            except Exception:
                                pass
                            self.diGraph.add_node(prereq_key,
                                                  label=str(prereq_true_self),
                                                  title=prereq_true_self.full_desc(tooltip=True),  # noqa: E501,
                                                  group=color_group)
                            # Adding edge (prereq_key => course_key)
                            self.diGraph.add_edge(prereq_key, course_key)
            print("NetworkX object initiated.")
            print("Found %d unique classes with %d prerequisite relationships"
                  % (len(self.diGraph.nodes), len(self.diGraph.edges)))
            course_ints = np.array(list(self.course_codes_set))
            course_ints = course_ints[(course_ints >
                                       np.quantile(course_ints, 0.1)) &
                                      (course_ints <
                                       np.quantile(course_ints, 0.9))].tolist()
            color_min = 0
            color_max = max(course_ints)
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
                elif self.diGraph.nodes[node]['group'] == 2:
                    cmap = plt.cm.Greens
                elif self.diGraph.nodes[node]['group'] == 3:
                    cmap = plt.cm.Purples
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
        self.generate_nx()
        return self.diGraph

    def print_graph(self, notebook=False, emphasize_in_degree=False,
                    defaults=True):

        self.generate_nx(emphasize_in_degree=emphasize_in_degree)

        net = Network('768px', '1024px', notebook)

        net.from_nx(self.diGraph)
        if defaults:
            net.set_options('''
                var options = {
                  "nodes": {
                    "shadow": {
                      "enabled": true,
                      "size": 15
                    }
                  },
                  "edges": {
                    "arrows": {
                      "to": {
                        "enabled": true
                      }
                    },
                    "color": {
                      "inherit": "both"
                    },
                    "smooth": false
                  },
                  "interaction": {
                    "hover": true
                  },
                  "manipulation": {
                    "enabled": true
                  },
                  "physics": {
                    "forceAtlas2Based": {
                      "gravitationalConstant": -200,
                      "centralGravity": 0.02,
                      "springLength": 120,
                      "springConstant": 0.2,
                      "avoidOverlap": 0.5
                    },
                    "minVelocity": 0.75,
                    "solver": "forceAtlas2Based"
                  }
                }
                ''')
        else:
            net.show_buttons(True)
        # net.enable_physics(True)
        # net.show_buttons(filter_=True)
        net.show("%s_%s.html" % (str(self).replace(" ", "_"),
                 self.preferred_subject_code))
        # net.show_buttons(filter_=['physics'])

    def set_url(self, new_url):
        if isinstance(new_url, str):
            # print("\t\tNew URL detected!")
            self.url_list.append(new_url)
            self.url = new_url

    def polite_crawler(self, URL=None):
        ''' saves a copy of the html to not overping '''
        if URL is not None:
            self.set_url(URL)

        data_dir = "canned_soup"
        if self.data_dir != "":
            data_dir = self.data_dir
        filename = "DATA"
        filename = str(self).replace(" ", "_")
        i = 1
        if self.url.split("/")[-i] == "":
            i += 1
        filename += "_" + self.url.split("/")[-i] + ".html"
        # print("Trying %s/%s" % (data_dir, filename))
        try:
            os.makedirs(data_dir)
        except Exception:
            # only here if already have the directory
            # do nothing safely
            pass
        try:
            # try to open html, where we cache the soup
            print("Reading from '%s'..." % str(data_dir + "/" + filename))
            with open(data_dir + "/" + filename, "r") as file:
                self.soup = BeautifulSoup(file, "lxml")
            return self.soup
        except Exception:
            try:
                print("\t\tPinging Server")
                res = requests.get(self.url)
                # using lxml because of bs4 doc
                self.soup = BeautifulSoup(res.content, "lxml")
                print("Writing to '%s'..." % str(data_dir + "/" + filename))
                with open(data_dir + "/" + filename, "w") as file:
                    file.write(str(self.soup))
                return self.soup
            except Exception:
                print("Why are you even here?")
                return self.soup

    def get_soup(self, URL=None):
        return self.polite_crawler(URL)

    def update(self, guess_alias=False):
        for key, alias_list in self.alias_dict.items():
            for alias in alias_list:
                self.course_dict[key].add_alias(alias)
                self.course_dict[key].copypasta(self.course_dict[alias])
