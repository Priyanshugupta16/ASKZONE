# Khushi run pip install mysqli-connector-python if you dont have it in your laptop
import mysql.connector

conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="askzone"
)

cursor = conn.cursor()