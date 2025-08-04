from flask import Flask, request, jsonify
import sqlite3
import json
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Fixed: Remove global connection - use proper connection management
def get_db_connection():
    """Get a new database connection for each request"""
    conn = sqlite3.connect('users.db')
    conn.row_factory = sqlite3.Row  # Enable column access by name
    return conn

def close_db_connection(conn):
    """Safely close database connection"""
    if conn:
        conn.close()

@app.route('/')
def home():
    return "User Management System"

@app.route('/users', methods=['GET'])
def get_all_users():
    conn = None
    try:
        # Fixed: Using proper connection management
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, email FROM users")
        users = cursor.fetchall()
        
        user_list = []
        for user in users:
            user_list.append({
                "id": user[0],
                "name": user[1],
                "email": user[2]
            })
        
        logger.info(f"Retrieved {len(user_list)} users")
        return jsonify({"users": user_list}), 200
        
    except Exception as e:
        logger.error(f"Database error in get_all_users: {e}")
        return jsonify({"error": "Internal server error"}), 500
    finally:
        close_db_connection(conn)

@app.route('/user/<user_id>', methods=['GET'])
def get_user(user_id):
    conn = None
    try:
        # Fixed: Using proper connection management and parameterized query
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        user = cursor.fetchone()
        
        if user:
            logger.info(f"User found: {user[1]}")  # Log name only, not sensitive data
            return jsonify({
                "id": user[0],
                "name": user[1],
                "email": user[2]
                # Note: Not returning password for security
            })
        else:
            logger.info("User not found")
            return jsonify({"error": "User not found"}), 404
    except Exception as e:
        logger.error(f"Database error in get_user: {e}")
        return jsonify({"error": "Internal server error"}), 500
    finally:
        close_db_connection(conn)

@app.route('/users', methods=['POST'])
def create_user():
    conn = None
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
            
        # Input validation
        required_fields = ['name', 'email', 'password']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({"error": f"Missing required field: {field}"}), 400
        
        name = data['name']
        email = data['email']
        password = data['password']
        
        # Fixed: Using proper connection management and parameterized query
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (name, email, password) VALUES (?, ?, ?)",
                      (name, email, password))
        conn.commit()
        
        logger.info(f"User created successfully: {name}")
        return jsonify({"message": "User created successfully"}), 201
        
    except json.JSONDecodeError:
        return jsonify({"error": "Invalid JSON data"}), 400
    except Exception as e:
        logger.error(f"Database error in create_user: {e}")
        return jsonify({"error": "Internal server error"}), 500
    finally:
        close_db_connection(conn)

@app.route('/user/<user_id>', methods=['PUT'])
def update_user(user_id):
    conn = None
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
        
        name = data.get('name')
        email = data.get('email')
        
        if not name or not email:
            return jsonify({"error": "Both name and email are required"}), 400
        
        # Fixed: Using proper connection management and parameterized query
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET name = ?, email = ? WHERE id = ?",
                      (name, email, user_id))
        
        if cursor.rowcount == 0:
            return jsonify({"error": "User not found"}), 404
            
        conn.commit()
        logger.info(f"User updated successfully: {user_id}")
        return jsonify({"message": "User updated successfully"}), 200
        
    except json.JSONDecodeError:
        return jsonify({"error": "Invalid JSON data"}), 400
    except Exception as e:
        logger.error(f"Database error in update_user: {e}")
        return jsonify({"error": "Internal server error"}), 500
    finally:
        close_db_connection(conn)

@app.route('/user/<user_id>', methods=['DELETE'])
def delete_user(user_id):
    conn = None
    try:
        # Fixed: Using proper connection management and parameterized query
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
        
        if cursor.rowcount == 0:
            return jsonify({"error": "User not found"}), 404
            
        conn.commit()
        logger.info(f"User {user_id} deleted successfully")
        return jsonify({"message": "User deleted successfully"}), 200
        
    except Exception as e:
        logger.error(f"Database error in delete_user: {e}")
        return jsonify({"error": "Internal server error"}), 500
    finally:
        close_db_connection(conn)

@app.route('/search', methods=['GET'])
def search_users():
    conn = None
    try:
        name = request.args.get('name')
        
        if not name:
            return jsonify({"error": "Please provide a name to search"}), 400
        
        # Fixed: Using proper connection management and parameterized query
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, email FROM users WHERE name LIKE ?",
                      (f"%{name}%",))
        users = cursor.fetchall()
        
        # Format results as JSON
        user_list = []
        for user in users:
            user_list.append({
                "id": user[0],
                "name": user[1],
                "email": user[2]
            })
        
        logger.info(f"Search completed for: {name}, found {len(user_list)} results")
        return jsonify({"users": user_list}), 200
        
    except Exception as e:
        logger.error(f"Database error in search_users: {e}")
        return jsonify({"error": "Internal server error"}), 500
    finally:
        close_db_connection(conn)

@app.route('/login', methods=['POST'])
def login():
    conn = None
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
            
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            return jsonify({"error": "Email and password are required"}), 400
        
        # Fixed: Using proper connection management and parameterized query
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, email FROM users WHERE email = ? AND password = ?",
                      (email, password))
        user = cursor.fetchone()
        
        if user:
            logger.info(f"Successful login for user: {email}")
            return jsonify({
                "status": "success",
                "user_id": user[0],
                "name": user[1]
            }), 200
        else:
            logger.warning(f"Failed login attempt for email: {email}")
            return jsonify({"status": "failed", "error": "Invalid credentials"}), 401
            
    except json.JSONDecodeError:
        return jsonify({"error": "Invalid JSON data"}), 400
    except Exception as e:
        logger.error(f"Database error in login: {e}")
        return jsonify({"error": "Internal server error"}), 500
    finally:
        close_db_connection(conn)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5009, debug=True)