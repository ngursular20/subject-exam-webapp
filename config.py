import mysql.connector

def get_db_connection():
    connection = mysql.connector.connect(
        host='localhost',
        user='sevde',
        password='1',
        database='quiz_app'
    )
    return connection
