import pymongo
import os
import hashlib  # hashing package

from dotenv import load_dotenv

# Login Page Modules
import loginpage
import loginpagefail
import admin
import student
import faculty
import advisor

# mongodb connect
load_dotenv()

MONGO_URL = os.getenv("MONGO_URL")

myclient = pymongo.MongoClient(MONGO_URL)
mydb = myclient["attendance"]
users = mydb["users"]
credentials = mydb["credentials"]
course = mydb["course"]

# Check if the users and credentials collections are empty
if users.count_documents({}) == 0 and credentials.count_documents({}) == 0:
    # Create admin user information
    admin_user = {"username": "admin",
                  "name": "Administrator", "userType": "admin"}
    admin_credentials = {"username": "admin", "password": "8c6976e5b5410415bde908bd4dee15dfb167a9c873fc4bb8a81f6f2ab448a918"}
    # Insert admin user information into users and credentials collections
    users.insert_one(admin_user)
    credentials.insert_one(admin_credentials)
    CYS_course_data = {"course": "CYS", "courseList": ["19CSE201", "20CYS201", "20CYS202", "20CYS203", "20CYS204", "20CYS205", "20CYS281", "22ADM201"], "courseName": ["Advanced Programming", "Optimization Techniques", "User Interface Design", "Operating Systems", "Database management system", "Modern Cryptography", "Operating Systems Lab", "Strategic Lessons of Mahabharata"]}
    course.insert_one(CYS_course_data)
    CSE_course_data={"course": "CSE", "courseList": ["19CSE201", "19CSE202", "19CSE204", "19CSE205", "19MAT201", "19MAT202", "19ECE204", "19ECE282", "22ADM201"], "courseName": ["Advanced Programming", "Database management system", "Object Oriented Programming", "Program Reasoning", "Numerical Methods", "Optimisation Techniques", "Digital Electronics and Systems", "Digital Electronics and Systems Lab", "Strategic Lessons of Mahabharata"]}
    course.insert_one(CSE_course_data)
    AIE_course_data = {"course": "AIE", "courseList": ["22AIE201", "22AIE202", "22AIE203", "22AIE204", "22AIE205", "22BIO201", "22MAT220", "22ADM201"], "courseName": ["Fundamentals of AI", "Operating Systems", "Data Structures & Algorithms 2", "Introduction to Computer Networks", "Introduction to Python", "Intelligence of Biological Systems 1", "Mathematics for computing 3", "Strategic Lessons of Mahabharata"]}
    course.insert_one(AIE_course_data)

# # check if the count of users and credentials collections are equal
# if users.count_documents({}) != credentials.count_documents({}):
#     print("Error: Users and credentials collections are not equal")
#     exit()

# check if every user in users table exists in credentials table
for user in users.find({}):
    if credentials.count_documents({"username": user["username"]}) == 0:
        print("Error: There is a problem mapping users and credentials, user in users does not exist in credentials")
        exit()

# check if every user in credntials table exists in users table
for user in credentials.find({}):
    if users.count_documents({"username": user["username"]}) == 0:
        print("Error: There is a problem mapping users and credentials, user in credentials does not exist in users")
        exit()

# Main functions

# geting username and password from the login script


def handle_login(receivedusername, receivedpassword):
    # This function is called when the login signal is emitted
    global username
    global password

    username = receivedusername
    password = receivedpassword
    # hashing the passwords
    password = hashlib.sha256(password.encode()).hexdigest()


def loggingin(libraryused):
    app = libraryused.QtWidgets.QApplication([])
    window = libraryused.Ui()
    window.login_signal.connect(handle_login)  # Connect to the custom signal
    app.exec_()
    # for exiting the program
    


def main():

    print('''
 █████╗ ████████╗████████╗███████╗███╗   ██╗██████╗  █████╗ ███╗   ██╗ ██████╗███████╗
██╔══██╗╚══██╔══╝╚══██╔══╝██╔════╝████╗  ██║██╔══██╗██╔══██╗████╗  ██║██╔════╝██╔════╝
███████║   ██║      ██║   █████╗  ██╔██╗ ██║██║  ██║███████║██╔██╗ ██║██║     █████╗  
██╔══██║   ██║      ██║   ██╔══╝  ██║╚██╗██║██║  ██║██╔══██║██║╚██╗██║██║     ██╔══╝  
██║  ██║   ██║      ██║   ███████╗██║ ╚████║██████╔╝██║  ██║██║ ╚████║╚██████╗███████╗
╚═╝  ╚═╝   ╚═╝      ╚═╝   ╚══════╝╚═╝  ╚═══╝╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═══╝ ╚═════╝╚══════╝                                                                                                 
    ''')
    print('''
                                                                                      
███╗   ███╗ █████╗ ███╗   ██╗ █████╗  ██████╗ ███████╗██████╗                         
████╗ ████║██╔══██╗████╗  ██║██╔══██╗██╔════╝ ██╔════╝██╔══██╗                        
██╔████╔██║███████║██╔██╗ ██║███████║██║  ███╗█████╗  ██████╔╝                        
██║╚██╔╝██║██╔══██║██║╚██╗██║██╔══██║██║   ██║██╔══╝  ██╔══██╗                        
██║ ╚═╝ ██║██║  ██║██║ ╚████║██║  ██║╚██████╔╝███████╗██║  ██║                        
╚═╝     ╚═╝╚═╝  ╚═╝╚═╝  ╚═══╝╚═╝  ╚═╝ ╚═════╝ ╚══════╝╚═╝  ╚═╝   
    ''')

    loggingin(loginpage)
    while True:
        try:
            serverpassword = credentials.find_one(
                {"username": username})["password"]
        except TypeError:
            print("Username does not exist")
            loggingin(loginpagefail)
            continue
        if password == serverpassword:
            print("Login successful")
            break
        else:
            print("Login failed")
            loggingin(loginpagefail)

    try:
        userType = users.find_one({"username": username})["userType"]
    except Exception as e:
        print("Error:", e)
        exit()
    if userType == "admin":
        print("You are an admin")
        admin.main_func()
    elif userType == "student":
        print("You are a student")
        student.main_func(username)
    elif userType == "faculty":
        print("You are a faculty")
        faculty.main_func(username)
    elif userType == "class_advisor":
        print("You are a Advisor")
        advisor.main_func(username)
    else:
        print("Invalid user type")

if __name__ == "__main__":  # This is the entry point of the program
    os.system('cls' if os.name == 'nt' else 'clear')
    main()
