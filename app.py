import os
from flask import Flask
from flask_restful import Api
from flask_migrate import Migrate
from models import db
from resources.bookings import (
    BookingResource,
    BookingListResource,
    UserBookingsResource,
    BookingValidationResource,
)
from resources.categories import CategoryResource
from resources.spaces import SpaceResource, SpacesByCategory 
from resources.users import UserResource, SignInResource, SignUpResource
from resources.images import ImageListResource, SpaceImageListResource
from resources.stats import StatsResource
from flask_jwt_extended import JWTManager
from dotenv import load_dotenv
from flask_bcrypt import Bcrypt
from flask_cors import CORS

load_dotenv()

app = Flask(__name__)
CORS(app)

app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True

# Setup the Flask-JWT-Extended extension
app.config["JWT_SECRET_KEY"] = os.environ.get("JWT_SECRET")
jwt = JWTManager(app)
bcrypt = Bcrypt(app)

db.init_app(app)
migrate = Migrate(app, db)
api = Api(app)


@app.route("/")
def index():
    return {"message": "Welcome to Spacer API!"}


api.add_resource(SpaceResource, "/spaces", "/spaces/<int:id>")
api.add_resource(SpacesByCategory, "/categories/<int:category_id>/spaces")
api.add_resource(CategoryResource, "/categories", "/categories/<int:id>")
api.add_resource(
    BookingListResource, "/bookings"
)  # gets all the bookings and posts a new booking
api.add_resource(
    BookingResource, "/bookings/<int:booking_id>"
)  # gets a single specific booking.
api.add_resource(
    UserBookingsResource, "/users/<int:user_id>/bookings"
)  # gets all the bookings for a particular user
api.add_resource(ImageListResource, "/api/images")
api.add_resource(SpaceImageListResource, "/api/spaces/<int:space_id>/images")
api.add_resource(UserResource, "/users", "/users/<int:id>")
api.add_resource(SignInResource, "/signin")
api.add_resource(SignUpResource, "/signup")
api.add_resource(StatsResource, "/stats")
api.add_resource(BookingValidationResource, "/bookings/validate")

if __name__ == "__main__":
    app.run(port=5555)
