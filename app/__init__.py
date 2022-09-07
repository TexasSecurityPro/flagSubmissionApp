from flask import Flask
from flask_bootstrap import Bootstrap
from app.database import init_db

app = Flask(__name__, instance_relative_config=True)

from app import views

app.config.from_object('config')

bootstrap = Bootstrap(app)

init_db()