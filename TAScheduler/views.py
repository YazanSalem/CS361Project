from django.shortcuts import render, redirect
from django.views import View
from .models import *
from TAScheduler.Management.UserManagement import UserManagement
from TAScheduler.Management.CourseManagement import CourseManagement
from TAScheduler.Management.LabManagement import LabManagement
from django.utils.datastructures import MultiValueDictKeyError


# Create your views here.
# A method to check if a user is allowed to view a certain webpage based on their userType. Included a check for if
# the user is not logged in
# request: The request of the current user. From this we can get the user's name using request.session["name"]
# valid_types: A list of all the types allowed to access the page. Should be all caps.
def userAllowed(request, valid_types):
    isValid = True
    try:
        if not (UserManagement.findUser(username=request.session["username"]).userType in valid_types):
            isValid = False
    except TypeError:
        isValid = False
    return isValid


class Login(View):
    @staticmethod
    def get(request):
        request.session["username"] = ""
        request.session["user_type"] = ""
        request.session["user_id"] = None
        return render(request, "login.html")

    @staticmethod
    def post(request):
        noUser = False
        incorrectPassword = False
        checkUser = UserProfile
        try:
            # checks to see if a user with the given name exists
            checkUser = UserManagement.findUser(username=request.POST["useraccount"])
            # if the name does exist, checks if the password is correct and sets incorrectPassword accordingly
            incorrectPassword = (checkUser.password != request.POST['password'])
        except TypeError:
            # if there is no user with the given name, an exception is thrown, in which case, noUser is set to true
            noUser = True
        if noUser:
            # if the username does not yet exist, the user is returned to the login page.
            # a message field would be a good thing to implement so the reason login was not completed is explained
            # to the user
            return render(request, "login.html")
        elif incorrectPassword:
            # if the password is incorrect for the given name, the user is returned to the login page
            # a message field would be a good thing to implement so the reason login was not completed is explained
            # to the user
            return render(request, "login.html")
        else:
            # if no issues are found, the user is redirected and the request.session["username"] field is set to the
            # username of the user
            request.session["username"] = checkUser.username
            request.session["user_type"] = checkUser.userType
            request.session["user_id"] = checkUser.userID
            return redirect("/home/")


class Home(View):
    @staticmethod
    def get(request):
        # If the user does not have a valid name, I.E. if they try to manually enter /home in the search bar,
        # they will fail the userAllowed test and be redirected back to the login page
        # If the user is allowed then home is rendered like normal
        if userAllowed(request, ["SUPERVISOR", "INSTRUCTOR", "TA"]):
            return render(request, "home.html", {"request.session.username": request.session["username"]})
        else:
            return redirect("/../")


class ViewSchedule(View):
    @staticmethod
    def get(request):
        # If the user does not have a valid name, I.E. if they try to manually enter /home in the search bar,
        # they will fail the userAllowed test and be redirected back to the login page
        # If the user is allowed then home is rendered like normal
        if userAllowed(request, ["INSTRUCTOR"]):

            return render(request, "schedule.html", {"object_list": UserProfile.objects.get(userID=request.session["user_id"]).getCourseLabList()})

        else:
            return redirect("/../")


class SendMsg(View):
    @staticmethod
    def get(request):
        # If the user does not have a valid name, I.E. if they try to manually enter /home in the search bar,
        # they will fail the userAllowed test and be redirected back to the login page
        # If the user is allowed then home is rendered like normal
        if userAllowed(request, ["SUPERVISOR", "INSTRUCTOR", "TA"]):
            return render(request, "sendmsg.html", {"request.session.username": request.session["username"]})
        else:
            return redirect("/../")


class CreateUser(View):
    @staticmethod
    def get(request):
        # If the user does not have a valid name or if they are not of the type SUPERVISOR, they will fail
        # userAllowed and will be redirected to home
        if userAllowed(request, ["SUPERVISOR"]):
            return render(request, "createuser.html", {})
        else:
            return redirect("/../home/")

    @staticmethod
    def post(request):
        # Takes user input of all parameters and creates a new user.
        UserManagement.createUser(user_id=request.POST["userID"], user_type=request.POST["userType"],
                                  username=request.POST["username"], password=request.POST["password"],
                                  name=request.POST["name"], address=request.POST["address"],
                                  phone=request.POST["phone"], email=request.POST["email"])
        return render(request, "createuser.html")


