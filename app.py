# Import the necessary libraries
from flask import Flask, render_template
from Scripts.DatabaseManager import connect, getCoursesFromSchedule, close, getColleges, getDepartmentsByCollege, getCoursesByDepartment

# Create a Flask application
app = Flask(__name__)

# Define a route that will render the HTML page
@app.route('/')
def index():
    # Call the getColleges() function to retrieve data
    connect()
    colleges = getColleges()
    close()  

    # Pass the data to the HTML template
    return render_template('index.html', colleges=colleges)

@app.route('/college/<college_name>')
def college_details(college_name):
    
    connect()
    departments = getDepartmentsByCollege(college_name)
    close()

    return render_template('college.html', departments=departments, college_name=college_name)

@app.route('/college/department/<department_name>')
def department_details(department_name):
    
    connect()
    courses = getCoursesByDepartment(department_name)
    close()

    return render_template('department.html', courses=courses, department_name=department_name)

@app.route('/gallery')
def gallery():
    return render_template('gallery.html')

if __name__ == '__main__':
    # Run the Flask application
    app.run(port=5500, debug=True)