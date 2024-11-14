from flask import Blueprint, jsonify, request, json
from prisma import Prisma
import os
from middleware.middleware import token_required

quiz_blueprint = Blueprint("quiz", __name__)

SECRET_KEY = os.getenv("SECRET_KEY")


@quiz_blueprint.route("/get-all-quiz", methods=["GET"])
# @token_required
async def get_all_quiz():
    try:
        prisma = Prisma()
        await prisma.connect()
        all_data = await prisma.quiz.find_many(
            include={
                "responses": {"include": {"quiz": True, "user": True}},
            }
        )
        await prisma.disconnect()
        all_quiz = []
        for data in all_data:
            all_quiz.append(
                {
                    "id": data.id,
                    "quizName": data.title,
                    "description": data.title,
                    "questions": data.questions,
                    "responses": [
                        {
                            "userId": response.userId,  # Include userId from UserResponse
                            "quizId": response.quizId,  # Include quizId from UserResponse
                            "responses": response.responses,  # Extract responses from related UserResponse records
                        }
                        for response in data.responses
                    ],
                }
            )
        return (
            jsonify({"message": "Success", "data": all_quiz}),
            200,
        )

    except Exception as e:
        print("Error:", e)
        await prisma.disconnect()
        return jsonify({"message": "Internal Server Error"}), 500


@quiz_blueprint.route("/get-all-response/<int:userId>", methods=["GET"])
# @token_required
async def get_all_response(userId):
    try:
        prisma = Prisma()
        await prisma.connect()
        all_data = await prisma.userresponse.find_many(
            where={"userId": userId},
            include={"quiz": True},
        )
        print(all_data)
        await prisma.disconnect()
        all_quiz = []
        for data in all_data:
            print(data)
            all_quiz.append(
                {
                    "id": data.id,
                    "quizName": data.quiz.title,
                    "questions": data.quiz.questions,
                    "userId": data.userId,  # Include userId from UserResponse
                    "quizId": data.quizId,  # Include quizId from UserResponse
                    "responses": data.responses,
                    "createdAt": data.createdAt,
                    "score": data.my_score,
                }
            )
        return (
            jsonify({"message": "Success", "data": all_quiz}),
            200,
        )

    except Exception as e:
        print("Error:", e)
        await prisma.disconnect()
        return jsonify({"message": "Internal Server Error"}), 500


@quiz_blueprint.route("/get-quiz/<int:quiz_id>", methods=["GET"])
# @token_required
async def get_quiz_by_id(quiz_id):
    try:
        prisma = Prisma()
        await prisma.connect()
        data = await prisma.quiz.find_first(where={"id": quiz_id})
        await prisma.disconnect()
        return (
            jsonify(
                {
                    "message": "Success",
                    "id": data.id,
                    "quizName": data.title,
                    "description": data.title,
                    "questions": data.questions,
                    "passing_score": data.passingMark,
                    "attemp": "not_vis",
                }
            ),
            200,
        )

    except Exception as e:
        print("Error:", e)
        await prisma.disconnect()
        return jsonify({"message": "Internal Server Error"}), 500


@quiz_blueprint.route("/submit-quiz/<int:quiz_id>", methods=["POST"])
# @token_required
async def submit_quiz(quiz_id):
    try:
        user_data = request.get_json()
        response = json.dumps(user_data["response"])
        prisma = Prisma()
        await prisma.connect()
        print("Response Data Type:", type(response))  # Should be <class 'dict'>
        print("Response Content:", response)
        data = await prisma.userresponse.create(
            data={
                "responses": response,
                "quizId": quiz_id,
                "userId": user_data["userId"],
                "my_score": user_data["my_score"],
            }
        )
        await prisma.disconnect()
        return (
            jsonify(
                {
                    "message": "Success",
                }
            ),
            200,
        )

    except Exception as e:
        print("Error:", e)
        await prisma.disconnect()
        return jsonify({"message": "Internal Server Error"}), 500


@quiz_blueprint.route("/get-leaderboard", methods=["GET"])
# @token_required
async def get_leaderboard():
    try:
        prisma = Prisma()
        await prisma.connect()
        responses = await prisma.userresponse.find_many(include={"user": True})

        # Dictionary to store the max score for each user per quiz
        user_max_scores = {}

        # Loop through all responses and determine the max score for each user-quiz pair
        for response in responses:
            user_id = response.userId
            quiz_id = response.quizId
            score = response.my_score

            # Initialize user if not already in dictionary
            if user_id not in user_max_scores:
                user_max_scores[user_id] = {}

            # Initialize quiz for the user if not already in dictionary
            if quiz_id not in user_max_scores[user_id]:
                user_max_scores[user_id][quiz_id] = score
            else:
                # Update the max score for the quiz, if the current score is higher
                user_max_scores[user_id][quiz_id] = max(
                    user_max_scores[user_id][quiz_id], score
                )

        # Now sum the max scores for each user across all quizzes
        user_total_scores = []

        for user_id, quizzes in user_max_scores.items():
            total_score = sum(quizzes.values())  # Sum the max scores for each user
            name = (
                await prisma.user.find_unique(where={"id": user_id})
            ).name  # Fetch username for the user
            user_total_scores.append({"name": name, "totalMaxScore": total_score})

        # Sort the leaderboard by total score in descending order
        user_total_scores.sort(key=lambda x: x["totalMaxScore"], reverse=True)
        print(user_total_scores)
        return user_total_scores

        return "good"
        return (
            jsonify({"message": "Success", "data": all_quiz}),
            200,
        )

    except Exception as e:
        print("Error:", e)
        await prisma.disconnect()
        return jsonify({"message": "Internal Server Error"}), 500
