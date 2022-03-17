"""
Unit tests for the curriculum class
"""

from curriculummapper import Course, Curriculum


def test_init():
    '''blink init'''
    test_curr = Curriculum()
    assert (test_curr.university == "" and
            test_curr.degree_name == "" and
            test_curr.course_dict == {})


def test_init_values():
    '''initiating with given values'''
    x = Course()
    y = Course(course_code=4567, prerequisites=[x])
    test_curr = Curriculum("TAMS",
                           "High School Diploma with Honors", "CSDS",
                           [x, y])
    assert (test_curr.university == "TAMS" and
            test_curr.degree_name == "High School Diploma with Honors" and
            # course_dict will use a Course object as a key and list of prereqs
            # which will help with adding each key to a graph later.
            test_curr.course_dict["NONE 0"] == x and
            test_curr.course_dict["NONE 4567"] == y)


def test_prereq_recursion():
    '''
    Course y is added with prereq x, prereq x is not in dict.
    expectation is x should also be added to the dict.
    '''
    x = Course()
    y = Course(prerequisites=[x])
    test_curr = Curriculum(course_list=[y])
    assert (str(test_curr.course_dict[str(x)]) == str(x) and
            str(test_curr.course_dict[str(y)]) == str(y))


def test_adding_repeated_course():
    '''
    when adding a course with less details the details should be preserved
    '''
    x = Course("DATA", "1234", "Real Analysis", "Get lubericant")
    y = Course("DATA", "1234")
    test_curr = Curriculum("TAMS", "High School Diploma with Honors")
    test_curr.add_course(x)
    test_curr.add_course(y)
    assert (test_curr.course_dict["DATA 1234"].course_title ==
            "Real Analysis" and
            test_curr.course_dict["DATA 1234"].course_description ==
            "Get lubericant" and
            test_curr.num_courses() == 1)


def test_num_courses():
    ''' testing no courses, added courses with prereq '''
    x = Course()
    y = Course(course_code=4567, prerequisites=[x])
    test_curr = Curriculum()
    test_curr2 = Curriculum(course_list=[y])
    assert (test_curr.num_courses() == 0 and
            test_curr2.num_courses() == 2)


def test_alias():
    ''' testing alias dectection system '''
    x = Course("CSDS", "1234", "Sound Engineering",
               alias_list=["CSDS 1234", "YMCA 1234"])
    y = Course("YMCA", "1234", "Sound Engineering",
               alias_list=["CSDS 1234", "YMCA 1234"])
    test_curr = Curriculum("TAMS", "High School Diploma with Honors", "CSDS")
    test_curr.add_course(y)
    test_curr.add_course(x)
    assert str(test_curr.get_course("YMCA 1234")) == "CSDS 1234"
