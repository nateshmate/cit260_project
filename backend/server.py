from flask import Flask, request, jsonify 
from flask_cors import CORS 
import pymysql
import re

app = Flask(__name__)
CORS(app)  

# Temporary storage for user input
# accounts = {}

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
def validate_email(email):
    pattern = r'^\d{10}@student\.csn\.edu$'
    return re.match(pattern, email) is not None


@app.route('/create_account', methods=['POST'])
def create_account():
    data = request.json
    first_name = data.get("first_name")
    last_name = data.get("last_name")
    role = data.get("role")
    username = data.get("username")
    password = data.get("password")

    if not all([first_name, last_name, role, username, password]):
        return jsonify({"error": "All fields are required"}), 400

    if role not in ['student', 'faculty']:
        return jsonify({"error": "Invalid role"}), 400
    
    if not validate_email(username):
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
            sql = """INSERT INTO authentication (firstname, lastname, email, password, role)
                     VALUES (%s, %s, %s, %s, %s)"""
            cursor.execute(sql, (first_name, last_name, username, password, role))
            conn.commit()

            # Insert new account into student or faculty table based on role
            if role == 'student':
                # Insert into student table
                sql = """INSERT INTO student (firstname, lastname) VALUES (%s, %s)"""
                cursor.execute(sql, (first_name, last_name))
                conn.commit()

            elif role == 'faculty':
                # Insert into faculty table
                sql = """INSERT INTO faculty (firstname, lastname) VALUES (%s, %s)"""
                cursor.execute(sql, (first_name, last_name))
                conn.commit()


        return jsonify({"message": f"Account created successfully for {first_name} {last_name}"}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if conn:
            conn.close()

    '''
    if username in accounts:
        return jsonify({"error": "Account already exists"}), 400

    accounts[username] = {
        'first_name': first_name,
        'last_name': last_name,
        'role': role,
        'password': password
    }
    return jsonify({"message": f"Account created successfully for {first_name} {last_name}"}), 201
    '''
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
                return jsonify({
                    "message": f"Welcome, {user['firstname']}!",
                    "first_name": user['firstname'],
                    "last_name": user['lastname'],
                    "role": user['role']
                }), 200
            else:
                return jsonify({"error": "Invalid credentials"}), 401
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if conn:
            conn.close()

    '''
    if username in accounts and accounts[username]['role'] == role and accounts[username]['password'] == password:
        return jsonify({
            "message": f"Welcome, {accounts[username]['first_name']}!",
            "first_name": accounts[username]['first_name'],
            "last_name": accounts[username]['last_name'],
            "role": role  
        }), 200
    return jsonify({"error": "Invalid credentials"}), 401
    '''


if __name__ == '__main__':
    app.run(debug=True)


