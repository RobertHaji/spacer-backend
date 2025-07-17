from flask_restful import Resource
from flask import request
from models import db, Booking, Space

class BookingResource(Resource):
    def get (self, booking_id):
        booking= Booking.query.get(booking_id)
        if booking:
            return booking.to_dict(), 200
        else:
            return {"message": "Booking not found"}, 404
        
    
    def post(self):
        data = request.get_json('booking')
        if not data:
            return {"message":"data must be provided"}, 400
        
        if not all(key in data for key in ("user_id", "space_id", "number_of_guests", "date_of_booking", "number_of_hours")):
            return{"message":"missing required fields"}, 400
        
        space = Space.query.get(data.get("space_id"))
        if not space:
            return {"message": "Space not found"}, 404

        try:
            number_of_hours = int(data.get("number_of_hours"))
            rent_rate = float(space.rent_rate)
            total_amount = rent_rate * number_of_hours
            if number_of_hours <= 0 or rent_rate <= 0:
                return {"message": "Invalid number of hours or rent rate"}, 400
            booking = Booking(
                user_id= data.get("user_id"),
                space_id= data.get("space_id"),
                number_of_guests= data.get("number_of_guests"),
                date_of_booking= data.get("date_of_booking"),
                total_amount= total_amount
            )    

            db.session.add(booking)
            db.session.commit()
            return booking.to_dict(), 201
        except Exception as e:
            db.session.rollback()
            return {"message": f"Error creating booking: {str(e)}"}, 400