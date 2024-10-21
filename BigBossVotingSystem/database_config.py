import mysql.connector

# MySQL Database Configuration
db_connection = mysql.connector.connect(
    host='localhost',       # Database Host (usually localhost)
    user='dipali',  # Your MySQL username
    password='dipali',  # Your MySQL password
    database='bigboss_voting1'  # Name of the database
)
