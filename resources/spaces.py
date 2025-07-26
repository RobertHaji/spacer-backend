from flask_restful import Resource, reqparse
from models import db, Space, Category
from datetime import datetime
from models import Booking
from utils import admin_required

def format_space(self):
    return {
        "id": self.id,
        "name": self.name,
        "owner_name": self.owner_name,
        "description": self.description,
        "rent_rate": float(self.rent_rate),
        "image_url": self.image_url,
        "available": self.available,
        "location": self.location,
        "time_available": self.time_available,
        "category_id": self.category_id,
        "user_id": self.user_id,
        "created_at": self.created_at.isoformat()
        if self.created_at
        else None,  
        "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        "deleted_at": self.deleted_at.isoformat() if self.deleted_at else None,
        "category_name": self.category.name if self.category else None,
    }
def update_space_availability():
    now = datetime.utcnow()
    spaces = Space.query.all()

    for space in spaces:
        booking = Booking.query.filter_by(space_id=space.id).order_by(Booking.date_of_booking.desc()).first()

        if booking and booking.date_of_booking > now:
            space.available = False
        else:
            space.available = True

        print(f"{space.name} → available: {space.available}, category: {space.category_id}")

    db.session.commit()
class SpaceResource(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument("name", type=str, required=True, help="Name is required")
    parser.add_argument(
        "owner_name", type=str, required=True, help="Owner name is required"
    )
    parser.add_argument(
        "description", type=str, required=True, help="Description is required"
    )
    parser.add_argument(
        "rent_rate", type=float, required=True, help="Rent rate is required"
    )
    parser.add_argument(
        "image_url", type=str, required=True, help="Image URL is required"
    )
    parser.add_argument(
        "available", type=bool, required=False, help="time available is required"
    )
    # Adds location to the parser. Its an update
    parser.add_argument(
        "location", type=str, required=True, help="Location is required"
    )

    parser.add_argument(
        "time_available", type=str, required=False, help="time available is required"
    )
    parser.add_argument(
        "category_id", type=int, required=True, help="Category ID is required"
    )

    def get(self, id=None):
        if id:
            space = Space.query.get(id)
            if space:
                return format_space(space), 200
            return {"error": "Space not found"}, 404
        else:
            spaces = Space.query.all()
            return [format_space(space) for space in spaces], 200


    @admin_required()
    def post(self):
        data = self.parser.parse_args()

        # Name and owner_name validation(must not be empty)
        if not data["name"].strip():
            return {"error": "Name cannot be empty"}, 400
        if not data["owner_name"].strip():
            return {"error": "Owner name cannot be empty"}, 400

        # Rent validation(Rent rate must be positive number)
        if data["rent_rate"] <= 0:
            return {"error": "Rent rate must be a positive number"}, 400

        # Category-id validation (category_id must exist)
        if not Category.query.get(data["category_id"]):
            return {"error": "Invalid category_id — category not found"}, 400

        space = Space(**data)
        db.session.add(space)
        db.session.commit()

        return {"message": "Space successfully created", "space": format_space(space)}, 201

    def patch(self, id):
        space = Space.query.filter_by(id=id).first()
        if not space:
            return {"error": "Space not found"}, 404

        data = self.parser.parse_args()

        # Rent validation(Rent rate must be positive number)
        if data["rent_rate"] is not None and data["rent_rate"] <= 0:
            return {"error": "Rent rate must be a positive number "}, 400

        # Name and owner_name validation(must not be empty)
        if data["name"] is not None and not data["name"].strip():
            return {"error": "Name cannot be empty"}, 400
        if data["owner_name"] is not None and not data["owner_name"].strip():
            return {"error": "Owner name cannot be empty"}, 400

        # Category-id validation if it is provided
        if data["category_id"] is not None and not Category.query.get(
            data["category_id"]
        ):
            return {"error": "Invalid category_id — category not found"}, 400

        # Update only the provided fields in the request
        for key, value in data.items():
            if value is not None:
                setattr(space, key, value)

        db.session.commit()
        return {"message": "Update successful", "space": format_space(space)}, 200

    @admin_required()
    def delete(self, id):
        space = Space.query.filter_by(id=id).first()
        if not space:
            return {"error": "Space not found"}, 404

        # Delete related bookings first

        if space.bookings:
         for booking in space.bookings:
            db.session.delete(booking)

        db.session.delete(space)
        db.session.commit()
        return {"message": "Space deleted successfully"}, 200


#  Resource to Get Spaces by Category
class SpacesByCategory(Resource):
    def get(self, category_id):
        spaces = Space.query.filter_by(category_id=category_id).all()
        return [format_space(space) for space in spaces], 200
