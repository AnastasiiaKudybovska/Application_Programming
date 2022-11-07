from flask import Flask
from wsgiref.simple_server import make_server

from blueprint import api_blueprint

app = Flask(__name__)

with make_server('', 5000, app) as server:
    # app.register_blueprint(api_blueprint, url_prefix='/api/v1')
    app.register_blueprint(api_blueprint, url_prefix='/api/student_rating')
    server.serve_forever()
