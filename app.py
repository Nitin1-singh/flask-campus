from flask import Flask
from user.user import user_blueprint
from quiz.quiz import quiz_blueprint

from prisma import Prisma, register
from flask_cors import CORS
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)
CORS(app)  # Enable CORS for cross-origin requests from React
app.register_blueprint(user_blueprint, url_prefix="/user")
app.register_blueprint(quiz_blueprint, url_prefix="/quiz")


@app.route("/", methods=["GET"])
def index():
    return {"health": "check"}


if __name__ == "__main__":
    app.run(debug=True, port=5000, host="0.0.0.0", threaded=True)
