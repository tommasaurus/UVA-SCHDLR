import requests
from bs4 import BeautifulSoup
import sys
import os
import re
import copy
from UVAObjects.Course import Course
from UVAObjects.College import College
from UVAObjects.Department import Department
from UVAObjects.UVA import UVA

# Setting the python path
config_directory = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(config_directory)

import config

def extractHTML(url):
    """ 
    Extracts all course information from Lou's List
    Returns:
        BeautifulSoup: Parsing object from HTML
    """
    # Send an HTTP GET request to the URL and store the response
    response = requests.get(url)

    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        # Get the HTML content from the response
        html_content = response.text

        # Parse the HTML content using BeautifulSoup
        soup = BeautifulSoup(html_content, 'lxml')
        return soup
    else:
        print(f"Failed to retrieve the web page. Status code: {response.status_code}")

def createDictCollegeToDepartments(soup):
    """
    Uses the main HTML and creates a mapping from college names to college objects
    Args:
        soup (BeautifulSoup): main parsing object from HTML

    Returns:
        Dict{str: Colleges}: dictionary with mapping from college names to college objects
    """
    # Find the accordion that contains all college names and departments
    div_accordion = soup.find('div', {'id': 'accordion'})
    
    # Find all colleges
    colleges = div_accordion.find_all('h3')

    # Find all the departments
    departments = div_accordion.find_all('table')
    
    # Master Object
    uva = UVA()
    
    # Iterate through the header and table elements and build the dictionary that maps schools within UVA to College objects
    for college, department in zip(colleges, departments):
        
        # Add colleges to main UVA object
        college_name = college.get_text(strip=True)
        uva.addCollege(college_name, addDepartmentsToCollege(department, college_name))
       
    return uva

def addDepartmentsToCollege(department, college_name):
    """
    Adds and creates all department objects and maps them to the given college
    Args:
        department (table): table object that holds all the departments
        college_name (str): name of the college 

    Returns:
        college: college object that contains all the related department objects
    """
    # Create college object to be returned
    tempCollege = copy.deepcopy(College(college_name))
    
    # Add each department to their respective college
    for a in department.find_all('a'):
        if not a.get_text(strip=True).replace(" ","") == "":
            tempCollege.addDepartment(Department(a.get_text(), config.URL + a["href"]))
    return tempCollege

def mapDepartmentToCourses(UVA, CollegeName, departmentName):
    """
    Adds all the courses available in a given department by sifting through the UVA object
    Args:
        UVA (UVA): UVA master object
        CollegeName (Str): The name of the college that the department is in
        departmentName (Str): The name of the department to add classes to 

    Returns:
        [Course]: List of courses within the department
    """
    # Retrieve the department URL from the given dictionary using the college name and department name
    departmentURl = UVA.colleges[CollegeName].getDepartment(departmentName).getURL()
    
    # Retrieve the departmentHTML from the given url
    departmentHTML = extractHTML(departmentURl)
    if (departmentHTML == None):
        return False

    # Retrieve the table element containing all the courses from the departmentHTML    
    table = departmentHTML.find("body").find('table', {'cellspacing': '0'})
    if (table == None):
        return False

    # Retrieve all elements with course IDs (eg: MATH1000) in the given department
    courseIDs = table.find_all('td', {"class": "CourseNum"})
    if (courseIDs == None):
        return False

    # List of course objects for each department object
    allCourses = copy.deepcopy(Department(departmentName, departmentURl))
    # allCourses = UVA.colleges[CollegeName].getDepartment(departmentName).getCourses()

    for course in courseIDs:
        # Find the name of course associated with the course ID element
        course_name_td = course.find_next_sibling('td', {"class": "CourseName"})

        if course_name_td:
            # Get the actual course ID (eg: MATH1000)
            course_num = course.get_text(strip=True)
            
            # Retrieve list of section elements within each course
            courseSections = table.find_all('tr', class_=lambda value: value and "SectionTopic" not in value and "SectionTitle" not in value and (" " + course_num.replace(" ","")) in value)
            
            for section in courseSections:
                sectionHTML = section.get_text(strip=True)
                
                if (sectionHTML != ""):
                    
                    # Check if section has a special name
                    prev = section.find_previous_sibling()                    
                    try: 
                        if "SectionTopic" in prev["class"][0]:
                            course_name = prev.get_text(strip=True)
                    except(Exception):
                        course_name = course_name_td.get_text(strip=True)

                    # Retrieve all section-related information (td elements) and add them to the courses
                    courseElements = section.find_all('td')
                    if len(courseElements) > 7:
                        allCourses.courses.append((course_num, parseCourse(courseElements, course_num, course_name)))
    index = UVA.colleges[CollegeName].departments.index(UVA.colleges[CollegeName].getDepartment(departmentName))
    UVA.colleges[CollegeName].departments[index] = allCourses
    return allCourses

