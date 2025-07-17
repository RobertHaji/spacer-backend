from flask_restful import Resource , reqparse
from models import db, Booking, Space

class BookingResource(Resource):
    def get (self, booking_id):
        if not booking_id:
            bookings = Booking.query.all()
            return [booking.to_dict() for booking in bookings], 200
        
        booking= Booking.query.get(booking_id)
        if booking:
            return booking.to_dict(), 200
        else:
            return {"error": "Booking not found"}, 404
        
    def get_bookings_by_user(self, user_id):
        bookings = Booking.query.filter_by(user_id=user_id).all()
        return [booking.to_dict() for booking in bookings], 200
    
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('user_id', type=int, required=True, help='User ID is required')
        parser.add_argument('space_id', type=int, required=True, help='Space ID is required')
        parser.add_argument('number_of_guests', type=int, required=True, help='Number of guests is required')
        parser.add_argument('date_of_booking', type=str, required=True, help='Date of booking is required')
        parser.add_argument('number_of_hours', type=int, required=True, help='Number of hours is required')
        args = parser.parse_args()

        space = Space.query.get(args['space_id'])
        if not space:
            return {"error": "Space not found"}, 404

        try:
            number_of_hours = args['number_of_hours']
            rent_rate = float(space.rent_rate)
            total_amount = rent_rate * number_of_hours
            if number_of_hours <= 0 or rent_rate <= 0:
                return {"error": "Invalid number of hours or rent rate"}, 400
            booking = Booking(
                user_id=args['user_id'],
                space_id=args['space_id'],
                number_of_guests=args['number_of_guests'],
                date_of_booking=args['date_of_booking'],
                total_amount=total_amount
            )
            db.session.add(booking)
            db.session.commit()
            return booking.to_dict(), 201
        except Exception as e:
            db.session.rollback()
            return {"error": f"Error creating booking: {str(e)}"}, 400