class CreateCourse(View):
    @staticmethod
    def get(request):
        # If the user does not have a valid name or if they are not of the type SUPERVISOR, they will fail
        # userAllowed and be redirected to home
        if userAllowed(request, ['SUPERVISOR']):
            return render(request, "createcourse.html", {"UserProfile_list": UserProfile.objects.all()})
        else:
            return redirect("/../home/")

    @staticmethod
    def post(request):
        # Takes user input of all parameters and creates a new course.
        gottenTAs = request.POST.getlist("TAs")

        for i in range(len(gottenTAs)):
            gottenTAs[i] = int(gottenTAs[i])
            gottenTAs[i] = UserProfile.objects.get(userID=gottenTAs[i])
        gottenDays = request.POST.getlist("days")
        days = ""
        for i in range(len(gottenDays)):
            if i < len(gottenDays) - 1:
                days = days + gottenDays[i] + ', '
            else:
                days = days + gottenDays[i]
        CourseManagement.createCourse(course_id=int(request.POST['ID']), name=request.POST['name'],
                                      location=request.POST['location'], hours=request.POST['hours'],
                                      days=days,
                                      instructor=UserProfile.objects.get(userID=int(request.POST['instructor'])),
                                      tas=gottenTAs)
        return render(request, "createcourse.html", {"UserProfile_list": UserProfile.objects.all()})


class AccountSettings(View):
    @staticmethod
    def get(request):
        # If the user does not have a valid name, I.E. if they try to manually enter /home in the search bar,
        # they will fail the userAllowed test and be redirected back to the login page
        # If the user is allowed then home is rendered like normal
        if userAllowed(request, ["SUPERVISOR", "INSTRUCTOR", "TA"]):
            return render(request, "accountsettings.html",
                          {"user": UserProfile.objects.get(username=request.session["username"])})
        else:
            return redirect("/../home")

    @staticmethod
    def post(request):
        edit = True
        try:
            edit_or_submit = request.POST["edit"]
        except MultiValueDictKeyError:
            edit_or_submit = request.POST["submit"]
            edit = False
        if edit:
            change_user = UserManagement.findUser(username=edit_or_submit)
            return render(request, "accountsettings.html",
                          {"user": UserProfile.objects.get(username=request.session["username"]),
                           "change_user": change_user})
        else:
            UserManagement.editUser(user_id=UserManagement.findUser(username=edit_or_submit).userID,
                                    user_type=request.POST["userType"],
                                    username=edit_or_submit,
                                    password=request.POST["password"], name=request.POST["name"],
                                    address=request.POST["address"], phone=request.POST["phone"],
                                    email=request.POST["email"])
            return render(request, "accountsettings.html",
                          {"user": UserProfile.objects.get(username=request.session["username"])})


class EditUser(View):
    @staticmethod
    def get(request):
        # If the user does not have a valid name, I.E. if they try to manually enter /home in the search bar,
        # they will fail the userAllowed test and be redirected back to the login page
        # If the user is allowed then home is rendered like normal
        if userAllowed(request, ["SUPERVISOR"]):
            return render(request, "edituser.html", {"object_list": UserProfile.objects.all()})
        else:
            return redirect("/../home/")

    @staticmethod
    def post(request):
        edit = True
        try:
            edit_or_submit = request.POST["edit"]
        except MultiValueDictKeyError:
            edit_or_submit = request.POST["submit"]
            edit = False
        if edit:
            change_user = UserManagement.findUser(username=edit_or_submit)
            return render(request, "edituser.html",
                          {"object_list": UserProfile.objects.all(), "change_user": change_user})
        else:
            UserManagement.editUser(user_id=UserManagement.findUser(username=edit_or_submit).userID,
                                    user_type=request.POST["type"], username=edit_or_submit,
                                    password=request.POST["password"], name=request.POST["name"],
                                    address=request.POST["address"], phone=request.POST["phone"],
                                    email=request.POST["email"])
            return render(request, "edituser.html", {"object_list": UserProfile.objects.all()})


