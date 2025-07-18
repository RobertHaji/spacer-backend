from flask_restful import Resource, reqparse
from models import db, Space, Category

from utils import admin_required


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
                return space.to_json(), 200
            return {"error": "Space not found"}, 404
        else:
            spaces = Space.query.all()
            return [space.to_json() for space in spaces], 200

    # @jwt_required
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

        return {"message": "Space successfully created", "space": space.to_json()}, 201

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
        return {"message": "Update successful", "space": space.to_json()}, 200

    @admin_required()
    def delete(self, id):
        space = Space.query.filter_by(id=id).first()
        if not space:
            return {"error": "Space not found"}, 404

        db.session.delete(space)
        db.session.commit()
        return {"message": "Space deleted successfully"}, 200


#  Resource to Get Spaces by Category
class SpacesByCategory(Resource):
    def get(self, category_id):
        spaces = Space.query.filter_by(category_id=category_id).all()
        return [space.to_json() for space in spaces], 200
