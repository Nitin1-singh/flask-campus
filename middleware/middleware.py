from flask import request, jsonify
from functools import wraps
import os
import jwt


# Function to decode the token and verify it
def token_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = None
        # Check if the token is passed in the Authorization header
        if "Authorization" in request.headers:
            token = request.headers["Authorization"].split(" ")[
                1
            ]  # Get the token after "Bearer"
        if not token:
            return jsonify({"message": "Token is missing!"}), 403

        try:
            # Decode the token
            data = jwt.decode(token, os.getenv("SECRET_KEY"), algorithms=["HS256"])
            current_user = data[
                "sub"
            ]  # Assuming the token has a 'sub' field for the user ID
        except Exception as e:
            return jsonify({"message": "Token is invalid!"}), 403

        return f(current_user, *args, **kwargs)

    return decorated_function
