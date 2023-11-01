import requests
from bs4 import BeautifulSoup
import sys
import os
import string

# Setting the python path
config_directory = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(config_directory)

import config

def extractHTML():
    """ 
    Extracts all course information from Lou's List
    Returns:
        BeautifulSoup: Parsing object from HTML
    """
    # Send an HTTP GET request to the URL and store the response
    response = requests.get(config.URL)

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
    # Finds the accordion that contains all college names and departments
    div_accordion = soup.find('div', {'id': 'accordion'})
    
    # Find all colleges
    colleges = div_accordion.find_all('h3')

    # Finds all the departments
    departments = div_accordion.find_all('table')
    
    accordion_data = {}  

    #Iterate through the header and table elements and build the dictionary that maps schools within UVA to subjects
    for college, department in zip(colleges, departments):
        college_name = college.get_text(strip=True)
        departmentList = [(a.get_text(), config.URL + a["href"]) for a in department.find_all('a')]
        accordion_data[college_name] = departmentList

    return accordion_data



soup = extractHTML()
dict = createDictCollegeToDepartments(soup)
keys = list(dict.keys())
print(dict[keys[0]])