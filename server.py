import sqlite3
import bcrypt
import json
from flask import Flask, request, jsonify

app = Flask(__name__)

# Database Initialization
def init_db():
    connection = sqlite3.connect("notes.db")
    cursor = connection.cursor()
    # Create accounts table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS accounts (
            username TEXT PRIMARY KEY,
            password TEXT
        )
    """)
    # Create notes table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            title TEXT,
            body TEXT,
            FOREIGN KEY (username) REFERENCES accounts (username)
        )
    """)
    connection.commit()
    connection.close()

init_db()

# Helper Functions
def hash_password(password):
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

def verify_password(password, hashed_password):
    return bcrypt.checkpw(password.encode("utf-8"), hashed_password.encode("utf-8"))

# Routes
@app.route("/signup", methods=["POST"])
def signup():
    data = request.json
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"status": 400, "message": "Username and password required"}), 400

    connection = sqlite3.connect("notes.db")
    cursor = connection.cursor()

    # Check if user already exists
    cursor.execute("SELECT * FROM accounts WHERE username = ?", (username,))
    if cursor.fetchone():
        connection.close()
        return jsonify({"status": 409, "message": "Username already exists"}), 409

    # Add user to the database
    hashed_password = hash_password(password)
    cursor.execute("INSERT INTO accounts (username, password) VALUES (?, ?)", (username, hashed_password))
    connection.commit()
    connection.close()

    return jsonify({"status": 200, "message": "Account created successfully"}), 200

@app.route("/login", methods=["POST"])
def login():
    data = request.json
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"status": 400, "message": "Username and password required"}), 400

    connection = sqlite3.connect("notes.db")
    cursor = connection.cursor()

    # Verify user
    cursor.execute("SELECT password FROM accounts WHERE username = ?", (username,))
    user = cursor.fetchone()
    connection.close()

    if user is None or not verify_password(password, user[0]):
        return jsonify({"status": 401, "message": "Invalid username or password"}), 401

    return jsonify({"status": 200, "message": "Login successful"}), 200

@app.route("/notes", methods=["GET", "POST", "PUT", "DELETE"])
def notes():
    data = request.json
    username = data.get("username")
    if not username:
        return jsonify({"status": 400, "message": "Username is required"}), 400

    connection = sqlite3.connect("notes.db")
    cursor = connection.cursor()

    if request.method == "GET":
        # Get all notes for the user
        cursor.execute("SELECT title, body FROM notes WHERE username = ?", (username,))
        notes = [{"title": row[0], "body": row[1]} for row in cursor.fetchall()]
        connection.close()
        return jsonify({"status": 200, "notes": notes}), 200

    elif request.method == "POST":
        title = data.get("title")
        body = data.get("body")
        if not title or not body:
            return jsonify({"status": 400, "message": "Title and body required"}), 400

        # Add a note
        cursor.execute("INSERT INTO notes (username, title, body) VALUES (?, ?, ?)", (username, title, body))
        connection.commit()
        connection.close()
        return jsonify({"status": 200, "message": "Note added successfully"}), 200

    elif request.method == "PUT":
        title = data.get("title")
        body = data.get("body")
        if not title or not body:
            return jsonify({"status": 400, "message": "Title and body required"}), 400

        # Update a note
        cursor.execute("UPDATE notes SET body = ? WHERE username = ? AND title = ?", (body, username, title))
        connection.commit()
        connection.close()
        return jsonify({"status": 200, "message": "Note updated successfully"}), 200

    elif request.method == "DELETE":
        title = data.get("title")
        if not title:
            return jsonify({"status": 400, "message": "Title required"}), 400

        # Delete a note
        cursor.execute("DELETE FROM notes WHERE username = ? AND title = ?", (username, title))
        connection.commit()
        connection.close()
        return jsonify({"status": 200, "message": "Note deleted successfully"}), 200

# Run the server
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
