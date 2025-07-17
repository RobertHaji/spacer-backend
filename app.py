from flask import Flask
from flask_restful import Api
from flask_migrate import Migrate
from models import db
from resources.bookings import BookingResource, BookingListResource, UserBookingsResource
from resources.categories import CategoryResource
from resources.spaces import SpaceResource,SpacesByCategory
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

@app.route("/")
def index():
    return {"message": "Welcome to Spacer API!"}

api.add_resource(SpaceResource, "/spaces", "/spaces/<int:id>")
api.add_resource(SpacesByCategory, "/categories/<int:category_id>/spaces")
api.add_resource(CategoryResource, '/categories', '/categories/<int:id>')
api.add_resource(BookingListResource, '/bookings')  # gets all the bookings and posts a new booking
api.add_resource(BookingResource, '/bookings/<int:booking_id>')  # gets a single specific booking.
api.add_resource(UserBookingsResource, '/users/<int:user_id>/bookings')  # gets all the bookings for a particular user
api.add_resource(ImageResource, '/images', '/images/<int:id>')
api.add_resource(UserResource, '/users', '/users/<int:id>')
api.add_resource(SignInResource, '/signin')
api.add_resource(SignUpResource, '/signup')



if __name__ == "__main__":
    app.run(port=5555)