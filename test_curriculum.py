"""
Unit tests for the curriculum class
"""

from curriculum import Course, Curriculum


# testing blink init
def test_init():
    test_curr = Curriculum()
    assert (test_curr.university == "" and
            test_curr.degree_name == "" and
            test_curr.course_dict == {})


# testing initiating with given values
def test_init_values():
    x = Course()
    y = Course(course_code=4567, prerequisites=[x])
    test_curr = Curriculum("TAMS",
                           "High School Diploma with Honors",
                           [x, y])
    assert (test_curr.university == "TAMS" and
            test_curr.degree_name == "High School Diploma with Honors" and
            # course_dict will use a Course object as a key and list of prereqs
            # which will help with adding each key to a graph later.
            test_curr.course_dict == {x: [], y: [x]})


# Scenario:
# Course x is added with prereq a, prereq a is not in list.
# expectation is a should also be added to the list.
def test_prereq_recursion():
    x = Course()
    y = Course(prerequisites=[x])
    test_curr = Curriculum(course_list=[y])
    assert test_curr.course_dict == {x: [], y: [x]}


def test_num_courses():
    x = Course()
    y = Course(course_code=4567, prerequisites=[x])
    test_curr = Curriculum()
    test_curr2 = Curriculum(course_list=[x, y])
    assert (test_curr.num_courses() == 0 and
            test_curr2.num_courses() == 2)
