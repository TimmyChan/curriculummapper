"""
Unit tests for the Course class
"""

from curriculum import Course


# No parameters passed should give blink course
def test_init():
    x = Course()
    assert (x.subject_code == "NONE" and x.course_code == "0" and
            x.course_title == "" and
            x.course_description == "" and
            x.prerequisites == set())


# Parameters passed should be saved
def test_init_with_param():
    x = Course()
    y = Course("DSCS", 5679, "To the left",
               "Everything you own", [x])
    assert (y.subject_code == "DSCS" and
            y.course_code == 5679 and
            y.course_title == "To the left" and
            y.course_description == "Everything you own" and
            y.prerequisites == set([x]))


# testing add_alias
def test_alias():
    ''' should be sorted '''
    x = Course("CSDS", 1234, "Yo Mama",
               "Needs her own zipcode")
    x.add_alias("ABCD 1234")
    assert x.alias_set == set(["ABCD 1234"])


# testing __str__() Should print subject code, course code.
def test_str():
    x = Course("SUBJ", "1234", "Course Title")
    assert str(x) == "SUBJ 1234"


# adding a prereq to the list
def test_add_prereq():
    x = Course()
    y = Course("DSCS", 5679, "To the left", "Everything you own")
    y.add_prereq(x)
    assert y.prerequisites == set([x])


# adding a object that is not a course should do nothing
def test_add_prereq_type():
    x = Course()
    x.add_prereq(5)
    assert x.prerequisites == set()
