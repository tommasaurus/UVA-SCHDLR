import mysql.connector
import sys
import os
import re

config_directory = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(config_directory)

import config

# Establish a connection to the MySQL server
connection = mysql.connector.connect(
    host = config.host,
    user = config.user,
    password = config.password,
    database = config.database
)

# Create a cursor
cursor = connection.cursor()

createTables_relative_path = "SQL_Scripts/CreateTables.sql"
createTables_script = os.path.join(os.getcwd(), createTables_relative_path)

for line in open(createTables_script):
    cursor.execute(line)

# Commit the changes
connection.commit()
results = cursor.fetchall()

# Close the cursor and connection
cursor.close()
connection.close()