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
def validate_email(email, Role):
    if Role == "student":
        pattern = r'^\d{10}@student\.csn\.edu$'
    elif Role == "faculty":
        pattern = r'^[a-zA-Z]+\.[a-zA-Z]+@csn\.edu$'
    else:
        return False
    return re.match(pattern, email) is not None


@app.route('/create_account', methods=['POST'])
def create_account():
    data = request.json
    First_Name = data.get("First_Name")
    Last_Name = data.get("Last_Name")
    Role = data.get("Role")
    CSN_email = data.get("CSN_email")
    Password = data.get("Password")

    if not all([First_Name, Last_Name, Role, CSN_email, Password]):
        return jsonify({"error": "All fields are required"}), 400

    if Role not in ['student', 'faculty']:
        return jsonify({"error": "Invalid role"}), 400
    
    if not validate_email(CSN_email, Role):
        return jsonify({"error": "Invalid email format"}), 400

    if Role == "student":
        expected_password = CSN_email[:10]  # Extract first 10 characters of email
        if Password != expected_password:
            return jsonify({"error": "Password must be NSHE# (first 10 characters of email)"}), 400
    
    # ----- Updated! Database Connection -----
    conn = None
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            # Check if the account already exists
            cursor.execute("SELECT * FROM authentication WHERE CSN_email = %s", (CSN_email,))
            existing = cursor.fetchone()
            if existing:
                return jsonify({"error": "Account already exists"}), 400

            # Insert new account into authentication table
            sql = """INSERT INTO authentication (CSN_email, Password, Role, First_Name, Last_Name)
                     VALUES (%s, %s, %s, %s, %s)"""
            cursor.execute(sql, (CSN_email, Password, Role, First_Name, Last_Name))
            conn.commit()

            # Insert new account into student or faculty table based on Role
            if Role == 'student':
                # Insert into student table
                sql = """INSERT INTO student (First_Name, Last_Name) VALUES (%s, %s)"""
                cursor.execute(sql, (First_Name, Last_Name))
                conn.commit()

            elif Role == 'faculty':
                # Insert into faculty table
                sql = """INSERT INTO faculty (First_Name, Last_Name) VALUES (%s, %s)"""
                cursor.execute(sql, (First_Name, Last_Name))
                conn.commit()


        return jsonify({"message": f"Account created successfully for {First_Name} {Last_Name}"}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if conn:
            conn.close()

    '''
    if CSN_email in accounts:
        return jsonify({"error": "Account already exists"}), 400

    accounts[CSN_email] = {
        'First_Name': First_Name,
        'Last_Name': Last_Name,
        'Role': Role,
        'Password': Password
    }
    return jsonify({"message": f"Account created successfully for {First_Name} {Last_Name}"}), 201
    '''
@app.route('/login', methods=['POST'])
def login():
    data = request.json
    Role = data.get("Role")
    CSN_email = data.get("CSN_email")
    Password = data.get("Password")

    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM authentication WHERE CSN_email = %s AND Role = %s", (CSN_email, Role))
            user = cursor.fetchone()

            if user and user['Password'] == Password:
                return jsonify({
                    "message": f"Welcome, {user['First_Name']}!",
                    "First_Name": user['First_Name'],
                    "Last_Name": user['Last_Name'],
                    "Role": user['Role']
                }), 200
            else:
                return jsonify({"error": "Invalid credentials"}), 401
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if conn:
            conn.close()

    '''
    if CSN_email in accounts and accounts[CSN_email]['Role'] == Role and accounts[CSN_email]['Password'] == Password:
        return jsonify({
            "message": f"Welcome, {accounts[CSN_email]['First_Name']}!",
            "First_Name": accounts[CSN_email]['First_Name'],
            "Last_Name": accounts[CSN_email]['Last_Name'],
            "Role": Role  
        }), 200
    return jsonify({"error": "Invalid credentials"}), 401
    '''


if __name__ == '__main__':
    app.run(debug=True)
