from flask import Flask, render_template, request
from pymysql import connections
import os
import boto3
from config import *

app = Flask(__name__)

bucket = custombucket
region = customregion

db_conn = connections.Connection(
    host=customhost,
    port=3306,
    user=customuser,
    password=custompass,
    db=customdb
)

@app.route("/", methods=['GET', 'POST'])
def home():
    return render_template('GetStud.html')

@app.route("/getstud", methods=['GET','POST'])
def GetStud():
    stud_id = request.form['stud_id']
    select_sql = "SELECT * FROM students WHERE stud_id = %s"
    cursor = db_conn.cursor()

    try:
        cursor.execute(select_sql, (stud_id))
        student = cursor.fetchone()
        if student:
            # Extract student information from the database
            stud_id, fname, lname, contact, address = student
            return render_template('GetStudOutput.html', id=stud_id, fname=fname, lname=lname, contact=contact, address=address)
        else:
            return "Student not found"

    except Exception as e:
        return str(e)

    finally:
        cursor.close()
    
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)
