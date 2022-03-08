#! python3

from pyvis.network import Network
import networkx as nx
import re
# import matplotlib.pyplot as plt


def printbreak(): print("----------")


class Course:
    '''Course object to handle course data'''
    def __init__(self, subject_code="NONE", course_code="0",
                 course_title="",
                 course_description="",
                 prerequisites=None, alias_list=None):
        ''' subject_code (string)
            course_code (string or int)
            course_title (string)
            course_description (string)
            prerequisites [list of Course(s)] somewhat like a linked list
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
        return self.course_key

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
                 degree_name="", preferred_subject_code="", course_list=None):
        '''
        University and degree name are for display
        course_list is not really expected but you can initiate with a list of
        Course objects.
        '''
        self.university = university
        self.degree_name = degree_name
        self.preferred_subject_code = preferred_subject_code
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

    def add_alias_group(self, alias_group=[]):
        for alias in alias_group:
            try:
                self.alias_dict[alias] = \
                    list(set(self.alias_dict[alias]) |
                         set(alias_group))
            except KeyError:
                self.alias_dict[alias] = alias_group

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
                if len(x.alias_list) > 0:
                    # print("Found Aliases %s in Curriculum.add_course(x)" %
                    #      x.alias_list)
                    # generating alias_dict[key] : [alias_1, alias_2, etc]
                    self.add_alias_group(x.alias_list)
            else:
                # replace the details only if it's longer (nonempty)
                if len(x.course_title) >= \
                   len(self.course_dict[key].course_title):
                    self.course_dict[key].course_title = x.course_title
                if len(x.course_description) >= \
                   len(self.course_dict[key].course_description):
                    self.course_dict[key].course_description = \
                                           x.course_description
                if len(x.prerequisites) >= \
                   len(self.course_dict[key].prerequisites):
                    self.course_dict[key].prerequisites = x.prerequisites
                if len(x.alias_list) >= len(self.course_dict[key].alias_list):
                    self.course_dict[key].alias_list = x.alias_list
                    self.add_alias_group(x.alias_list)
            # loop through prerequisites list
            for prereq in x.prerequisites:
                # recurison
                # print("Found prereq %s, adding it" % str(prereq))
                self.add_course(prereq)

            for alias in x.alias_list:
                # print("Found alias %s adding it" % alias)
                self.add_course(Course(alias.split()[0], alias.split()[1]))
        else:
            raise TypeError("tried to add an object that is \
                             not a Course to course_list")

    def __str__(self):
        return self.university + " " + self.degree_name + " Curriculum"

    def num_courses(self):
        ''' returns total number of unique courses'''
        return len(self.course_dict)

    def print_all(self, notebook=False):
        ''' purely for CLI debug use'''
        print(str(self))
        printbreak()
        for x in self.course_dict:
            printbreak()
            print(self.course_dict[x].full_desc())
        printbreak()
        # print(self.alias_dict)
        self.generate_graph(notebook)

    def get_course(self, course_id="", ):
        ''' tries to retreive a Course object using the key (subj_code course_code)
            scans thru alias list and returns one.
            returns None if not in dict
            '''
        # print("\tseeking %s" % course_id)
        if self.alias_dict.get(course_id) is not None:
            # print("\t\tAlias found")
            for alias in self.alias_dict[course_id]:
                if re.match(self.preferred_subject_code, alias):
                    # print("returning %s" % self.course_dict[alias])
                    return self.course_dict[alias]
        else:
            return self.course_dict[course_id]

    def generate_graph(self, notebook=False):
        '''
        Visualizing the curriculum using networkx.
        '''
        for alias in self.alias_dict:
            self.alias_dict[alias].sort()
        if self.num_courses() > 0:
            print("Course Inventory contains %d courses..." %
                  self.num_courses())
            # Looping through every course:
            for course in self.course_dict.values():
                course_key = str(self.get_course(str(course)))
                # print("Adding class %s as node" % course_key)

                self.diGraph.add_node(course_key,
                                      label=course_key,
                                      title=self.course_dict[course_key]
                                      .course_title,
                                      group=(1
                                             if re.match(self.preferred_subject_code, course_key)  # noqa: E501
                                             else 0))
                if len(course.prerequisites) > 0:
                    for prereq in course.prerequisites:
                        prereq_key = str(self.get_course(str(prereq)))
                        # Adding node prereq_key
                        self.diGraph.add_node(prereq_key,
                                              label=prereq_key,
                                              title=self.course_dict[prereq_key]  # noqa: E501
                                              .course_title,
                                              group=(1 if
                                                     re.match(self.preferred_subject_code, prereq_key)  # noqa: E501
                                                     else 0))
                        # Adding edge (prereq_key => course_key)
                        self.diGraph.add_edge(prereq_key, course_key)
            # DiGraph populated.

            print("After scanning alias lists, found %d unique classes" %
                  self.diGraph.number_of_nodes())
            print("Found %d number of prerequisite relationships" %
                  self.diGraph.number_of_edges())

            # formatting graph
            for node in self.diGraph:
                # setting the size of each node to depend
                # on the in_degree
                self.diGraph.nodes[node]['size'] = \
                    5*(self.diGraph.in_degree(node) + 1)

#            for node in self.diGraph.nodes:
#                self.digraph.nodes[node]
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
            net.show("%s.html" % self.preferred_subject_code)
        else:
            print("Add courses first!")
