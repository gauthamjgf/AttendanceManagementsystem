import pymongo
from PyQt5 import QtWidgets, uic, QtCore
import sys
import hashlib  # hashing package
import os
from dotenv import load_dotenv

# mongodb connect
load_dotenv()

MONGO_URL = os.getenv("MONGO_URL")

myclient = pymongo.MongoClient(MONGO_URL)
mydb = myclient["attendance"]
users = mydb["users"]
credentials = mydb["credentials"]
notifications = mydb["notifications"]

# Main functions


class Ui(QtWidgets.QMainWindow):
    # Custom signal for sending username and password
    login_signal = QtCore.pyqtSignal(str, str)

    def __init__(self):
        super(Ui, self).__init__()
        uic.loadUi('uifiles/admin.ui', self)

        # Page 1: Create user
        self.UserName = self.findChild(QtWidgets.QLineEdit, 'UserName')
        self.PassWord = self.findChild(QtWidgets.QLineEdit, 'PassWord')
        self.NameofUser = self.findChild(QtWidgets.QLineEdit, 'NameofUser')
        self.userType = self.findChild(QtWidgets.QComboBox, 'userType')
        self.Course = self.findChild(QtWidgets.QComboBox, 'Course')

        self.subjectLabel=self.findChild(QtWidgets.QLabel,'subjectLabel')
        self.subjectLabel.hide()
        self.subjectList=self.findChild(QtWidgets.QComboBox,'subjectList')
        self.subjectList.hide()
        self.userType.currentIndexChanged.connect(self.addSubjects)
        self.Course.currentIndexChanged.connect(self.addSubjects)

        self.CreateSubmit = self.findChild(
            QtWidgets.QPushButton, 'CreateSubmit')
        self.CreateSubmit.clicked.connect(self.CreateUser)
        self.CreateAck = self.findChild(QtWidgets.QLabel, 'CreateAck')

        # Page 2: Edit user
        self.EditUsername = self.findChild(QtWidgets.QLineEdit, 'EditUsername')
        self.EditPassword = self.findChild(QtWidgets.QLineEdit, 'EditPassword')
        self.EditSubmit = self.findChild(QtWidgets.QPushButton, 'EditSubmit')
        self.EditSubmit.clicked.connect(self.EditUser)
        self.EditAck = self.findChild(QtWidgets.QLabel, 'EditAck')

        # Page 3: Delete user
        self.DeleteUsername = self.findChild(
            QtWidgets.QLineEdit, 'DeleteUsername')
        self.DeleteSubmit = self.findChild(
            QtWidgets.QPushButton, 'DeleteSubmit')
        self.DeleteSubmit.clicked.connect(self.DeleteUser)

        # Page 4: Find Users
        self.FindUsername = self.findChild(QtWidgets.QLineEdit, 'FindUsername')
        self.FindName = self.findChild(QtWidgets.QLineEdit, 'FindName')
        self.FindSubmit = self.findChild(QtWidgets.QPushButton, 'FindSubmit')
        self.FindSubmit.clicked.connect(self.FindUser)

        self.FindResult = self.findChild(QtWidgets.QTextBrowser, 'FindResult')

        # Page 5: Notifications
        self.NotificationShow()
        self.NotificationRefresh= self.findChild(QtWidgets.QPushButton, 'NotificationRefresh')
        self.NotificationRefresh.clicked.connect(self.NotificationShow)
        self.NotificationClear= self.findChild(QtWidgets.QPushButton, 'NotificationClear')
        self.NotificationClear.clicked.connect(self.NotificationClearer)
        self.notificationsWindow = self.findChild(QtWidgets.QTextBrowser, 'notificationsWindow')
        self.NotificationRefresh.clicked.connect(self.NotificationShow)

        # Final Show
        self.show()

    def addSubjects(self):
        self.subjectList.clear()
        if(self.userType.currentText() == "faculty"):
            self.subjectLabel.show()
            self.subjectList.show()
            courseStudying = self.Course.currentText()
            courseList = mydb.course.find_one({"course": courseStudying})["courseList"]
            courses = []
            for i in range(0, len(courseList)):
                courses.append(courseList[i])
            for j in courses:
                self.subjectList.addItem(j)
        else:
            self.subjectLabel.hide()
            self.subjectList.hide()

    def CreateUser(self):
        if (self.UserName.text() == "admin"):
            self.CreateAck.setText("Cannot edit admin user")
            return
        else:
            try:
                user = credentials.find_one({"username": self.UserName.text()})
                if user is not None:
                    self.CreateAck.setText("Username already exists")
                else:
                    user_type = self.userType.currentText()
                    course = self.Course.currentText()
                    credentials.insert_one({"username": self.UserName.text(),"password": hashlib.sha256(self.PassWord.text().encode()).hexdigest()})
                    if user_type == "faculty":
                        subject = self.subjectList.currentText()
                        users.insert_one({"username": self.UserName.text(),"name": self.NameofUser.text(),"userType": user_type,"course": course,"subject": subject})
                    else:
                        users.insert_one({"username": self.UserName.text(),"name": self.NameofUser.text(),"userType": user_type,"course": course})
                    self.CreateAck.setText("User with username " +
                                            self.UserName.text() + " Created Successfully")
            except Exception as e:
                print(e)


    def EditUser(self):
        if (self.EditUsername.text() == "admin"):
            self.EditAck.setText("Cannot edit admin user")
        else:
            try:
                user = credentials.find_one(
                    {"username": self.EditUsername.text()})
                if user is None:
                    self.EditAck.setText("Username does not exist")
                else:
                    credentials.update_one({"username": self.EditUsername.text()}, {"$set": {
                                           "password": hashlib.sha256(self.EditPassword.text().encode()).hexdigest()}})
                    self.EditAck.setText(
                        "User with username " + self.EditUsername.text() + " Edited Successfully")
            except Exception as e:
                print(e)

    def DeleteUser(self):
        if (self.DeleteUsername.text() == "admin"):
            self.DeleteAck.setText("Cannot edit admin user")
        else:
            try:
                user = credentials.find_one(
                    {"username": self.DeleteUsername.text()})
                if user is None:
                    self.DeleteAck.setText("Username does not exist")
                else:
                    credentials.delete_one(
                        {"username": self.DeleteUsername.text()})
                    users.delete_one({"username": self.DeleteUsername.text()})
                    self.DeleteAck.setText("User with username " +
                                           self.DeleteUsername.text() + " Deleted Successfully")
            except Exception as e:
                print(e)

    def FindUser(self):
        if (self.FindUsername.text() == "admin"):
            self.FindResult.setText("Operation Not Permitted")
        else:
            # Get the search inputs
            name = self.FindName.text()
            username = self.FindUsername.text()

            # Check if both inputs are given
            if name and username:
                self.FindResult.setText("Both inputs not allowed.")
                return

            # Search for the user by name or username
            try:
                if name:
                    users_list = list(users.find({"name": name}))
                else:
                    users_list = list(users.find({"username": username}))
                type(users_list)
                if len(users_list) == 0:
                    self.FindResult.setText("User not found.")
                else:
                    # Display the user details in the FindResult text browser
                    result_text = "Username\t Name\t User Type\t Course\n"
                    for user in users_list:
                        result_text += f"{user['username']}\t {user['name']}\t {user['userType']}\t{user['course']}\n"
                    self.FindResult.setText(result_text)
            except Exception as e:
                print(e)

    def NotificationShow(self):
        self.notificationsWindow.clear()
        notificationsList = list(notifications.find({"username": "admin"}))
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

    def NotificationClearer(self):
        notifications.delete_many({"username": "admin"})
        self.NotificationShow()

    def exitnow():
        exit(0)


def main_func():
    app = QtWidgets.QApplication([])
    window = Ui()
    app.exec_()


if __name__ == '__main__':
    print("This file is not supposed to run in this way, exiting now")
    exit(1)
