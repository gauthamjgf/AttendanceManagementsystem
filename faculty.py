import pymongo
from PyQt5 import QtWidgets, uic, QtCore
import sys
from datetime import datetime

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
attendance = mydb["attendance"]
notifications = mydb["notifications"]


class Faculty:
    def __init__(self, username):
        self.__username = username
        self.__Name = users.find_one({"username": username})["name"]
        self.__course = users.find_one({"username": username})["course"]
        self.__courseList = course.find_one(
            {"course": self.__course})["courseList"]
        self.__courseName = course.find_one(
            {"course": self.__course})["courseName"]
        self.__subject = users.find_one({"username": username})["subject"]
    
    def getUsername(self):
        return self.__username
    
    def getName(self):
        return self.__Name
    
    def getCourse(self):
        return self.__course
    
    def getSubject(self):
        return self.__subject
    
    def getCourseList(self):
        return self.__courseList
    
    def getCourseName(self):
        return self.__courseName

class Ui(QtWidgets.QMainWindow):
    # Custom signal for sending username and password
    login_signal = QtCore.pyqtSignal(str, str)

    def __init__(self):
        super(Ui, self).__init__()
        uic.loadUi('uifiles/faculty.ui', self)

        # Page 1: Homepage
        # Welcoming
        self.Welcome = self.findChild(QtWidgets.QLabel, 'WelcomeLabel')
        self.Welcome.setText(
            "Welcome, " + fac.getName() + "!")
        # Time
        self.Time = self.findChild(QtWidgets.QLCDNumber, 'Time')
        time = QtCore.QTime.currentTime()
        self.Time.display(time.toString('hh:mm'))

        # Page 2: Upload Attendance

        faccourse = fac.getCourse()

        studnames = list(users.find(
            {"course": faccourse, "userType": "student"}, {"name": 1, "_id": 0}))
        names = []
        for i in studnames:
            names.append(i["name"])

        # Get the grid layout from the "Upload attendance" tab
        upload_attendance_layout = self.tab_2.findChild(
            QtWidgets.QGridLayout, "gridLayout")

        if upload_attendance_layout is not None:
            self.checkboxes = []
            num_columns = 3 

            for name in names:
                i = names.index(name)
                checkbox = QtWidgets.QCheckBox(name)
                self.checkboxes.append(checkbox)
                row = i // num_columns
                col = i % num_columns
                upload_attendance_layout.addWidget(checkbox, row, col)

        self.AttendanceSubmit = self.findChild(
            QtWidgets.QPushButton, 'AttendanceSubmit')
        self.AttendanceSubmit.clicked.connect(self.AttendancePress)

        # Page 3.1: Check Class Attendance
        self.classAttendanceDate= self.findChild(QtWidgets.QDateEdit, 'classAttendanceDate')
        self.classAttendanceDate.setDate(QtCore.QDate.currentDate())
        self.classAttendanceSubmit= self.findChild(QtWidgets.QPushButton, 'classAttendanceSubmit')
        self.classAttendanceSubmit.clicked.connect(self.classAttendanceCheck)
        self.classAttendanceShow= self.findChild(QtWidgets.QTextBrowser, 'classAttendanceShow')

        # Page 3.2 Check student attendance across all dates
        self.studentAttendanceUsername = self.findChild(QtWidgets.QLineEdit, 'studentAttendanceUsername')
        self.studentAttendanceSubmit = self.findChild(QtWidgets.QPushButton, 'studentAttendanceSubmit')
        self.studentAttendanceSubmit.clicked.connect(self.studentAttendanceCheck)
        self.studentAttendanceShow = self.findChild(QtWidgets.QTextBrowser, 'studentAttendanceShow')

        # Page 4: Send Notifications

        self.MessageArea= self.findChild(QtWidgets.QTextEdit, 'MessageArea')
        self.UsernameSend= self.findChild(QtWidgets.QLineEdit, 'UsernameSend')

        self.NotificationSubmit= self.findChild(QtWidgets.QPushButton, 'NotificationSubmit')
        self.NotificationSubmit.clicked.connect(self.NotificationPress)
        self.notificationAck= self.findChild(QtWidgets.QLabel, 'notificationAck')

        # Page 5: Notifications
        self.NotificationShow()
        self.NotificationRefresh= self.findChild(QtWidgets.QPushButton, 'NotificationRefresh')
        self.NotificationRefresh.clicked.connect(self.NotificationShow)
        self.NotificationClear= self.findChild(QtWidgets.QPushButton, 'NotificationClear')
        self.NotificationClear.clicked.connect(self.NotificationClearPress)
        self.notificationsWindow = self.findChild(QtWidgets.QTextBrowser, 'notificationsWindow')
        self.NotificationRefresh.clicked.connect(self.NotificationShow)

        self.show()

    def AttendancePress(self):
        faccourse = fac.getCourse()
        subject = fac.getSubject()
        studnames = list(users.find(
            {"course": faccourse,"userType":"student"}, {"username": 1, "_id": 0}))
        usernames = []
        for i in studnames:
            usernames.append(i["username"])
        attendance_list = []
        for i in range(len(self.checkboxes)):
            if self.checkboxes[i].isChecked():
                attendance_list.append(usernames[i])
        date = datetime.now().strftime("%d-%m-%Y")
        attendance.update_one({"course": faccourse, "date": date}, {
                              "$set": {subject: attendance_list}}, upsert=True)
        self.AttendanceSubmit.setText("Attendance Uploaded")

    def classAttendanceCheck(self):
        faccourse = fac.getCourse()
        date = self.classAttendanceDate.date().toString('dd-MM-yyyy')
        subject = fac.getSubject()
        try:
            attendance_list = attendance.find_one({"course": faccourse, "date": date})[subject]
        except TypeError:
            self.classAttendanceShow.setText("Attendance for the given date does not exist")
            return
        studnames = list(users.find({"course": faccourse,"userType":"student"}, {"username": 1, "_id": 0}))
        names = []
        for i in studnames:
            names.append(i["username"])
        self.classAttendanceShow.setText("Name\t\tAttendance\n")
        for i in range(len(names)):
            # get the name of the student from the username
            namesofStudent = users.find_one({"username": names[i]})["name"]
            if names[i] in attendance_list:
                self.classAttendanceShow.setText(self.classAttendanceShow.toPlainText() + namesofStudent + "\t\tPresent\n")
            else:
                self.classAttendanceShow.setText(self.classAttendanceShow.toPlainText() + namesofStudent + "\t\tAbsent\n")

    def studentAttendanceCheck(self):
        faccourse = fac.getCourse()
        username = self.studentAttendanceUsername.text()
        subject = fac.getSubject()
        attendance_list = list(attendance.find({"course": faccourse, subject: username}))
        self.studentAttendanceShow.setText("Date\t\tAttendance\n")
        for i in attendance_list:
            self.studentAttendanceShow.setText(self.studentAttendanceShow.toPlainText() + i["date"] + "\t\tPresent\n")

    def NotificationPress(self):
        faccourse = fac.getCourse()
        message = self.MessageArea.toPlainText()
        sender_name = fac.getName()
        username = self.UsernameSend.text()
        if username:
            try:
                usertype = users.find_one({"username": username})["userType"]
            except TypeError:
                self.notificationAck.setText("Username does not exist")
                return
            if usertype == "student":
                date = datetime.now().strftime("%d-%m-%Y")
                notifications.update_one({"username": username, "course": faccourse}, {"$push": {"message": message, "sender": sender_name, "date": date}}, upsert=True)
                self.notificationAck.setText("Notification Sent")
            elif usertype=="admin":
                date = datetime.now().strftime("%d-%m-%Y")
                notifications.update_one({"username": "admin"}, {"$push": {"message": message, "sender": sender_name, "date": date}}, upsert=True)
                self.notificationAck.setText("Notification Sent")
            else:
                self.notificationAck.setText("Username does not exist")
        else:
            student_usernames = [user["username"] for user in users.find({"course": faccourse, "userType": "student"})]
            date = datetime.now().strftime("%d-%m-%Y")
            for username in student_usernames:
                notifications.update_one({"username": username, "course": faccourse}, {"$push": {"message": message, "sender": sender_name, "date": date}}, upsert=True)
            self.notificationAck.setText("Notification Sent to all students in the course")

    def NotificationShow(self):
        self.notificationsWindow.clear()
        notificationsList = list(notifications.find({"username": fac.getUsername()}))
        if len(notificationsList) == 0:
            self.notificationsWindow.append("No notifications found for this username")
            return
        try:
            self.notificationsWindow.append("Date\t\tMessage\t\tSender")
            for i in notificationsList:
                for j in range(len(i["message"])):
                    self.notificationsWindow.append(i["date"][j] + "\t\t" + i["message"][j] + "\t\t" + i["sender"][j])
        except TypeError:
            self.notificationsWindow.append("Error occurred while fetching notifications")

    def NotificationClearPress(self):
        faccourse = fac.getCourse()
        notifications.delete_many({"username": fac.getUsername(), "course": faccourse})
        self.NotificationShow()

def main_func(username):
    global fac
    fac= Faculty(username)
    app = QtWidgets.QApplication([])
    window = Ui()
    app.exec_()


if __name__ == '__main__':
    print("This file is not supposed to run in this way, exiting now")
    exit(1)
