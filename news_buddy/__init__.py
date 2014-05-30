import flask.ext.api
import os

static_path = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../ui/"))
app = flask.ext.api.FlaskAPI("NewsBuddy", static_folder=static_path, static_url_path="")