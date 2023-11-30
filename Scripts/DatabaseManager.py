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
user = None

def connect():
    """
    Establish a connection to the MySQL server using the config file information
    Returns:
        MySQL Connection Object: This object represents the connection with the SQL server
    """
    global connection, cursor
    connection = mysql.connector.connect(
        host = config.host,
        user = config.user,
        password = config.password,
        database = config.database
    )
    cursor = connection.cursor()
    return True

def createTables():
    """
    Creates all the necessary tables (Colleges, Departments, Courses, Schedule, Schedule_Interface, Students) 
    by using the CreateTables.sql script
    Returns:
        bool: True if tables are created
    """
    global connection, cursor
    if connection == None or cursor == None:
        print("Not Connected to the Database")
        return False
    else:
        createTables_relative_path = "SQL_Scripts/CreateTables.sql"
        createTables_script = os.path.join(os.getcwd(), createTables_relative_path)

        for line in open(createTables_script):
            cursor.execute(line)
        return True

def addCollege(college_name):
    """
    add College to the Colleges table 
    Args:
        college_name (str): Name of the college to be added

    Returns:
        bool: returns True if the college was successfully added
    """
    global connection, cursor
    if connection == None or cursor == None:
        print("Not Connected to the Database")
        return False
    elif not table_exists("Colleges"):
        print("Colleges Table does not exist")
        return False
    
    try:
        statement = f"INSERT INTO {config.database}.Colleges(college_name) VALUES('{college_name}')"
        cursor.execute(statement)
        
        connection.commit()
        return True
    except mysql.connector.Error as err:
        print(f"Error: {err}")

def addDepartment(department_name, college_name):
    """
    add Department to Departments table
    Args:
        department_name (str): Name of the department
        college_name (str): Name of the college that the department is in

    Returns:
        bool: returns True if the department was successfully added
    """
    global connection, cursor
    if connection == None or cursor == None:
        print("Not Connected to the Database")
        return False
    elif not table_exists("Colleges") and not table_exists("Departments"):
        return "Colleges Table does not exist"
    
    try:
        query = f"SELECT id FROM {config.database}.Colleges WHERE college_name = '{college_name}';"
        cursor.execute(query)
        result = cursor.fetchone()[0]

        statement = f"INSERT INTO {config.database}.Departments(department_name, college) VALUES('{department_name}','{result}')"
        cursor.execute(statement)
        
        connection.commit()
        return True
    except mysql.connector.Error as err:
        print(f"Error: {err}")
    
def addCourse(course, department_name):
    """
    add Course to the Courses table
    Args:
        course (Course object): Course object that contains all the course information (eg: course id and section)
        department_name (str): Name of the department that the course is in

    Returns:
        bool: returns True if the course was successfully added 
    """
    global connection, cursor
    if connection == None or cursor == None:
        print("Not Connected to the Database")
        return False
    elif not table_exists("Colleges"):
        print("Colleges Table does not exist")
        return False
    
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

        statement = f"INSERT INTO {config.database}.Courses(name, course_code, course_id, section, class_type, credits, enrollment_status, availability, professor, time, location, department_id) VALUES('{name}','{course_num}',{id},'{section}','{class_type}','{credits}','{availability}','{enrollment}','{professor[0]}','{time}','{location}',{department_id})"
        cursor.execute(statement)
        
        connection.commit()
        return True
    except mysql.connector.Error as err:
        print(f"Error: {err}")

def table_exists(table_name):
    """
    Given the table name, check if the table exists within the SQL server
    Args:
        table_name (str): Name of the table

    Returns:
        bool: returns True if the table exists
    """
    global connection, cursor
    if connection == None or cursor == None:
        print("Not Connected to the Database")
        return False

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
    """
    Clears all of the tables except for the Student table
    Returns:
        bool: returns True if the tables were cleared
    """
    global connection, cursor
    if connection == None or cursor == None:
        print("Not Connected to the Database")
        return False

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
    """
    Fill all the tables with the most up-to-date data and create tables if they do not already exist
    Returns:
        bool: returns True if the tables are successfully refreshed
    """
    global connection, cursor
    if connection == None or cursor == None:
        print("Not Connected to the Database")
        return False     
    if table_exists("Colleges") and table_exists("Departments") and table_exists("Courses"):
        clear()
    else:
        createTables()

    uva = Extract.createUVA()
    for each in uva.colleges:
        addCollege(each)

        for departments in uva.colleges[each].getDepartments():
            addDepartment(departments.name, each)

            for course in departments.getCourses():
                addCourse(course[1], departments.name)
    return True

