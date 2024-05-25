from flask import Flask
from flask_socketio import SocketIO
from flask_cors import CORS
import os
import logging
from kittysploit.base.kitty_path import base_path

print(base_path())
app = Flask(
    __name__,
    template_folder=base_path() + "/core/framework/browser_server/templates/",
    static_folder=base_path() + "/core/framework/browser_server/static/",
)
app.config["SECRET_KEY"] = os.urandom(32)


sio = SocketIO()
sio.init_app(app, async_mode="threading", cors_allowed_origins="*")

CORS(app, resources={r"/*": {"origins": "*"}})
