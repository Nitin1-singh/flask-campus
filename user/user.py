from flask import Blueprint, request, jsonify
import jwt
from prisma import Prisma
import datetime
import os
import bcrypt


# Hash the password before storing it in the database
def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed_password.decode("utf-8")


def check_password(entered_password: str, stored_hashed_password: str) -> bool:
    return bcrypt.checkpw(
        entered_password.encode("utf-8"), stored_hashed_password.encode("utf-8")
    )


user_blueprint = Blueprint("user", __name__)

SECRET_KEY = os.getenv("SECRET_KEY")


@user_blueprint.route("/create-user", methods=["POST"])
async def create_user():
    try:
        prisma = Prisma()
        await prisma.connect()
        user_data = request.get_json()
        expiration_time = datetime.datetime.now(
            datetime.timezone.utc
        ) + datetime.timedelta(hours=2)
        username = user_data.get("username")
        password = user_data.get("password")
        name = user_data.get("fullName")
        # create user
        existing_user = await prisma.user.find_first(where={"username": username})
        if existing_user:
            # If username exists, return an error response
            return (
                jsonify(
                    {
                        "message": "Username already exists. Please choose a different one."
                    }
                ),
                400,
            )
        user = await prisma.user.create(
            data={
                "name": name,
                "username": username,
                "password": hash_password(password=password),
            }
        )
        await prisma.disconnect()
        token = jwt.encode(
            {
                "id": user.id,  # Ideally this would be dynamic, like from the user data or database
                "name": str(user.name),
                "exp": expiration_time,  # Expiration time set dynamically
            },
            SECRET_KEY,
            algorithm="HS256",
        )
        return jsonify({"message": "User created successfully", "token": token}), 200
    except Exception as e:
        print("Error:", e)
        await prisma.disconnect()
        return jsonify({"message": "Internal Server Error"}), 500


@user_blueprint.route("/get-user", methods=["GET"])
async def get_user():
    try:
        prisma = Prisma()
        await prisma.connect()
        users = await prisma.user.find_many()
        await prisma.disconnect()
        users_dict = []
        for user in users:
            user_dict = {
                "id": user.id,
                "name": user.name,
                "username": user.username,
                "password": user.password,
                "createdAt": user.createdAt.isoformat(),  # Convert datetime to ISO 8601 string
            }
            users_dict.append(user_dict)
        return jsonify({"user": users_dict})
    except Exception as e:
        print("Error:", e)
        await prisma.disconnect()
        return jsonify({"message": "Internal Server Error"}), 500


@user_blueprint.route("/login-user", methods=["POST"])
async def login_user():
    try:
        prisma = Prisma()
        await prisma.connect()
        user_data = request.get_json()
        expiration_time = datetime.datetime.now(
            datetime.timezone.utc
        ) + datetime.timedelta(hours=24)
        username = user_data.get("username")
        password = user_data.get("password")
        # create user
        user = await prisma.user.find_first(where={"username": username})
        await prisma.disconnect()
        # If user exists, verify password
        if check_password(password, user.password):
            token = jwt.encode(
                {
                    "id": user.id,  # Ideally this would be dynamic, like from the user data or database
                    "name": str(user.name),
                    "exp": expiration_time,  # Expiration time set dynamically
                },
                SECRET_KEY,
                algorithm="HS256",
            )
            return (
                jsonify(
                    {
                        "message": "Login successfully",
                        "token": token,
                        "user": {"name": user.name},
                    }
                ),
                200,
            )

        else:
            return jsonify({"message": "Invalid username or password"}), 401

    except Exception as e:
        print("Error:", e)
        await prisma.disconnect()
        return jsonify({"message": "Internal Server Error"}), 500
