import mysql.connector
import sys
import os
import re
import Extract
from Scripts.UVAObjects.Course import Course

config_directory = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(config_directory)

import config
connection = None
cursor = None

def connect():
    # Establish a connection to the MySQL server
    global connection, cursor
    connection = mysql.connector.connect(
        host = config.host,
        user = config.user,
        password = config.password,
        database = config.database
    )
    cursor = connection.cursor()
    return connection

def createTables():
    global connection, cursor
    if connection == None or cursor == None:
        return "Not Connected to the Database"
    else:
        createTables_relative_path = "SQL_Scripts/CreateTables.sql"
        createTables_script = os.path.join(os.getcwd(), createTables_relative_path)

        for line in open(createTables_script):
            cursor.execute(line)

def addCollege(college_name):
    global connection, cursor
    if connection == None or cursor == None:
        return "Not Connected to the Database"
    elif not table_exists("Colleges"):
        return "Colleges Table does not exist"
    try:
        statement = f"INSERT INTO {config.database}.Colleges(college_name) VALUES('{college_name}')"
        cursor.execute(statement)
        
        connection.commit()
    except mysql.connector.Error as err:
        print(f"Error: {err}")

def addDepartment(department_name, college_name):
    global connection, cursor
    if connection == None or cursor == None:
        return "Not Connected to the Database"
    elif not table_exists("Colleges") and not table_exists("Departments"):
        return "Colleges Table does not exist"
    try:
        query = f"SELECT id FROM {config.database}.Colleges WHERE college_name = '{college_name}';"
        cursor.execute(query)
        result = cursor.fetchone()[0]

        statement = f"INSERT INTO {config.database}.Departments(department_name, college) VALUES('{department_name}','{result}')"
        cursor.execute(statement)
        
        connection.commit()
    except mysql.connector.Error as err:
        print(f"Error: {err}")
    
def addCourse(course, department_name):
    global connection, cursor
    if connection == None or cursor == None:
        return "Not Connected to the Database"
    elif not table_exists("Colleges"):
        return "Colleges Table does not exist"
    try:
        if (course == None):
            return
        name = course.name
        course_num = course.course_num
        id = int(course.id)
        section = course.section
        class_type = course.class_type
        credits = course.credits
        availability = course.availability
        enrollment = course.enrollment
        professor = course.professor
        time = course.time
        location = course.location

        query = f"SELECT id FROM {config.database}.Departments WHERE department_name = '{department_name}';"
        cursor.execute(query)
        department_id = cursor.fetchone()[0]
        cursor.fetchall()

        statement = f"INSERT INTO {config.database}.Courses(name, course_code, course_id, section, class_type, credits, availability, enrollment_status, professor, time, location, department_id) VALUES('{name}','{course_num}',{id},'{section}','{class_type}','{credits}','{availability}','{enrollment}','{professor[0]}','{time}','{location}',{department_id})"
        cursor.execute(statement)
        
        connection.commit()
    except mysql.connector.Error as err:
        print(f"Error: {err}")

def table_exists(table_name):
    global connection, cursor
    if connection == None or cursor == None:
        return "Not Connected to the Database"
    try:
        # Query to check if the table exists in the config database
        query = f"SELECT 1 FROM information_schema.tables WHERE table_schema = '{config.database}' AND table_type = 'BASE TABLE' AND table_name = '{table_name}' LIMIT 1"

        # Execute the query
        cursor.execute(query)

        # Fetch the result
        result = cursor.fetchone()

        return result is not None  
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return False

def clear():
    global connection, cursor
    if connection == None or cursor == None:
        return "Not Connected to the Database"
    try:
        cursor.execute("SET foreign_key_checks = 0;")
        result = cursor.fetchall()
        
        cursor.execute(f"TRUNCATE TABLE {config.database}.Schedule_Interface;")
        result = cursor.fetchall()

        cursor.execute(f"TRUNCATE TABLE {config.database}.Schedule;")
        result = cursor.fetchall()

        cursor.execute(f"TRUNCATE TABLE {config.database}.Courses;")
        result = cursor.fetchall()

        cursor.execute(f"TRUNCATE TABLE {config.database}.Departments;")
        result = cursor.fetchall()

        cursor.execute(f"TRUNCATE TABLE {config.database}.Colleges;")
        result = cursor.fetchall()
        
        cursor.execute("SET foreign_key_checks = 1;")
        result = cursor.fetchall()
        return True
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return False


def fillTables():
    global connection, cursor
    if connection == None or cursor == None:
        return "Not Connected to the Database"
    if table_exists("Colleges") and table_exists("Departments") and table_exists("Courses"):
        clear()
    else:
        createTables()
        
    uva = Extract.createUVA()
    for each in uva.colleges:
        # print(each)
        addCollege(each)
        for departments in uva.colleges[each].getDepartments():
            addDepartment(departments.name, each)
            for course in departments.getCourses():
                # print(course[1])
                addCourse(course[1], departments.name)


connection = connect()
fillTables()
clear()

# Close the cursor and connection
cursor.close()
connection.close()

# print("UVA\n")
# print(uva)

# print("College of Arts Departments\n")
# print(uva.colleges['Arts & Sciences Departments'])
# print("length: ", len(uva.colleges['Arts & Sciences Departments'].departments))

# print("Courses in African American studies\n")
# aas = uva.colleges['Arts & Sciences Departments'].departments[0]
# print("length: ", len(uva.colleges['Arts & Sciences Departments'].departments[0].courses))
# print("length: ", len(uva.colleges['Arts & Sciences Departments'].departments[1].courses))
# print("length: ", len(uva.colleges['Arts & Sciences Programs, Seminars, and Institutes'].departments[0].courses))
# print(aas)

# for each in aas.courses:
#     print(each)
# temp = Course("Intro to math", "MATH 1000", "10000", "101","Lecture","3","Open","0/20","Professor Qu","TuTh 11:00am - 12:15pm", "New Cabell")
# addCourse(temp, 'African-American & African Studies')