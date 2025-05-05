from flask import Flask, request, jsonify 
from flask_cors import CORS 
import pymysql
import re

app = Flask(__name__)
CORS(app)  


# Connect database
def get_connection():
    return pymysql.connect(
        host="35.230.124.147",
        user="le",
        password="plqn2004", 
        database="registration_db",
        cursorclass=pymysql.cursors.DictCursor
    )

# Validate email format
def validate_email(email, role):
    if role == "student":
        pattern = r'^\d{10}@student\.csn\.edu$'
    elif role == "faculty":
        pattern = r'^\d{10}@csn\.edu$'
    else:
        return False
    return re.match(pattern, email) is not None


@app.route('/create_account', methods=['POST'])
def create_account():
    data = request.json
    first_name = data.get("first_name")
    last_name = data.get("last_name")
    role = data.get("role")
    username = data.get("username")
    password = data.get("password")
    nshe_number = username[:10]

    if not all([first_name, last_name, role, username, password]):
        return jsonify({"error": "All fields are required"}), 400

    if role not in ['student', 'faculty']:
        return jsonify({"error": "Invalid role"}), 400
    
    if not validate_email(username, role):
        return jsonify({"error": "Invalid email format"}), 400

    expected_password = username[:10]  # Extract first 10 characters of email
    if password != expected_password:
        return jsonify({"error": "Password must be NSHE# (first 10 characters of email)"}), 400
    
    # ----- Updated! Database Connection -----
    conn = None
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            # Check if the account already exists
            cursor.execute("SELECT * FROM authentication WHERE email = %s", (username,))
            existing = cursor.fetchone()
            if existing:
                return jsonify({"error": "Account already exists"}), 400

            # Insert new account into authentication table
            sql_auth = """INSERT INTO authentication (email, password, role)
                     VALUES (%s, %s, %s)"""
            cursor.execute(sql_auth, (username, password, role))
            conn.commit()

            # Insert new account into authentication table
            authentication_id = cursor.lastrowid

            # Insert new account into student or faculty table based on role
            if role == 'student':
                # Insert into student table
                sql_student = """INSERT INTO student (firstname, lastname, email, NSHENumber, authenticationID) 
                VALUES (%s, %s, %s, %s, %s)"""
                cursor.execute(sql_student, (first_name, last_name, username, nshe_number, authentication_id))
                conn.commit()

            elif role == 'faculty':
                # Insert into faculty table
                sql_faculty = """INSERT INTO faculty (firstname, lastname, email) VALUES (%s, %s, %s)"""
                cursor.execute(sql_faculty, (first_name, last_name, username))
                conn.commit()


        return jsonify({"message": f"Account created successfully for {first_name} {last_name}"}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if conn:
            conn.close()

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    role = data.get("role")
    username = data.get("username")
    password = data.get("password")

    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM authentication WHERE email = %s AND role = %s", (username, role))
            user = cursor.fetchone()

            if user and user['password'] == password:
                if role == 'student':
                    cursor.execute("SELECT * FROM student WHERE email = %s", (username,))
                    student = cursor.fetchone()
                    if student:
                        return jsonify({
                            "message": f"Welcome, {student['firstname']}!",
                            "first_name": student['firstname'],
                            "last_name": student['lastname'],
                            "role": role
                        }), 200
                elif role == 'faculty':
                    cursor.execute("SELECT * FROM faculty WHERE email = %s", (username,))
                    faculty = cursor.fetchone()
                    if faculty:
                        return jsonify({
                            "message": f"Welcome, {faculty['firstname']}!",
                            "first_name": faculty['firstname'],
                            "last_name": faculty['lastname'],
                            "role": role
                        }), 200

            else:
                return jsonify({"error": "Invalid credentials"}), 401
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if conn:
            conn.close()

@app.route('/create_exam', methods=['POST'])
def create_exam():

    from datetime import datetime

    def normalize_time(time_str):
        try:
            # if time is "HH"MM AM/PM"
            t = datetime.strptime(time_str, "%I:%M %p")
            return t.strftime("%H:%M")
        except:
            try:
                # if time is "HH:MM"
                t = datetime.strptime(time_str, "%H:%M")
                return t.strftime("%H:%M")
            except:
                return time_str  
                
    data = request.json
    examname = data.get("examname")
    examdate = data.get("examdate")
    examtime = normalize_time(data.get("examtime"))
    campusname = data.get("campusname")
    buildingname = data.get("buildingname")
    roomnumber = data.get("roomnumber")
    faculty_email = data.get("email")
    #print("Received email:", faculty_email)
    #facultyID = data.get("facultyID")  
    #capacity = data.get("capacity")    

    if not all([examname, campusname, buildingname, roomnumber, examdate, examtime]):
        return jsonify({"error": "All fields are required"}), 400

    conn = None
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            # Find facultyID by email
            cursor.execute("SELECT facultyID FROM faculty WHERE email = %s", (faculty_email,))
            faculty = cursor.fetchone()
            if not faculty:
                return jsonify({"error": "Faculty not found"}), 404
            facultyID = faculty["facultyID"]

            # Find locationID
            sql_find_location = """
                SELECT locationID FROM location
                WHERE campusname = %s AND buildingname = %s AND roomnumber = %s
            """
            cursor.execute(sql_find_location, (campusname, buildingname, roomnumber))
            location = cursor.fetchone()

            if location:
                locationID = location['locationID']
            else:
                # Insert new location
                sql_insert_location = """
                    INSERT INTO location (campusname, buildingname, roomnumber)
                    VALUES (%s, %s, %s)
                """
                cursor.execute(sql_insert_location, (campusname, buildingname, roomnumber))
                conn.commit()

                # Get the last inserted locationID
                locationID = cursor.lastrowid  
            
            # Check if an exam already exists at same time, date, location
            cursor.execute("""
                SELECT * FROM exam
                WHERE examdate = %s AND examtime = %s AND locationID = %s
            """, (examdate, examtime, locationID))
            existing_exam = cursor.fetchone()

            if existing_exam:
                return jsonify({"error": "An exam with the same name, date, time, and location already exists."}), 409
            
            # Insert exam
            sql_insert_exam = """
                INSERT INTO exam (examname, examdate, examtime, locationID, facultyID)
                VALUES (%s, %s, %s, %s, %s)
            """
            cursor.execute(sql_insert_exam, (examname, examdate, examtime, locationID, facultyID))
            conn.commit()

        return jsonify({"message": "Exam created successfully"}), 201

    except Exception as e:
        print(e)
        return jsonify({"error": "Failed to create exam"}), 500

    finally:
        if conn:
            conn.close()

@app.route('/get_exams', methods=['GET'])
def get_exams():
    conn = None
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT e.examid, e.examname, e.examdate, e.examtime, e.capacity,
                       COUNT(r.registrationID) AS currentCount,
                       l.campusname, l.buildingname, l.roomnumber,
                       f.firstname AS faculty_firstname,
                       f.lastname AS faculty_lastname
                FROM exam e
                LEFT JOIN location l ON e.locationid = l.locationid
                LEFT JOIN faculty f ON e.facultyid = f.facultyid
                LEFT JOIN registration r ON e.examid = r.examid
                GROUP BY e.examid
            """)
            exams = cursor.fetchall()
            return jsonify(exams), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if conn:
            conn.close()


@app.route('/register_exam', methods=['POST'])
def register_exam():
    data = request.json
    student_email = data.get("email") 
    exam_id = data.get("Exam_ID")
    reg_date = data.get("Reg_Date")

    if not all([student_email, exam_id, reg_date]):
        return jsonify({"error": "Missing data"}), 400

    conn = None
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            # find studentID
            cursor.execute("SELECT studentID FROM student WHERE email = %s", (student_email,))
            student = cursor.fetchone()

            if not student:
                return jsonify({"error": "Student not found"}), 404

            student_id = student["studentID"]

            # Check if the exam exists
            cursor.execute("SELECT * FROM registration WHERE studentID = %s AND examID = %s", (student_id, exam_id))
            existing = cursor.fetchone()
            if existing:
                return jsonify({"error": "You have already registered for this exam"}), 400

            # Insert registration
            sql_insert = """
                INSERT INTO registration (studentID, examID, regDate)
                VALUES (%s, %s, %s)
            """
            cursor.execute(sql_insert, (student_id, exam_id, reg_date))
            conn.commit()

        return jsonify({"message": "Registration successful!"}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        if conn:
            conn.close()

@app.route('/student/registrations', methods=['GET'])
def get_student_registrations():
    email = request.args.get('email')
    if not email:
        return jsonify({"error": "Missing student email"}), 400

    conn = None
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            sql = """
                SELECT
                    r.registrationID AS Registration_ID,
                    e.examname AS Exam_Name,
                    e.examdate AS Date,
                    e.examtime AS Exam_time,
                    l.campusname AS Campus_Name,
                    l.buildingname AS Building_Name,
                    l.roomnumber AS Room_Number
                FROM registration r
                JOIN exam e ON r.examID = e.examID
                JOIN location l ON e.locationID = l.locationID
                JOIN student s ON r.studentID = s.studentID
                WHERE s.email = %s
            """
            cursor.execute(sql, (email,))
            result = cursor.fetchall()
            return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if conn:
            conn.close()

@app.route('/student/registrations/<int:registration_id>', methods=['DELETE'])
def delete_registration(registration_id):
    conn = None
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute("DELETE FROM registration WHERE registrationID = %s", (registration_id,))
            conn.commit()
            return jsonify({"message": "Registration deleted successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if conn:
            conn.close()

@app.route('/faculty/exams', methods=['GET'])
def get_faculty_exams():
    conn = None
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT
                    e.examID AS examid,
                    e.examname AS examname,
                    e.examdate AS examdate,
                    e.examtime  AS examtime,
                    e.capacity AS capacity,
                    (
                        SELECT COUNT(*) FROM registration r
                        WHERE r.examID = e.examID
                    ) AS currentCount,
                    l.campusname AS campusname,
                    l.buildingname AS buildingname,
                    l.roomnumber AS roomnumber,
                    f.firstname AS faculty_firstname,
                    f.lastname AS faculty_lastname       
                FROM exam e
                JOIN faculty f ON e.facultyID = f.facultyID
                JOIN location l ON e.locationID = l.locationID
                
            """)
            exams = cursor.fetchall()
            return jsonify(exams), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if conn:
            conn.close()

if __name__ == '__main__':
    app.run(debug=True)
