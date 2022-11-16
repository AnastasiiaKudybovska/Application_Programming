from flask import Flask
from wsgiref.simple_server import make_server
from flask_jwt_extended import JWTManager
from blueprint import api_blueprint
from config import Config

app = Flask(__name__)
app.config.from_object(Config)
jwt = JWTManager(app)

with make_server('', 5000, app) as server:
    # app.register_blueprint(api_blueprint, url_prefix='/api/v1')
    app.register_blueprint(api_blueprint, url_prefix='/api/student_rating')
    server.serve_forever()
