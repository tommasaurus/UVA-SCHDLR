# Import the necessary libraries
from flask import Flask, render_template
from Scripts.DatabaseManager import connect, getCoursesFromSchedule, close

# Create a Flask application
app = Flask(__name__)

# Define a route that will render the HTML page
@app.route('/')
def index():
    # Call the getClasses() function to retrieve data
    connect()
    classes_data = getCoursesFromSchedule(3)
    close()

    print(classes_data)
    

    # Pass the data to the HTML template
    return render_template('index.html', classes_data=classes_data)

@app.route('/emoji')
def emoji():
    return render_template('emoji.html')

@app.route('/gallery')
def gallery():
    return render_template('gallery.html')

if __name__ == '__main__':
    # Run the Flask application
    app.run(port=5500, debug=True)