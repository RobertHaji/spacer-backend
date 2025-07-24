from flask_restful import Resource
from models import Space, User, Booking

class StatsResource(Resource):
    def get(self):
        total_spaces = Space.query.count()
        total_users = User.query.count()
        total_bookings = Booking.query.count()

        return {
            "spaces": total_spaces,
            "users": total_users,
            "bookings": total_bookings
        }, 200
