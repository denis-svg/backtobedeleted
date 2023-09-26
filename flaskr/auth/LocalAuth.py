from flaskr.auth.AuthManagerInterface import AuthManagerInterface
from werkzeug.security import check_password_hash, generate_password_hash
import jwt
import datetime
from flaskr.db import get_db
from mysql.connector.errors import IntegrityError
from functools import wraps
from flask import current_app, jsonify

class LocalAuth(AuthManagerInterface):
    def registerUser(self, request):
        if request.method == "POST":
            username = request.json["username"]
            password = request.json["password"]
            
            db = get_db()
            cursor = db.cursor()
            error = None

            if not username:
                error = 'Username is required.'
            elif not password:
                error = 'Password is required.'

            if error is None:
                try:
                    cursor.execute(
                        "INSERT INTO users (username, password) VALUES (%s, %s)",
                        (username, generate_password_hash(password)),
                    )
                    db.commit()
                except IntegrityError:
                    cursor.close()
                    return {"error": f"User {username} is already registered.",
                            "status": 409}
                finally:
                    cursor.close()
            
            return {"message": "Registration successful.",
                            "status": 201}
        
    def loginUser(self, request):
        if request.method == "POST":
            username = request.json["username"]
            password = request.json["password"]

            db = get_db()
            cursor = db.cursor(dictionary=True)
            error = None

            cursor.execute(f'SELECT * FROM users WHERE username = %s', (username,))

            user = cursor.fetchone()

            if user is None:
                error = 'Incorrect username.'
            elif not check_password_hash(user['password'], password):
                error = 'Incorrect password.'

            if error is None:
                token = jwt.encode({"user":username, "exp":datetime.datetime.utcnow() + datetime.timedelta(minutes=30), "role":"basic"},
                                current_app.config["SECRET_KEY"])
                return {"message": "Login succesful",
                        "token":token,
                        "status":200}
        return {"error":error,
                "status": 401}
    
    def tokenRequired(self, request, role):
        def decorator(view):
            @wraps(view)
            def wrapped_view(*args, **kwargs):
                token = request.headers["Authorization"].split()[1]
                
                if not token:
                    return jsonify({"error":"Token is missing"}), 401

                try:
                    data = jwt.decode(token, current_app.config["SECRET_KEY"], algorithms=["HS256"])
                    if data['role'] != role:
                        return jsonify({"error":"You dont have permision"}), 403
                except Exception as e:
                    return jsonify({"error":"Token is invalid"}), 401
                return view(*args, **kwargs)

            return wrapped_view
        return decorator