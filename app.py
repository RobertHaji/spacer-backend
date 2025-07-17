from flask import Flask
from flask_restful import Api
from flask_migrate import Migrate
from models import db
from resources.bookings import BookingResource
from resources.categories import CategoryResource
from resources.spaces import SpaceResource
from resources.users import UserResource,SignInResource,SignUpResource
from resources.images import ImageResource

# import os
app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///spacer.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True

db.init_app(app)
migrate = Migrate(app, db)
api = Api(app)


api.add_resource(SpaceResource, '/spaces','/spaces/<int:id')
api.add_resource(CategoryResource, '/categories','/categories/<int:id')
api.add_resource(BookingResource, '/bookings','/bookings/<int:id',"/users/<int:user_id>/bookings")
api.add_resource(ImageResource, '/images','/images/<int:id')
api.add_resource(UserResource, '/users','/users/<int:id')
api.add_resource(SignInResource, '/users','/users/<int:id')
api.add_resource(SignUpResource, '/users','/users/<int:id')



if __name__ == "__main__":
    app.run(port=5555)