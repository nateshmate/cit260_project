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
    data = request.json
    examname = data.get("examname")
    examdate = data.get("examdate")
    examtime = data.get("examtime")
    campusname = data.get("campusname")
    buildingname = data.get("buildingname")
    roomnumber = data.get("roomnumber")
    #facultyID = data.get("facultyID")  
    #capacity = data.get("capacity")    

    if not all([examname, campusname, buildingname, roomnumber, examdate, examtime]):
        return jsonify({"error": "All fields are required"}), 400

    conn = None
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
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

            # Insert exam
            sql_insert_exam = """
                INSERT INTO exam (examname, examdate, examtime, locationID)
                VALUES (%s, %s, %s, %s)
            """
            cursor.execute(sql_insert_exam, (examname, examdate, examtime, locationID))
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
                SELECT e.examID, e.examname, e.examdate, e.examtime,
                       l.campusname, l.buildingname, l.roomnumber
                FROM exam e
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