def getDepartmentsByCollege(collegeID):
    global connection, cursor
    if connection == None or cursor == None:
        print("Not Connected to the Database")
        return False     
    
    try:
        query = f"""SELECT
        UVA_Scheduler.Departments.id AS department_id,
        UVA_Scheduler.Departments.department_name
        FROM
            UVA_Scheduler.Departments
        JOIN
            UVA_Scheduler.Colleges ON UVA_Scheduler.Departments.college = UVA_Scheduler.Colleges.id
        WHERE
            UVA_Scheduler.Colleges.college_name = '{collegeID}';"""
        
        cursor.execute(query)
        resultSet = cursor.fetchall()

        return resultSet
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return False

def getCoursesByDepartment(department):
    global connection, cursor
    if connection == None or cursor == None:
        print("Not Connected to the Database")
        return False     
    
    try:
        query = f"""SELECT
        UVA_Scheduler.Courses.name AS course_name,
        UVA_Scheduler.Courses.course_code,
        UVA_Scheduler.Courses.course_id,
        UVA_Scheduler.Courses.section,
        UVA_Scheduler.Courses.class_type,
        UVA_Scheduler.Courses.credits,
        UVA_Scheduler.Courses.enrollment_status,
        UVA_Scheduler.Courses.availability,
        UVA_Scheduler.Courses.professor,
        UVA_Scheduler.Courses.time,
        UVA_Scheduler.Courses.location
        FROM
            UVA_Scheduler.Courses
        JOIN
            UVA_Scheduler.Departments ON UVA_Scheduler.Courses.department_id = UVA_Scheduler.Departments.id
        WHERE
            UVA_Scheduler.Departments.department_name = '{department}';"""
        
        cursor.execute(query)
        resultSet = cursor.fetchall()
        return resultSet
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return False

def createStudent(username, password):
    global connection, cursor, user
    if connection == None or cursor == None:
        print("Not Connected to the Database")
        return False
    
    try:
        statement = f"INSERT INTO {config.database}.Students(student_username, password) VALUES('{username}','{password}')"
        cursor.execute(statement)
        cursor.fetchall()
        user = username
        return True
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return False    

def createScheduleByStudent(username, schedule_name):
    global connection, cursor, user
    if connection == None or cursor == None:
        print("Not Connected to the Database")
        return False
    
    try:
        statement = f"INSERT INTO {config.database}.Schedule(student_username, student_schedule) VALUES('{username}','{schedule_name}')"
        cursor.execute(statement)
        cursor.fetchall()
        return True
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return False

def getStudentSchedules(username):
    global connection, cursor, user
    if connection == None or cursor == None:
        print("Not Connected to the Database")
        return False
    try:
        query = f"""SELECT
        UVA_Scheduler.Schedule.id AS schedule_id,
        UVA_Scheduler.Schedule.student_schedule
        FROM
            UVA_Scheduler.Schedule
        JOIN
            UVA_Scheduler.Students ON UVA_Scheduler.Schedule.student_username = UVA_Scheduler.Students.student_username
        WHERE
            UVA_Scheduler.Schedule.student_username = '{username}';"""
        
        cursor.execute(query)
        resultSet = cursor.fetchall()
        return resultSet
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return False 

def addCoursesToSchedule(schedule_id, course_id):
    global connection, cursor, user
    if connection == None or cursor == None:
        print("Not Connected to the Database")
        return False
    statement = f"INSERT INTO {config.database}.Schedule_Interface(schedule_id, course_id) VALUES('{schedule_id}','{course_id}')"
    cursor.execute(statement)
    cursor.fetchall()
    return True

def getCoursesFromSchedule(schedule_id):
    global connection, cursor, user
    if connection == None or cursor == None:
        print("Not Connected to the Database")
        return False
    try:
        query = f"""SELECT
        UVA_Scheduler.Schedule_Interface.course_id
        FROM
            UVA_Scheduler.Schedule_Interface
        JOIN
            UVA_Scheduler.Schedule ON UVA_Scheduler.Schedule_Interface.schedule_id = UVA_Scheduler.Schedule.id
        WHERE
            UVA_Scheduler.Schedule_Interface.schedule_id = '{schedule_id}';"""
        
        cursor.execute(query)
        resultSet = cursor.fetchall()
        return resultSet
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return False 

def close():
    global connection, cursor
    if connection == None or cursor == None:
        print("Not Connected to the Database")
        return False 
    cursor.close()
    connection.close()
    return True


connect()
# fillTables()
rs = getCoursesByDepartment("Mathematics")
for each in rs:
    print(each)
close()
# clear()

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