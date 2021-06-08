from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from src import config

db = SQLAlchemy()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = config.DATABASE_URI

db.init_app(app)
#
# with app.app_context():
#     db.create_all()


