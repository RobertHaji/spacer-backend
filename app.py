from flask import Flask
from flask_restful import Api, Resource
from flask_migrate import Migrate
from models import db
# import os
app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///spacer.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True

db.init_app(app)
migrate = Migrate(app, db)
api = Api(app)

if __name__ == "__main__":
    app.run(port=5555)