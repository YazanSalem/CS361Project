# createCourse(courseName, courseTime, courseDays, courseHours, courseInstructor, courseTA)
# editCourse(courseName, courseTime, courseDays, courseHours, courseInstructor, courseTa)
# deleteCourse(courseName)
# populateSearchClass(searchPromp)  should change class to course
# displayAllCourse()
from TAScheduler.models import Course
from TAScheduler.models import UserProfile


class CourseManagement(object):

    # Preconditions: The user has to have been instantiated.
    # The user must be of type administrator
    # Postconditions:Creates a course
    # Side-effects: Course is created and added inside the database
    # Course Name(in) - Name of the course
    # Course Time(in) - Time of the course
    # Course Days(in) - Days of the course
    # Course Hours(in) - Hours of the course
    # Course Instructor(in) - Instructor of the course
    # Course TA(in) -TA of the course
    @staticmethod
    def createCourse(course_id, name, location, days, hours, instructor, tas=None):
        try:
            Course.objects.get(courseID=course_id)
        except Course.DoesNotExist:
            CourseManagement.inputErrorChecker(course_id, name, location, days, hours, instructor, tas)
            Course.objects.create(courseID=course_id, name=name, location=location, hours=hours, days=days,
                                  instructor=instructor)
            course = Course.objects.get(courseID=course_id)
            if not (tas is None):
                for ta in tas:
                    course.TAs.add(ta)
            return "Course was created"

    # Preconditions: The user has to have been instantiated.
    # The user must be of type administrator
    # Postconditions:Edits a course
    # Side-effects: Course is edited inside the database
    # Course Name(in) - Name of the course
    # Course Time(in) - Time of the course
    # Course Days(in) - Days of the course
    # Course Hours(in) - Hours of the course
    # Course Instructor(in) - Instructor of the course
    # Course TA(in) -TA of the course
    @staticmethod
    def editCourse(course_id, name="", location="", days="", hours="", instructor=None, tas=None):
        CourseManagement.inputErrorChecker(course_id, name, location, days, hours, instructor, tas)
        if not (Course.objects.filter(courseID=course_id).exists()):
            raise TypeError("This course does not exist")

        editedCourse = Course.objects.get(courseID=course_id)
        if not (name == ""):
            editedCourse.name = name
        if not (location == ""):
            editedCourse.location = location
        if not (hours == ""):
            editedCourse.hours = hours
        if not (days == ""):
            editedCourse.days = days
        if not (instructor is None):
            editedCourse.instructor = instructor
        if not (tas is None):
            editedCourse.TAs.clear()
            for i in tas:
                editedCourse.TAs.add(i)
        editedCourse.save()
        return "The course was successfully edited"

    # Preconditions: The user has to have been instantiated.
    # The user must be of type administrator
    # Postconditions:Deletes a course
    # Side-effects: Course is deleted and removed from the database
    # Course Name(in) - Name of the course
    @staticmethod
    def deleteCourse(course_id):
        if not (isinstance(course_id, int)):
            raise TypeError("Id entered is not of type int")

        retMsg = "Course has been successfully deleted"
        if not (Course.objects.filter(courseID=course_id).exists()):
            retMsg = "This Course being deleted does not exist"
        else:
            Course.objects.filter(courseID=course_id).delete()
        return retMsg

    # Preconditions: The user has to have been instantiated
    # The searchPrompt is an existing course assignment name
    # Postconditions: Course assignments are populated
    # Side-effects: None
    # Search Prompt(in): Course Name you are searching for
    @staticmethod
    def populateSearchClass(course_id):
        CourseManagement.inputErrorChecker(course_id=course_id)
        if not (Course.objects.filter(courseID=course_id).exists()):
            retMsg = "This course being deleted does not exist"
        else:
            retMsg = {
                'Found Course': Course.objects.get(courseID=course_id)
            }

        return retMsg

    # Preconditions: The user has to have been instantiated
    # There are courses to display
    # Postconditions: All courses are displayed
    # Side-effects: None
    @staticmethod
    def displayAllCourse():
        allCourses = Course.objects.all()

        data = {
            'All Courses': allCourses
        }

        return allCourses

    @staticmethod
    def inputErrorChecker(course_id=0, name="", location="", days="", hours="", instructor=None, tas=None):
        if not (isinstance(course_id, int)):
            raise TypeError("course_id entered is not of type int")
        if not (isinstance(name, str)):
            raise TypeError("Course name entered is not of type str")
        if not (isinstance(location, str)):
            raise TypeError("Course location entered is not of type str")
        if not (isinstance(days, str)):
            raise TypeError("Course hours entered is not of type str")
        if not (isinstance(hours, str)):
            raise TypeError("Course days entered is not of type str")
        if not (instructor is None):
            if not (isinstance(instructor, UserProfile)):
                raise TypeError("Course instructor entered is not of type User")
            if instructor.userType != "INSTRUCTOR":
                raise TypeError("Course instructor's type is not of type INSTRUCTOR")
        if not (tas is None):
            for TA in tas:
                if not (isinstance(TA, UserProfile)):
                    raise TypeError("Course TA entered is not of type User")
                if TA.userType != "TA":
                    raise TypeError("Course TA's type is not of type TA")
