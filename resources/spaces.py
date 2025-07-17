from flask_restful import Resource, reqparse

from models import db, Space

class SpaceRescource (Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('name', type=str, required=True, help="Name is required")
    parser.add_argument('owner_name', type=str, required=True, help="Owner name is required")
    parser.add_argument('description', type=str, required=True, help="Description is required")
    parser.add_argument('rent_rate', type=float, required=True, help="Rent rate is required")
    parser.add_argument('image_url', type=str, required=True, help="Image URL is required")
    parser.add_argument('available', type=bool, required=False)
    parser.add_argument('time_available', type=str, required=False)
    parser.add_argument('category_id', type=int, required=True, help="Category ID is required")

    def get(self, id=None):
        if id is None:
            spaces = Space.query.all()
            return [space.to_dict() for space in spaces], 200
        else:
            space = Space.query.filter_by(id=id).first()
            if space:
                return space.to_dict(), 200
            return {"error": "Space not found"}, 404

    def post(self):
        data = self.parser.parse_args()
        # Rent validation(Rent rate must be positive number)
        if data['rent_rate'] <= 0:
            return {"error": "Rent rate must be a positive number"}, 400
        space = Space(**data)
        db.session.add(space)
        db.session.commit()
        return {"message": "Space successfully created", "space": space.to_dict()}, 201

    def patch(self, id):
        space = Space.query.filter_by(id=id).first()
        if not space:
            return {"message": "Space not found"}, 404

        data = self.parser.parse_args()

        # Rent validation(Rent rate must be positive number)
        if data['rent_rate'] is not None and data['rent_rate'] <= 0:
            return {"error": "Rent rate must be a positive number "}, 400

        # Update only the provided fields in the request
        for key, value in data.items():
            if value is not None:
                setattr(space, key, value)

        db.session.commit()
        return {"message": "Update successful", "space": space.to_dict()}, 200

    def delete(self, id):
        space = Space.query.filter_by(id=id).first()
        if not space:
            return {"message": "Space not found"}, 404

        db.session.delete(space)
        db.session.commit()
        return {"message": "Space deleted successfully"}, 200