def parseCourse(courseHTML, courseNum, courseName):
    """
    Parses the courseHTML to separate the attributes for to create a Course object
    Args:
        courseHTML ([td elements]): _description_
        courseNum (str): course ID (eg: MATH 1000)
        courseName (str): course name

    Returns:
        Course: newly created Course object
    """
    course_type_pattern = r'([a-zA-Z]+)' # Match the type of course (eg: discussion)
    credits_pattern = r'\((.*?)\)'  # Match text inside parentheses for credits
    professor_pattern = r'((-|To Be Announced)|([A-Za-z]+ [A-Za-z]+))'   # Match for professor names
    pattern = course_type_pattern + credits_pattern
    
    # Check if the HTML contains the required attributes
    if (len(courseHTML) == 8):
        
        #Set courseHTML elements to strings
        courseElements = []
        for each in courseHTML:
            courseElements.append(each.get_text(strip=True))
    
        # Seperate the type of course (eg: discussion) and the number of credits (eg: 3 credits)
        match = re.search(pattern, courseElements[2])
        class_type = match.group(1)
        credits = match.group(2)

        courseElements[2] = class_type
        courseElements.insert(3, credits)

        # Check if course is taught by more than one professor
        match = re.finditer(professor_pattern, courseElements[6])
        professorList = [each.group() for each in match]
        if (len(professorList) == 0):
            professorList.append("To Be Determined")
        courseElements[6] = professorList

        id, section, course_type, credits, availability, enrollment, professor, time, location = courseElements
        
        return Course(courseName, courseNum, id, section, course_type, credits, availability, enrollment, professor, time, location)
    

        
    # #Create regex search patterns
    # course_id_pattern = r'(\d{5})' # Match 5 digits for course id
    # section_number_pattern = r'(\d{3})' # Match 3 digits for section number
    # course_type_pattern = r'([a-zA-Z]+)' # Match the type of course (eg: discussion)
    # units_pattern = r'\((.*?)\)'  # Match text inside parentheses for units
    # course_availability_pattern = r'([A-Za-z]+)'  # Match "Open" or "Closed"
    # course_enrollment_pattern = r'(\d+ \/ \d+)[0-9\/() ]*'  # Match "X / X" format
    # professor_pattern = r'([A-Za-z]+\s[A-Za-z ]+|To Be Announced)' # Match the professor's name
    # course_time_pattern = r'([A-Za-z]* \d+:\d+[apm ]+- \d+:\d+[apm ]+|TBA)' # Match the course time
    # course_location_pattern = r'(.*)'  # Match location
    
    # pattern = course_id_pattern + section_number_pattern + course_type_pattern + units_pattern + course_availability_pattern + \
    #     course_enrollment_pattern + professor_pattern + course_time_pattern + course_location_pattern
    
    # match = re.search(pattern, courseHTML)
    
    # if match:
    #     # Extract values from the match object
    #     id, section, course_type, credits, availability, enrollment, professor, time, location = match.groups()

    #     # Create a Course object
    #     return Course(courseName, courseNum, id, section, course_type, credits, availability, enrollment, professor, time, location)
    # else:
    #     print("No match found in the input string.")
    
def createUVA():
    """
    Generates the master UVA object that contains all colleges, associated departments, and associated courses
    Returns:
        UVA: UVA object
    """
    # Create a UVA object with mapping to all the colleges and departments
    soup = extractHTML(config.URL)
    uvaObject = createDictCollegeToDepartments(soup)
    del uvaObject.colleges["Special Listings and Raw Data"]
    del uvaObject.colleges["Other Programs, Seminars, and Institutes"]
    
    # Adds all the courses to each respective department
    keys = list(uvaObject.colleges.keys())
    for each in keys:        
        print(each)
        for departmentName in uvaObject.colleges[each].getDepartmentNames():
            if (not mapDepartmentToCourses(uvaObject, each, departmentName)):
                uvaObject.colleges[each].removeDepartment(departmentName)
    
    return uvaObject
