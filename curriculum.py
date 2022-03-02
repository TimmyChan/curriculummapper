#! python3

### course object to handle course 

def printbreak(): print("----------")

class Course:
    def __init__(self,  subject_code="DATA", course_code=1234, course_title="Hello", course_description="From the other side", prerequisites = None):
        self.subject_code = subject_code
        self.course_code = course_code
        self.course_title = course_title
        self.course_description = course_description
        if prerequisites is None:
            prerequisites = []
        self.prerequisites = prerequisites
    def __str__(self):
        return str(self.subject_code) + " " + str(self.course_code)
    def full_desc(self):
        temp =  str(self) + "\n Course Title: " + self.course_title + "\n Course Description: " + self.course_description 
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
            pass #just ignore if something tries to add something that isn't a course
### curriculum object to handle courses and generating a graph of prerequisites

class Curriculum:
    def __init__(self, university="Texas Institute of Technology and Sciences", degree_name = "MS in Data Science", course_list = None):
        self.university = university
        self.degree_name = degree_name
        if course_list is None:
            course_list = []
        self.course_list = course_list

    def add_course(self, x):
        if isinstance(x, Course):
            self.course_list.append(x)
        else:
            raise TypeError("tried to add an object that is not a Course to course_list")
    def __str__(self):
        return self.university + " " + self.degree_name + " Curriculum"
    def num_courses():
        return len(self.course_list)
    def print_all(self):
        print(str(self))
        printbreak()
        for x in self.course_list:
            printbreak()
            print(x.full_desc())
        printbreak()
