"""
Unit tests for the curriculum class
"""

from curriculum import Course, Curriculum


def test_init():
    test_curr = Curriculum()
    assert (test_curr.university == "Brown" and 
            test_curr.degree_name == "MS in Data Science" and 
            test_curr.course_list == [])


def test_init_values():
    x = Course()
    y = Course(course_code=4567, prerequistes=[x])
    test_curr = Curriculum("TAMS", 
                           "High School Diploma with Honors", 
                           [x, y])
    assert (test_curr.university == "TAMS" and
            test_curr.degree_name == "High School Diploma with Honors" and
            test_curr.course_list == [x, y])


def test_num_courses():
    x = Course()
    y = Course(course_code=4567, prerequisites=[x])
    test_curr = Curriculum()
    test_curr2 = Curriculum(course_list=[x, y])
    assert (test_curr.num_courses() == 0 and
            test_curr2.num_courses() == 2)