class EditCourse(View):
    @staticmethod
    def get(request):
        # If the user does not have a valid name, I.E. if they try to manually enter /home in the search bar,
        # they will fail the userAllowed test and be redirected back to the login page
        # If the user is allowed then home is rendered like normal
        if userAllowed(request, ["SUPERVISOR"]):
            return render(request, "editcourse.html", {"Course_list": Course.objects.all()})
        else:
            return redirect("/../home/")

    @staticmethod
    def post(request):
        edit = True
        try:
            edit_or_submit = request.POST["edit"]
        except MultiValueDictKeyError:
            edit_or_submit = request.POST["submit"]

            edit = False

        if edit:
            change_course = CourseManagement.findCourse(int(edit_or_submit))
            return render(request, "editcourse.html",
                          {"Course_list": Course.objects.all(), "change_course": change_course,
                           "UserProfile_list": UserProfile.objects.all()})
        else:
            gottenTAs = request.POST.getlist("TAs")
            for i in range(len(gottenTAs)):
                gottenTAs[i] = int(gottenTAs[i])
                gottenTAs[i] = UserProfile.objects.get(userID=gottenTAs[i])
            gottenDays = request.POST.getlist("days")
            days = ""
            for i in range(len(gottenDays)):
                if i < len(gottenDays) - 1:
                    days = days + gottenDays[i] + ', '
                else:
                    days = days + gottenDays[i]
            change_course = CourseManagement.findCourse(courseID=int(edit_or_submit))
            CourseManagement.editCourse(int(change_course.courseID), name=request.POST["name"],
                                        location=request.POST["location"], days=days,
                                        hours=request.POST["hours"],
                                        instructor=UserProfile.objects.get(userID=int(request.POST["instructor"])),
                                        tas=gottenTAs)

            return render(request, "editcourse.html", {"Course_list": Course.objects.all()})


class DeleteLab(View):
    @staticmethod
    def get(request):
        # If the user does not have a valid name, I.E. if they try to manually enter /home in the search bar,
        # they will fail the userAllowed test and be redirected back to the login page
        # If the user is allowed then home is rendered like normal
        if userAllowed(request, ["SUPERVISOR"]):
            return render(request, "deletelab.html", {"lab_list": Lab.objects.all()})
        else:
            return redirect("/../home/")

    @staticmethod
    def post(request):
        LabManagement.deleteLab(lab_id=int(request.POST["delete"]))
        return render(request, "deletelab.html", {"lab_list": Lab.objects.all()})


class DeleteCourse(View):
    @staticmethod
    def get(request):
        # If the user does not have a valid name, I.E. if they try to manually enter /home in the search bar,
        # they will fail the userAllowed test and be redirected back to the login page
        # If the user is allowed then home is rendered like normal
        if userAllowed(request, ["SUPERVISOR"]):
            return render(request, "deletecourse.html", {"course_list": Course.objects.all()})
        else:
            return redirect("/../home/")

    @staticmethod
    def post(request):
        CourseManagement.deleteCourse(course_id=int(request.POST["delete"]))
        return render(request, "deletecourse.html", {"course_list": Course.objects.all()})


class DeleteUser(View):
    @staticmethod
    def get(request):
        # If the user does not have a valid name, I.E. if they try to manually enter /home in the search bar,
        # they will fail the userAllowed test and be redirected back to the login page
        # If the user is allowed then home is rendered like normal
        if userAllowed(request, ["SUPERVISOR"]):
            return render(request, "deleteuser.html", {"user_list": UserProfile.objects.all()})
        else:
            return redirect("/../home/")

    @staticmethod
    def post(request):
        UserManagement.deleteUser(user_id=int(request.POST["delete"]))
        return render(request, "deleteuser.html", {"user_list": UserProfile.objects.all()})


class CreateLab(View):
    @staticmethod
    def get(request):
        # If the user does not have a valid name, I.E. if they try to manually enter /home in the search bar,
        # they will fail the userAllowed test and be redirected back to the login page
        # If the user is allowed then home is rendered like normal
        if userAllowed(request, ["SUPERVISOR"]):
            return render(request, "createlab.html",
                          {"Course_list": Course.objects.all(), "UserProfile_list": UserProfile.objects.all()})
        else:
            return redirect("/../home/")

    @staticmethod
    def post(request):
        gottenDays = request.POST.getlist("labDays")
        days = ""
        for i in range(len(gottenDays)):
            if i < len(gottenDays) - 1:
                days = days + gottenDays[i] + ', '
            else:
                days = days + gottenDays[i]
        LabManagement.createLab(int(request.POST['labID']), request.POST['labName'],
                                request.POST['labHours'], request.POST['labLocation'], days,
                                Course.objects.get(courseID=request.POST['course']),
                                UserProfile.objects.get(userID=request.POST['labTA']))
        return render(request, "createlab.html",
                      {"Course_list": Course.objects.all(), "UserProfile_list": UserProfile.objects.all()})


