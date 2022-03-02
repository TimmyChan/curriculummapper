#! python3

# course object to handle course


def printbreak(): print("----------")


class Course:
    def __init__(self,  subject_code="DATA", course_code=1234,
                 course_title="Hello",
                 course_description="From the other side",
                 prerequisites=None):
        self.subject_code = subject_code
        self.course_code = course_code
        self.course_title = course_title
        self.course_description = course_description
        self.prerequisites = []
        if prerequisites is not None:
            for course in prerequisites:
                self.add_prereq(course)

    def __str__(self):
        return str(self.subject_code) + " " + str(self.course_code)

    def full_desc(self):
        temp = str(self) + "\n Course Title: " + self.course_title + \
                        "\n Course Description: " + self.course_description
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
        self.course_list = []
        if course_list is None:
            course_list = []
        for course in course_list:
            self.add_course(course)

    def add_course(self, x):
        if isinstance(x, Course):
            self.course_list.append(x)
        else:
            raise TypeError("tried to add an object that is \
                             not a Course to course_list")

    def __str__(self):
        return self.university + " " + self.degree_name + " Curriculum"

    def num_courses(self):
        return len(self.course_list)

    def print_all(self):
        print(str(self))
        printbreak()
        for x in self.course_list:
            printbreak()
            print(x.full_desc())
        printbreak()
