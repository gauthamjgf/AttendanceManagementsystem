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

class Advisor:
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
        uic.loadUi('uifiles/advisor.ui', self)

        # Page 1: Homepage
        # Welcoming
        self.Welcome = self.findChild(QtWidgets.QLabel, 'WelcomeLabel')
        self.Welcome.setText(
            "Welcome, " + adv.getName() + "!")
        # Time
        self.Time = self.findChild(QtWidgets.QLCDNumber, 'Time')
        time = QtCore.QTime.currentTime()
        self.Time.display(time.toString('hh:mm'))

        # Page 2
        # Page 2.1: OD Requests

        self.ODGrid = self.findChild(QtWidgets.QGridLayout, 'ODGrid')
        self.ODPage = 0
        self.ODShow()
        self.ODRefresh = self.findChild(QtWidgets.QPushButton, 'ODRefresh')
        self.ODRefresh.clicked.connect(self.ODShow)

        # Page 2.2: Main Notifications
        self.NotificationShow()
        self.NotificationRefresh = self.findChild(
            QtWidgets.QPushButton, 'NotificationRefresh')
        self.notificationsWindow = self.findChild(
            QtWidgets.QTextBrowser, 'notificationsWindow')
        self.NotificationRefresh.clicked.connect(self.NotificationShow)
        self.NotificationClear= self.findChild(QtWidgets.QPushButton,'NotificationClear')
        self.NotificationClear.clicked.connect(self.NotificationClearPress)

        # Page 3: Send Notifications

        self.MessageArea = self.findChild(QtWidgets.QTextEdit, 'MessageArea')
        self.UsernameSend = self.findChild(QtWidgets.QLineEdit, 'UsernameSend')
        self.NotifyStudents = self.findChild(
            QtWidgets.QCheckBox, 'NotifyStudents')
        self.NotifyFaculty = self.findChild(
            QtWidgets.QCheckBox, 'NotifyFaculty')
        self.NotificationSubmit = self.findChild(
            QtWidgets.QPushButton, 'NotificationSubmit')
        self.NotificationSubmit.clicked.connect(self.NotificationPress)
        self.notificationAck = self.findChild(
            QtWidgets.QLabel, 'notificationAck')

        self.show()

    def clearGridLayout(self, grid_layout):
        for i in reversed(range(grid_layout.count())):
            widget = grid_layout.itemAt(i).widget()
            if widget is not None:
                widget.deleteLater()

    def ODShow(self):
        self.clearGridLayout(self.ODGrid)
        ODList = list(OD.find({"course": adv.getCourse(), "accepted": -1}))
        if len(ODList) == 0:
            self.ODGrid.addWidget(QtWidgets.QLabel("No OD requests found"))
            return
        try:
            # self.ODGrid.addWidget(QtWidgets.QLabel("Date\t\tStart Time\t\tEnd Time\t\tReason\t\tStatus"))
            for i, item in enumerate(ODList[:4]):
                username_label = QtWidgets.QLabel(f'Username: {item["username"]}\nDate: {item["date"]}\nStart Time: {
                                                  item["startTime"]}\nEnd Time: {item["endTime"]}\nReason: {item["reason"]}')
                accept_button = QtWidgets.QPushButton('Accept')
                accept_button.clicked.connect(lambda _, username=item["username"], date=item["date"], startTime=item["startTime"],
                                              endTime=item["endTime"], ODid=item["ODid"]: self.acceptOD(username, date, startTime, endTime, ODid))
                decline_button = QtWidgets.QPushButton('Decline')
                decline_button.clicked.connect(lambda _, username=item["username"], date=item["date"], startTime=item["startTime"],
                                               endTime=item["endTime"], ODid=item["ODid"]: self.declineOD(username, date, startTime, endTime, ODid))

                self.ODGrid.addWidget(username_label, i, 0)  # First column
                self.ODGrid.addWidget(accept_button, i, 1)    # Second column
                self.ODGrid.addWidget(decline_button, i, 2)   # Third column
        except TypeError:
            print("Error occurred while fetching OD requests")

    def acceptOD(self, username, date, startTime, endTime, ODid):
        OD.update_one({"ODid": ODid, "username": username, "date": date, "startTime": startTime,
                      "endTime": endTime}, {"$set": {"accepted": 1}})

        # Create a notification for the faculty member
        faculty_course = adv.getCourse()
        user = users.find_one({"username": username})
        notification_text = f"OD Request of {user['name']} for {date} \nfrom {
            startTime} to {endTime} has been \naccepted. Proceed to mark attendance."
        faculty_usernames = [user["username"] for user in users.find(
            {"course": faculty_course, "userType": "faculty"})]
        date = datetime.now().strftime("%d-%m-%Y")
        advisor_name = adv.getName()
        for username in faculty_usernames:
            notifications.update_one({"username": username, "course": faculty_course}, {
                "$push": {"message": notification_text, "sender": advisor_name, "date": date}}, upsert=True)

        self.ODShow()

    def declineOD(self, username, date, startTime, endTime,ODid):
        OD.update_one({"ODid": ODid, "username": username, "date": date, "startTime": startTime,
                      "endTime": endTime}, {"$set": {"accepted": 0}})
        self.ODShow()

    def NotificationPress(self):
        faccourse = adv.getCourse()
        message = self.MessageArea.toPlainText()
        sender_name = adv.getName()
        username = self.UsernameSend.text()
        notify_students = self.NotifyStudents.isChecked()
        notify_faculty = self.NotifyFaculty.isChecked()

        if not message:
            self.notificationAck.setText("Please enter a message")
            return

        if username and (notify_students or notify_faculty):
            self.notificationAck.setText(
                "Please select only one group of people to notify")
            return

        if notify_students and notify_faculty:
            student_usernames = [user["username"] for user in users.find(
                {"course": faccourse, "userType": "student"})]
            faculty_usernames = [user["username"] for user in users.find(
                {"course": faccourse, "userType": "faculty"})]
            date = datetime.now().strftime("%d-%m-%Y")
            for username in student_usernames + faculty_usernames:
                notifications.update_one({"username": username, "course": faccourse}, {
                                         "$push": {"message": message, "sender": sender_name, "date": date}}, upsert=True)
            self.notificationAck.setText(
                "Notification Sent to all students and faculty in the course")
            return

        if username:
            try:
                usertype = users.find_one({"username": username})["userType"]
            except TypeError:
                self.notificationAck.setText("Username does not exist")
                return
            if usertype == "student" or usertype == "faculty" or usertype == "admin":
                date = datetime.now().strftime("%d-%m-%Y")
                notifications.update_one({"username": username, "course": faccourse}, {
                                         "$push": {"message": message, "sender": sender_name, "date": date}}, upsert=True)
                self.notificationAck.setText("Notification Sent")
            else:
                self.notificationAck.setText("Username does not exist")
        elif notify_students:
            student_usernames = [user["username"] for user in users.find(
                {"course": faccourse, "userType": "student"})]
            date = datetime.now().strftime("%d-%m-%Y")
            for username in student_usernames:
                notifications.update_one({"username": username, "course": faccourse}, {
                                         "$push": {"message": message, "sender": sender_name, "date": date}}, upsert=True)
            self.notificationAck.setText(
                "Notification Sent to all students in the course")
        elif notify_faculty:
            faculty_usernames = [user["username"] for user in users.find(
                {"course": faccourse, "userType": "faculty"})]
            date = datetime.now().strftime("%d-%m-%Y")
            for username in faculty_usernames:
                notifications.update_one({"username": username, "course": faccourse}, {
                                         "$push": {"message": message, "sender": sender_name, "date": date}}, upsert=True)
            self.notificationAck.setText(
                "Notification Sent to all faculty in the course")
        elif notify_students and notify_faculty:
            student_usernames = [user["username"] for user in users.find(
                {"course": faccourse, "userType": "student"})]
            faculty_usernames = [user["username"] for user in users.find(
                {"course": faccourse, "userType": "faculty"})]
            date = datetime.now().strftime("%d-%m-%Y")
            for username in student_usernames + faculty_usernames:
                notifications.update_one({"username": username, "course": faccourse}, {
                                         "$push": {"message": message, "sender": sender_name, "date": date}}, upsert=True)
            self.notificationAck.setText(
                "Notification Sent to all students and faculty in the course")
            return
        else:
            self.notificationAck.setText(
                "Please select a group of people to notify")

    def NotificationShow(self):
        self.notificationsWindow.clear()
        notificationsList = list(
            notifications.find({"username": adv.getUsername()}))
        if len(notificationsList) == 0:
            self.notificationsWindow.append(
                "No notifications found for this username")
            return
        try:
            self.notificationsWindow.append("Date\t\tMessage\t\tSender")
            for i in notificationsList:
                for j in range(len(i["message"])):
                    self.notificationsWindow.append(
                        i["date"][j] + "\t\t" + i["message"][j] + "\t\t" + i["sender"][j])
        except TypeError:
            self.notificationsWindow.append(
                "Error occurred while fetching notifications")
    
    def NotificationClearPress(self):
        notifications.delete_many({"username": adv.getUsername()})
        self.NotificationShow()


def main_func(username):
    global adv
    adv= Advisor(username)
    app = QtWidgets.QApplication([])
    window = Ui()
    app.exec_()


if __name__ == '__main__':
    print("This file is not supposed to run in this way, exiting now")
    exit(1)
