#! python3
# import time  
from curriculum import Course, Curriculum


def printbreak(): print("----------")


def main():
    x = Course() 
    y = Course("DSCS", 3456, "To the Left", 
               "Everything you own in a box to the Left", [x])  
    case_western = Curriculum("Case Western", course_list=[x])
    case_western.add_course(y)
    case_western.print_all()


if __name__ == "__main__":
    main()
