import requests
from bs4 import BeautifulSoup
import sys
import os
import re
import copy
from Objects.Course import Course
from Objects.College import College
from Objects.Department import Department
from Objects.UVA import UVA

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
    
    # Master Dictionary
    uva = UVA()
    count = 0
    # Iterate through the header and table elements and build the dictionary that maps schools within UVA to College objects
    for college, department in zip(colleges, departments):
        # Add colleges to main UVA dictionary
        count += 1
        college_name = college.get_text(strip=True)
        uva.addCollege(college_name, new_func(department, college_name))
        # print(id(uva.colleges["Arts & Sciences Departments"].departments))
        # if count > 1:
        #     print("SECOND ID", id(uva.colleges["Arts & Sciences Programs, Seminars, and Institutes"].departments))

    
    print(len(uva.colleges["Arts & Sciences Programs, Seminars, and Institutes"].departments))
    # if (id(uva.colleges["Arts & Sciences Departments"].departments) == id(uva.colleges["Arts & Sciences Programs, Seminars, and Institutes"].departments)):
        # print("TERUEUURUURTUUUERUEURUEU")
    return uva

def new_func(department, college_name):
    
    tempCollege = copy.deepcopy(College(college_name))
    #  print(id(tempCollege))
    # Add each department to their respective college
    for a in department.find_all('a'):
        if not a.get_text(strip=True).replace(" ","") == "":
            tempCollege.addDepartment(Department(a.get_text(), config.URL + a["href"]))
    return tempCollege

def createDictDepartmentToCourses(CollegeDictionary, CollegeName, departmentName):
    """_summary_

    Args:
        CollegeToDepartmentDict (_type_): _description_
        CollegeName (_type_): _description_
        departmentName (_type_): _description_

    Returns:
        _type_: _description_
    """
    # Retrieve the department URL from the given dictionary using the college name and department name
    departmentURl = CollegeDictionary.colleges[CollegeName].getDepartment(departmentName).getURL()
    
    # Retrieve the table element containing all the courses from the departmentHTML
    departmentHTML = extractHTML(departmentURl)
    if (departmentHTML == None):
        return 
        
    table = departmentHTML.find("body").find('table', {'cellspacing': '0'})
    
    if (table == None):
        print("THIS DEPARTMENT HAS NO COURSES: ", departmentName, "COLLEGE NAME: ", CollegeName)
        return 

    # Retrieve all elements with course IDs (eg: MATH1000) in the given department
    courseIDs = table.find_all('td', {"class": "CourseNum"})
    if (courseIDs == None):
        return
    # List of courses for each department
    allCourses = CollegeDictionary.colleges[CollegeName].getDepartment(departmentName).getCourses()

    for course in courseIDs:
        # Find the name of course associated with the course ID
        course_name_td = course.find_next_sibling('td', {"class": "CourseName"})

        if course_name_td:
            course_num = course.get_text(strip=True)
            
            # Retrieve list of sections within each course
            courseSections = table.find_all('tr', class_=lambda value: value and "SectionTopic" not in value and "SectionTitle" not in value and (" " + course_num.replace(" ","")) in value)
            
            for section in courseSections:
                sectionHTML = section.get_text(strip=True)
                
                if (sectionHTML != ""):
                    
                    # Check if section has a name
                    prev = section.find_previous_sibling()                    
                    try: 
                        if "SectionTopic" in prev["class"][0]:
                            course_name = prev.get_text(strip=True)
                    except(Exception):
                        course_name = course_name_td.get_text(strip=True)

                    # Retrieve all section-related information (td elements)
                    courseElements = section.find_all('td')
                    if len(courseElements) > 7:
                        allCourses.append((course_num, parseCourse(courseElements, course_num, course_name)))
            
    return allCourses

def parseCourse(courseHTML, courseNum, courseName):
    """_summary_

    Args:
        courseHTML (_type_): _description_
        courseNum (_type_): _description_
        courseName (_type_): _description_

    Returns:
        _type_: _description_
    """
    course_type_pattern = r'([a-zA-Z]+)' # Match the type of course (eg: discussion)
    credits_pattern = r'\((.*?)\)'  # Match text inside parentheses for credits
    professor_pattern = r'((-|To Be Announced)|([A-Za-z]+ [A-Za-z]+))'   # Match for professor names
    pattern = course_type_pattern + credits_pattern
    
    if (len(courseHTML) == 8):
        courseElements = []
        for each in courseHTML:
            courseElements.append(each.get_text(strip=True))
    
        match = re.search(pattern, courseElements[2])
        class_type = match.group(1)
        credits = match.group(2)

        courseElements[2] = class_type
        courseElements.insert(3, credits)

        match = re.finditer(professor_pattern, courseElements[6])
        courseElements[6] = [each.group() for each in match]

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
    
soup = extractHTML(config.URL)
dict = createDictCollegeToDepartments(soup)
# createDictDepartmentToCourses(dict, "Arts & Sciences Departments", "African-American & African Studies")
# # (len(dict)
# print(dict.colleges['Arts & Sciences Departments'].departments[0].getCourseNames())
count = 0
keys = list(dict.colleges.keys())
print(len(keys))
for each in keys:
    #  print(each)
    #  print(len(dict[each].departments))
    #  print(dict[each].getDepartmentNames())
    print("NEW COLLEGEEEEEE")
    for departmentName in dict.colleges[each].getDepartmentNames():
        createDictDepartmentToCourses(dict, each, departmentName)
        count += 1
        print(count) 
    if count == 136:
        print()
print(dict)
