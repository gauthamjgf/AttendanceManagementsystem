import pymongo
from PyQt5 import QtWidgets, uic, QtCore
import sys

import os
from dotenv import load_dotenv
# mongodb connect
load_dotenv()

MONGO_URL = os.getenv("MONGO_URL")
myclient = pymongo.MongoClient(MONGO_URL)
mydb = myclient["attendance"]
users = mydb["users"]
course = mydb["course"]
OD = mydb["OD"]
notifications = mydb["notifications"]


class Student:
    def __init__(self, username):
        self.__username = username
        self.__Name = users.find_one({"username": username})["name"]
        self.__course = users.find_one({"username": username})["course"]
        self.__courseList = course.find_one(
            {"course": self.__course})["courseList"]
        self.__courseName = course.find_one(
            {"course": self.__course})["courseName"]

    def getUsername(self):
        return self.__username

    def getName(self):
        return self.__Name

    def getCourse(self):
        return self.__course
    
    def getCourseList(self):
        return self.__courseList
    
    def getCourseName(self):
        return self.__courseName


class Ui(QtWidgets.QMainWindow):
    # Custom signal for sending username and password
    login_signal = QtCore.pyqtSignal(str, str)

    def __init__(self):
        super(Ui, self).__init__()
        uic.loadUi('uifiles/student.ui', self)

        # Page 1: Homepage
        # Welcoming
        self.Welcome = self.findChild(QtWidgets.QLabel, 'WelcomeLabel')
        self.Welcome.setText(
            "Welcome, " + stud.getName() + "!")

        # Time
        self.Time = self.findChild(QtWidgets.QLCDNumber, 'Time')
        time = QtCore.QTime.currentTime()
        self.Time.display(time.toString('hh:mm'))

        # Page 2: Check Attendance
        self.SubjectList = self.findChild(QtWidgets.QComboBox, 'CourseList')
        courseStudying = stud.getCourse()
        # store array of the courses received from the courseName column in the course table where course = courseStudying
        courseList = stud.getCourseList()
        courseName = stud.getCourseName()
        courses = []
        for i in range(0, len(courseList)):
            courses.append(courseName[i]+" "+courseList[i])
        for j in courses:
            self.SubjectList.addItem(j)

        self.RequestAttendance = self.findChild(
            QtWidgets.QPushButton, 'RequestAttendance')
        self.RequestAttendance.clicked.connect(self.SubjectPress)
        self.AttendanceResult = self.findChild(
            QtWidgets.QTextBrowser, 'AttendanceResult')

        # Page 3.1: OD Creation
        self.ODDate = self.findChild(QtWidgets.QDateEdit, 'ODDate')
        self.ODDate.setDate(QtCore.QDate.currentDate())
        self.ODStartTime = self.findChild(QtWidgets.QTimeEdit, 'ODStartTime')
        self.ODEndTime = self.findChild(QtWidgets.QTimeEdit, 'ODEndTime')
        self.ODReason = self.findChild(QtWidgets.QLineEdit, 'ODReason')
        self.ODSubmit = self.findChild(QtWidgets.QPushButton, 'ODSubmit')
        self.ODSubmit.clicked.connect(self.ODCreate)

        # Page 3.2: OD History
        self.ODHistoryRefresh()
        self.ODHistory = self.findChild(QtWidgets.QTextBrowser, 'ODHistory')
        self.ODRefresh = self.findChild(QtWidgets.QPushButton, 'ODRefresh')
        self.ODRefresh.clicked.connect(self.ODHistoryRefresh)

        # Page 4: Notifications
        self.NotificationShow()
        self.NotificationRefresh = self.findChild(
            QtWidgets.QPushButton, 'NotificationRefresh')
        self.NotificationRefresh.clicked.connect(self.NotificationShow)
        self.NotificationClear = self.findChild(
            QtWidgets.QPushButton, 'NotificationClear')
        self.NotificationClear.clicked.connect(self.NotificationClearer)
        self.notificationsWindow = self.findChild(
            QtWidgets.QTextBrowser, 'notificationsWindow')
        self.NotificationRefresh.clicked.connect(self.NotificationShow)

        self.show()

    def exitnow():
        exit(0)

    def SubjectPress(self):
        self.AttendanceResult.clear()
        subject = self.SubjectList.currentText()
        subject = subject[-8:]

        # Retrieve attendance for the selected subject and date
        dates = mydb.attendance.distinct("date")
        self.AttendanceResult.append("Date\t\tAttendance\n")
        for date in dates:
            try:
                attendance = mydb.attendance.find_one({"date": date})[subject]
            except KeyError:
                continue
            nameofuser = stud.getUsername()
            if nameofuser in attendance:
                self.AttendanceResult.append("{}\t\tPresent\n".format(date))
            else:
                self.AttendanceResult.append("{}\t\tAbsent\n".format(date))

    def ODCreate(self):
        # Check if all fields are entered
        if not self.ODDate.date() or not self.ODStartTime.time() or not self.ODEndTime.time() or not self.ODReason.text():
            self.ODAck.setText("Please fill all the fields")
            return

        try:
            # Get the last ODid from the database and increment it by 1
            last_ODid = OD.find_one(
                sort=[("ODid", pymongo.DESCENDING)])["ODid"]
            ODid = last_ODid + 1
        except TypeError:
            # If the table is empty, set ODid to 1
            ODid = 1

        date = str(self.ODDate.date().toPyDate())
        startTime = str(self.ODStartTime.time().toPyTime())
        endTime = str(self.ODEndTime.time().toPyTime())
        reason = str(self.ODReason.text())
        accepted = -1
        course = str(stud.getCourse())
        OD.insert_one({"ODid": ODid, "username": stud.getUsername(), "course": course, "date": date, "startTime": startTime,
                       "endTime": endTime, "reason": reason, "accepted": accepted})
        self.ODAck.setText("OD created successfully")

    def ODHistoryRefresh(self):
        self.ODHistory.clear()
        ODList = list(OD.find({"username": stud.getUsername()}))
        if len(ODList) == 0:
            self.ODHistory.append("No ODs found for this username")
            return
        try:
            self.ODHistory.append(
                "ODid\tDate\tStart Time\tEnd Time\tReason\tStatus")
            for i in ODList:
                if i["accepted"] == -1:
                    accepted_str = "Not Checked"
                elif i["accepted"] == 0:
                    accepted_str = "Declined"
                else:
                    accepted_str = "Accepted"
                self.ODHistory.append(str(i["ODid"]) + "\t" + i["date"] + "\t" + i["startTime"] +
                                      "\t" + i["endTime"] + "\t" + i["reason"] + "\t" + accepted_str+"\n")
        except TypeError:
            self.ODHistory.append("Error occurred while fetching ODs")

    def NotificationShow(self):
        self.notificationsWindow.clear()
        notificationsList = list(
            notifications.find({"username": stud.getUsername()}))
        if len(notificationsList) == 0:
            self.notificationsWindow.append(
                "No notifications found for this username")
            return
        try:
            self.notificationsWindow.append("Date\t\tMessage\t\tSender")
            for i in notificationsList:
                for j in range(len(i["message"])):
                    self.notificationsWindow.append(
                        i["date"][j] + "\t\t" + i["message"][j] + "\t\t" + i["sender"][j]+"\n")
        except TypeError:
            self.notificationsWindow.append(
                "Error occurred while fetching notifications")

    def NotificationClearer(self):
        notifications.delete_many({"username": stud.getUsername()})
        self.NotificationShow()


def main_func(username):
    global stud
    stud = Student(username)
    app = QtWidgets.QApplication([])
    window = Ui()
    app.exec_()


if __name__ == '__main__':
    print("This file is not supposed to run in this way, exiting now")
    exit(1)