class EditLab(View):
    @staticmethod
    def get(request):
        # If the user does not have a valid name, I.E. if they try to manually enter /home in the search bar,
        # they will fail the userAllowed test and be redirected back to the login page
        # If the user is allowed then home is rendered like normal
        if userAllowed(request, ["SUPERVISOR"]):
            return render(request, "editlab.html", {"object_list": Lab.objects.all()})
        else:
            return redirect("/../home/")

    @staticmethod
    def post(request):
        edit = True
        try:
            edit_or_submit = int(request.POST["edit"])
        except MultiValueDictKeyError:
            edit_or_submit = int(request.POST["submit"])
            edit = False
        if edit:
            change_lab = Lab.objects.get(labID=edit_or_submit)
            return render(request, "editlab.html",
                          {"object_list": Lab.objects.all(), "Course_list": Course.objects.all(),
                           "UserProfile_list": UserProfile.objects.all(), "change_lab": change_lab})
        else:
            gottenDays = request.POST.getlist("days")
            days = ""
            for i in range(len(gottenDays)):
                if i < len(gottenDays) - 1:
                    days = days + gottenDays[i] + ', '
                else:
                    days = days + gottenDays[i]
            LabManagement.editLab(lab_id=int(Lab.objects.get(labID=edit_or_submit).labID),
                                  lab_name=request.POST["name"], lab_location=request.POST["location"],
                                  lab_hours=request.POST["hours"], lab_days=days,
                                  course=Course.objects.get(courseID=request.POST["course"]),
                                  ta=UserManagement.findUser(user_id=request.POST["TA"]))
            return render(request, "editlab.html", {"object_list": Lab.objects.all()})


class EditLabForInstructors(View):
    @staticmethod
    def get(request):
        if userAllowed(request, ["INSTRUCTOR"]):
            instructor_labs = []
            for lab in Lab.objects.all():
                if lab.course.instructor.userID == int(request.session["user_id"]):
                    instructor_labs.append(lab)
            return render(request, "editlab_forinstructors.html", {"object_list": instructor_labs})
        else:
            return redirect("/../home")

    @staticmethod
    def post(request):
        instructor_labs = []
        instructor_tas = []
        for lab in Lab.objects.all():
            if lab.course.instructor.userID == int(request.session["user_id"]):
                instructor_labs.append(lab)
        for user in UserProfile.objects.all():
            for course in user.TAToCourse.all():
                if course.instructor.userID == request.session["user_id"]:
                    instructor_tas.append(user)
                    break
        try:
            this_lab_id = int(request.POST["edit"])
        except MultiValueDictKeyError:
            this_lab_id = int(request.POST["submit"])
            LabManagement.editLab(lab_id=this_lab_id, ta=UserManagement.findUser(user_id=int(request.POST["TA"])))
            return render(request, "editlab_forinstructors.html", {"object_list": instructor_labs})
        change_lab = Lab.objects.get(labID=this_lab_id)
        return render(request, "editlab_forinstructors.html",
                      {"object_list": instructor_labs, "UserProfile_list": instructor_tas, "change_lab": change_lab})


class ViewUser(View):
    @staticmethod
    def get(request):
        # If the user does not have a valid name, I.E. if they try to manually enter /home in the search bar,
        # they will fail the userAllowed test and be redirected back to the login page
        # If the user is allowed then home is rendered like normal
        if userAllowed(request, ["SUPERVISOR", "INSTRUCTOR", "TA"]):
            return render(request, "viewuser.html", {"user_list": UserProfile.objects.all()})
        else:
            return redirect("/../")


class AssignTa(View):
    @staticmethod
    def get(request):
        # If the user does not have a valid name, I.E. if they try to manually enter /home in the search bar,
        # they will fail the userAllowed test and be redirected back to the login page
        # If the user is allowed then home is rendered like normal
        if userAllowed(request, ["SUPERVISOR", "INSTRUCTOR", "TA"]):
            return render(request, "assignTA.html", {"object_list": Lab.objects.all(), "Course_list": Course.objects.all()})
        else:
            return redirect("/../home/")


class ClassSchedules(View):
    pass


class ClassLabManagement(View):
    pass


class CourseTAAssignments(View):
    pass


class UserList(View):
    pass


class AccountCreation(View):
    pass


class ClassList(View):
    pass


class CourseCreation(View):
    pass


class LabList(View):
    pass


class CourseAssignments(View):
    pass


class TAList(View):
    pass
