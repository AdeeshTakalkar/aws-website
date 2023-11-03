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
output = {}
table = 'students'


@app.route("/", methods=['GET', 'POST'])
def home():
    return render_template('AddStud.html')


@app.route("/addstud", methods=['POST'])
def AddStud():
    stud_id = request.form['stud_id']
    fname = request.form['fname']
    lname = request.form['lname']
    contact = request.form['contact']
    address = request.form['address']
    stud_image_file = request.files['stud_image_file']

    insert_sql = "INSERT INTO students VALUES (%s, %s, %s, %s, %s)"
    cursor = db_conn.cursor()

    if stud_image_file.filename == "":
        return "Please select a file"

    try:

        cursor.execute(insert_sql, (stud_id, fname, lname, contact, address))
        db_conn.commit()
        stud_name = "" + fname + " " + lname
        # Uplaod image file in S3 #
        stud_image_file_name_in_s3 = "stud-id-" + str(stud_id) + "_image_file"
        s3 = boto3.resource('s3')

        try:
            print("Data inserted in MySQL RDS... uploading image to S3...")
            s3.Bucket(custombucket).put_object(Key=stud_image_file_name_in_s3, Body=stud_image_file)
            bucket_location = boto3.client('s3').get_bucket_location(Bucket=custombucket)
            s3_location = (bucket_location['LocationConstraint'])

            if s3_location is None:
                s3_location = ''
            else:
                s3_location = '-' + s3_location

            object_url = "https://s3{0}.amazonaws.com/{1}/{2}".format(
                s3_location,
                custombucket,
                stud_image_file_name_in_s3)

        except Exception as e:
            return str(e)

    finally:
        cursor.close()

    print("all modification done...")
    return render_template('AddStudOutput.html', name=stud_name)

@app.route("/getstud", methods=['GET','POST'])
def GetStud():
    render_template('GetStud.html');
    stud_id = request.form['stud_id']

    select_sql = "SELECT * FROM students WHERE stud_id = %s"
    cursor = db_conn.cursor()

    try:
        cursor.execute(select_sql, (stud_id,))
        student = cursor.fetchone()
        if student:
            # Extract student information from the database
            stud_id, fname, lname, contact, address = student
            return render_template('GetStud.html', id=stud_id, fname=fname, lname=lname, contact=contact, address=address)
        else:
            return "Student not found"

    except Exception as e:
        return str(e)

    finally:
        cursor.close()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)
