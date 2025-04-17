from flask import Flask, request, jsonify 
from flask_cors import CORS 
import re

app = Flask(__name__)
CORS(app)  

# Temporary storage for user input
accounts = {}

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

    if not all([first_name, last_name, role, username, password]):
        return jsonify({"error": "All fields are required"}), 400

    if role not in ['student', 'faculty']:
        return jsonify({"error": "Invalid role"}), 400
    
    if not validate_email(username, role):
        return jsonify({"error": "Invalid email format"}), 400


    expected_password = username[:10]  # Extract first 10 characters of email
    if password != expected_password:
        return jsonify({"error": "Password must be NSHE# (first 10 characters of email)"}), 400

    if username in accounts:
        return jsonify({"error": "Account already exists"}), 400

    accounts[username] = {
        'first_name': first_name,
        'last_name': last_name,
        'role': role,
        'password': password
    }
    return jsonify({"message": f"Account created successfully for {first_name} {last_name}"}), 201

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    role = data.get("role")
    username = data.get("username")
    password = data.get("password")

    if username in accounts and accounts[username]['role'] == role and accounts[username]['password'] == password:
        return jsonify({
            "message": f"Welcome, {accounts[username]['first_name']}!",
            "first_name": accounts[username]['first_name'],
            "last_name": accounts[username]['last_name'],
            "role": role  
        }), 200
    return jsonify({"error": "Invalid credentials"}), 401


if __name__ == '__main__':
    app.run(debug=True)


