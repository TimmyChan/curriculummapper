#! python3

# course object to handle course


def printbreak(): print("----------")


class Course:
    def __init__(self,  subject_code="SUBJ", course_code=1234,
                 course_title="Course Title",
                 course_description="Course Description",
                 prerequisites=None):
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
        return str(self.subject_code) + " " + str(self.course_code) + " " + \
               self.course_title

    def full_desc(self):
        temp = str(self) + "\n Course Description: " + self.course_description
        if len(self.prerequisites) > 0:
            temp += "\nPrereqs: "
            for prereq in self.prerequisites:
                temp += str(prereq)
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


# curriculum object to handle courses and generating a graph of prerequisites
class Curriculum:
    def __init__(self, university="Brown",
                 degree_name="MS in Data Science", course_list=None):
        self.university = university
        self.degree_name = degree_name
        if course_list is None:
            course_list = []
        self.course_dict = {}
        for course in course_list:
            self.add_course(course)

    def add_course(self, x):
        if isinstance(x, Course):
            self.course_dict[x.course_key] = x
        else:
            raise TypeError("tried to add an object that is \
                             not a Course to course_list")

    def __str__(self):
        return self.university + " " + self.degree_name + " Curriculum"

    def num_courses(self):
        return len(self.course_dict)

    def print_all(self):
        print(str(self))
        printbreak()
        for x in self.course_dict:
            printbreak()
            print(self.course_dict[x].full_desc())
        printbreak()

    def find_course(self, course_key="CSDS 486"):
        return self.course_dict[course_key]
