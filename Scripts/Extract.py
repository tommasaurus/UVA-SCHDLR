import requests
from bs4 import BeautifulSoup
import sys
import os
import re
from Objects.Course import Course
from Objects.College import College
from Objects.Department import Department


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
    Uses the main HTML and creates a mapping from college names to department names and their respective links
    Args:
        soup (Beautiful Soup): main parsing object from HTML

    Returns:
        Dict{str: str[(str, str)]}: dictionary with mapping from college names to department names and their respective links
    """
    # Find the accordion that contains all college names and departments
    div_accordion = soup.find('div', {'id': 'accordion'})
    
    # Find all colleges
    colleges = div_accordion.find_all('h3')

    # Find all the departments
    departments = div_accordion.find_all('table')
    
    accordion_data = {}  

    #Iterate through the header and table elements and build the dictionary that maps schools within UVA to subjects
    for college, department in zip(colleges, departments):
        college_name = college.get_text(strip=True)
        departmentList = {a.get_text(): config.URL + a["href"] for a in department.find_all('a')}
        accordion_data[college_name] = departmentList

    return accordion_data

def createDictDepartmentToCourses(CollegeToDepartmentDict, CollegeName, departmentName):
    # Retrieve the department URL from the given dictionary using the college name and department name
    departmentURl = CollegeToDepartmentDict[CollegeName][departmentName]
    
    # Retrieve the table element with all the classes from the departmentHTML
    departmentHTML = extractHTML(departmentURl)
    table = departmentHTML.find("body").find('table', {'cellspacing': '0'})
    
    # Retrieve all elements with course ID (eg: MATH1000)
    courseNums = table.find_all('td', {"class": "CourseNum"})
    
    list = []
    # tr_elements = table.find_all('tr', class_=lambda value: value and 'AAS1020' in value)
    # list = [a.get_text(strip = True) for a in tr_elements if a.get_text(strip = True) != ""]

    for each in courseNums:
        allCourses = []
        course_name_td = each.find_next_sibling('td', {"class": "CourseName"})
        # CourseElements = table.find_all('tr', class_=lambda value: value and "SectionTopic" not in value and "SectionTitle" not in value and " AAS5559" in value)
        
        # allCourses = [a.get_text(strip = True) for a in CourseElements if a.get_text(strip = True) != ""]
        # list.append((course_name_td.get_text(strip=True), parseCourse(allCourses[0], "AAS 2500", "AAS NAME")))

        if course_name_td:
            course_num = each.get_text(strip=True)
            
            CourseElements = table.find_all('tr', class_=lambda value: value and "SectionTopic" not in value and "SectionTitle" not in value and (" " + course_num.replace(" ","")) in value)
            for a in CourseElements:
                print(len(CourseElements))
                courseHTML = a.get_text(strip=True)
                if (courseHTML != ""):
                    prev = a.find_previous_sibling()
                    try: 
                        if "SectionTopic" in prev["class"][0]:
                            course_name = prev.get_text(strip=True)
                    except(Exception):
                        course_name = course_name_td.get_text(strip=True)
                    list.append((course_num, parseCourse(courseHTML, course_num, course_name)))
            
    
    return list

def parseCourse(courseHTML, courseNum, courseName):
    #Create regex search patterns
    course_id_pattern = r'(\d{5})' # Match 5 digits for course id
    section_number_pattern = r'(\d{3})' # Match 3 digits for section number
    course_type_pattern = r'([a-zA-Z]+)' # Match the type of course (eg: discussion)
    units_pattern = r'\((.*?)\)'  # Match text inside parentheses for units
    course_availability_pattern = r'([A-Za-z]+)'  # Match "Open" or "Closed"
    course_enrollment_pattern = r'(\d+ \/ \d+)[0-9\/() ]*'  # Match "X / X" format
    professor_pattern = r'([A-Za-z]+\s[A-Za-z]+[+]?[0-9]?|To Be Announced)(?=[A-Z])'#r'([A-Za-z]+ [A-Z][a-z]+\+?\d?|To Be Announced)' # Match the professor's name
    course_time_pattern = r'([A-Za-z]* \d+:\d+[apm ]+- \d+:\d+[apm ]+|TBA)' # Match the course time
    course_location_pattern = r'(.*)'  # Match location
    
    pattern = course_id_pattern + section_number_pattern + course_type_pattern + units_pattern + course_availability_pattern + \
        course_enrollment_pattern + professor_pattern + course_time_pattern + course_location_pattern
    
    match = re.search(pattern, courseHTML)
    
    if match:
        # Extract values from the match object
        id, section, course_type, credits, availability, enrollment, professor, time, location = match.groups()

        # Create a Course object
        return Course(courseName, courseNum, id, section, course_type, credits, availability, enrollment, professor, time, location)
    else:
        print("No match found in the input string.")
    
    


soup = extractHTML(config.URL)
dict = createDictCollegeToDepartments(soup)
keys = list(dict.keys())
depthtml = createDictDepartmentToCourses(dict, keys[0], "African-American & African Studies")
print(depthtml)
# print(dict[keys[0]])