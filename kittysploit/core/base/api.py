from kittysploit.core.base.sessions import Sessions
from kittysploit.core.base.config import KittyConfig
from flask import Flask, jsonify, request
from flask_restful import Resource, Api, reqparse
from datetime import datetime, timedelta
import jwt
import os, sys
from functools import wraps
import logging
import base64

log = logging.getLogger("werkzeug")
log.setLevel(logging.ERROR)
log.disabled = True

app = Flask(__name__)
app.config["SECRET_KEY"] = os.urandom(32)
app.logger.disabled = True

cli = sys.modules["flask.cli"]
cli.show_server_banner = lambda *x: None

api = Api(app)
my_config = KittyConfig()
user = my_config.get_config("API", "username")
if not user:
    user = "kitty"

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        response = {"success": False, "message": "Unauthorized Access!"}
        token = None
        if "x-access-token" in request.headers:
            token = request.headers["x-access-token"]
            print(token)
        if not token:
            return response, 401

        try:
            data = jwt.decode(token, app.config["SECRET_KEY"])
            print(data)
            current_user = {"user": "kitty"}
            if not current_user:
                return response, 401
        except:
            return response, 401
        return f(*args, **kwargs)

    return decorated


class All_sessions_api(Resource):

    @token_required
    def get(self):
        session = Sessions()
        all_sessions = session.get_sessions()
        data = {}
        for i in all_sessions:
            data.update(
                {
                    i: {
                        "user": all_sessions[i]["user"],
                        "arch": all_sessions[i]["arch"],
                        "version": all_sessions[i]["version"],
                        "shell": all_sessions[i]["shell"],
                        "host": all_sessions[i]["host"],
                        "port": all_sessions[i]["port"],
                    }
                }
            )
        return jsonify(data)


class Session_interact(Resource):

#    @token_required
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument(
            "id_session",
            type=str,
            help="You need to enter your full name",
            required=True,
        )
        parser.add_argument(
            "cmd", type=str, help="Your command in base64 encoded", required=True
        )

        args = parser.parse_args()

        id_session = args.get("id_session")
        cmd = args.get("cmd")

        command = base64.b64decode(cmd).decode()
        session = Sessions()
        data = session.execute(id_session, command, raw=True)

        return jsonify({"data": data})


class Check_session(Resource):

#    @token_required
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument("id_session", type=str, help="", required=True)
        args = parser.parse_args()
        id_session = args.get("id_session")

        response = {"success": False, "message": "Session not found"}
        sessions = Sessions()
        all_sessions = sessions.get_sessions()
        if int(id_session) in all_sessions:
            response["success"] = True
            response["message"] = "Session exist"
            return response, 200
        return response, 200


class Login_api(Resource):

    def get(self):

        parser = reqparse.RequestParser()
        parser.add_argument(
            "username", type=str, help="You need to enter your username", required=True
        )
        parser.add_argument("password", type=str, help="Your password", required=True)

        args = parser.parse_args()

        username = args.get("username")
        password = args.get("password")

        response = {"success": False, "message": "Invalid parameters", "token": ""}
        try:

            if not username or not password:
                response["message"] = "Invalid data"
                return response, 422

            if username != my_config.get_config("API", "username"):
                response["message"] = "Unauthorized Access!"
                return response, 401

            if password == my_config.get_config("API", "password"):
                token = jwt.encode(
                    {
                        "user": username,
                        "exp": datetime.utcnow() + timedelta(minutes=120),
                    },
                    app.config["SECRET_KEY"],
                )

                response["message"] = "token generated"
                response["token"] = token
                response["success"] = True
                return response, 200

            response["message"] = "Invalid emailid or password"
            return response, 403

        except Exception as ex:
            return response, 422

class API:

    def run(self, port):

        api.add_resource(All_sessions_api, "/api/sessions")
        api.add_resource(Session_interact, "/api/interact")
        api.add_resource(Check_session, "/api/check_session")
        api.add_resource(Login_api, "/api/login")
        app.logger.disabled = True

        app.run(host="0.0.0.0", port=int(port))
