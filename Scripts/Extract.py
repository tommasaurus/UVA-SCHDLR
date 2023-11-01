import requests
from bs4 import BeautifulSoup

url = 'https://louslist.org/'

# Send an HTTP GET request to the URL and store the response
response = requests.get(url)

# Check if the request was successful (status code 200)
if response.status_code == 200:
    # Get the HTML content from the response
    html_content = response.text

    # Parse the HTML content using BeautifulSoup
    soup = BeautifulSoup(html_content, 'lxml')  # You can choose a different parser if needed
    print("hello")
    # Now you can work with the parsed HTML content as described in the previous steps
    # For example, locating the specific div element and extracting data from it
else:
    print(f"Failed to retrieve the web page. Status code: {response.status_code}")
