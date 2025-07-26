from flask_restful import Resource, reqparse
from models import db, Booking, Space
from datetime import datetime
from flask_jwt_extended import jwt_required, get_jwt_identity
from utils import admin_required


def format_booking(b):
    return {
        "id": b.id,
        "user_id": b.user_id,
        "space_id": b.space_id,
        "date_of_booking": b.date_of_booking.strftime("%Y-%m-%d %H:%M:%S"),
        "number_of_guests": b.number_of_guests,
        "number_of_hours": b.number_of_hours,
        "total_amount": float(b.total_amount),
        "space_name": b.space.name,
        "user_name": b.user.name
    }
class BookingResource(Resource):
    @jwt_required()
    def get(self, booking_id):
        user_id = get_jwt_identity()
        if not user_id:
            return {"error": "Unauthorized"}, 401
        booking = Booking.query.get(booking_id)
        if booking:
            return format_booking(booking), 200
        return {"error": "Booking not found"}, 404

    @jwt_required()
    def delete(self, booking_id):
        user_id = get_jwt_identity()
        users_id = int(user_id)
        booking = Booking.query.get(booking_id)
        if not booking:
            return {"error": "Booking not found"}, 404
        if booking.user_id != users_id:
            return {"error": "Unauthorized"}, 403
        try:
            db.session.delete(booking)
            db.session.commit()
            return {"message": "Booking deleted successfully"}, 200
        except Exception as e:
            db.session.rollback()
            return {"error": f"Error deleting booking: {str(e)}"}, 400


class BookingListResource(Resource):
    @admin_required()
    def get(self):
        # Retrieve all bookings. Only accessible by admin users.
        bookings = Booking.query.all()
        return [format_booking(b) for b in bookings], 200

    @jwt_required()
    def post(self):
        user_id = get_jwt_identity()

        parser = reqparse.RequestParser()
        parser.add_argument(
            "space_name", type=str, required=True, help="Space name is required"
        )
        parser.add_argument(
            "number_of_guests",
            type=int,
            required=True,
            help="Number of guests is required",
        )
        parser.add_argument(
            "date_of_booking",
            type=str,
            required=True,
            help="Date of booking is required",
        )
        parser.add_argument('number_of_hours', type=int, required=True, help='Number of hours is required')
        args = parser.parse_args()
    
        space = Space.query.filter_by(name=args["space_name"]).first()
        space_id = space.id

        if not space_id:
            return {"error": "Space not found"}, 404

        try:
            date_of_booking = datetime.strptime(
                args["date_of_booking"], "%Y-%m-%d %H:%M:%S"
            )
        except ValueError:
            return {"error": "Invalid date format. Use YYYY-MM-DD HH:MM:SS"}, 400

        try:
            number_of_hours = args['number_of_hours']
            rent_rate = float(space.rent_rate)
            if number_of_hours <= 0 or rent_rate <= 0:
                return {"error": "Invalid number of hours or rent rate"}, 400

            total_amount = rent_rate * number_of_hours

            booking = Booking(
                user_id=user_id,
                space_id=space_id,
                number_of_guests=args["number_of_guests"],
                date_of_booking=date_of_booking,
                number_of_hours=number_of_hours,
                total_amount= total_amount
            )
            db.session.add(booking)
            if date_of_booking > datetime.utcnow():
                space.available = False

            db.session.commit()

            db.session.commit()
            return format_booking(booking), 201

        except Exception as e:
            db.session.rollback()
            return {"error": f"Error creating booking: {str(e)}"}, 400


class UserBookingsResource(Resource):
    @jwt_required()
    def get(self, user_id):
        present_user = get_jwt_identity()
        current_user = int(present_user)
        if current_user != user_id:
            return {"error": "Unauthorized"}, 403

        bookings = Booking.query.filter_by(user_id=user_id).all()
        return [format_booking(b) for b in bookings], 200
