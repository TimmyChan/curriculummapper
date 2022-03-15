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


# testing __str__() Should print subject code, course code.
def test_str():
    x = Course("SUBJ", "1234", "Course Title")
    assert str(x) == "SUBJ 1234"


# testing __repr__(self) should always print simple string as defined below
def test_repr():
    x = Course("SUBJ", "1234", "Course Title")
    assert repr(x) == "curriculum.Course(SUBJ, 1234, Course Title)"


def test_eq():
    x = Course("SUBJ", "1234")
    y = Course("SUBJ", "1234", "Yo Mama")
    assert (x == y)


# testing simple add_alias
def test_alias():
    ''' should be sorted '''
    x = Course("CSDS", 1234, "Yo Mama",
               "Needs her own zipcode")
    x.add_alias("ABCD 1234")
    assert x.alias_set == set(["ABCD 1234"])


# testing repeat add_alias (should behave as set)
def test_alias_repeat():
    ''' should return just one '''
    x = Course("CSDS", 1234, "Yo Mama")
    x.add_alias("ABCD 1234")
    x.add_alias("ABCD 1234")
    assert x.alias_set == set(["ABCD 1234"])


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


# should return a simple int
def test_get_course_code_int():
    x = Course("DATA", 1234)
    assert x.get_course_code_int() == 1234


# should return an int still
def test_get_course_code_int_tricky():
    x = Course("DATA", "1234F")
    assert x.get_course_code_int() == 1234


# appending course title with shorter string does nothing
def test_append_course_title_no_action():
    x = Course("DSCS", 5679, "To the left", "Everything you own")
    x.append_course_title("yeee")
    assert x.course_title == "To the left"


# appending longer string for course title will replace
def test_append_course_title_change():
    x = Course()
    x.append_course_title("Chocolate Star Fish")
    assert x.course_title == "Chocolate Star Fish"


# appending course title with shorter string does nothing
def test_append_course_desc_no_action():
    x = Course("DSCS", 5679, "To the left", "Everything you own")
    x.append_course_description("yeee")
    assert x.course_description == "Everything you own"


# appending longer string for course title will replace
def test_append_course_desc_change():
    x = Course()
    x.append_course_description("And the hot dog flavored water")
    assert x.course_description == "And the hot dog flavored water"


# full_desc rly just spits out a long string representation with some options
# to output lines instead of one long string.
def test_full_desc():
    x = Course()
    assert isinstance(x.full_desc(), str)

