from PyQt5 import QtWidgets, uic, QtCore
import sys

class Ui(QtWidgets.QMainWindow):
    login_signal = QtCore.pyqtSignal(str, str)  # Custom signal for sending username and password

    def __init__(self):
        super(Ui, self).__init__()
        uic.loadUi('uifiles/login_fail.ui', self)

        self.Username = self.findChild(QtWidgets.QLineEdit, 'Username')
        self.Password = self.findChild(QtWidgets.QLineEdit, 'Password')
        self.Login = self.findChild(QtWidgets.QPushButton, 'Login')
        self.Login.clicked.connect(self.LoginPress)

        self.Exit = self.findChild(QtWidgets.QPushButton, 'Exit')
        self.Exit.clicked.connect(self.exitnow)

        self.show()

    def LoginPress(self):
        username = str(self.Username.text())
        password = str(self.Password.text())
        self.login_signal.emit(username, password)  # Emit the custom signal with username and password
        self.close()
    
    def exitnow(self):
        exit(0)



if __name__ == '__main__':
    print("This file is not supposed to run in this way, exiting now")
    exit(1)
