from flask import jsonify
from flask_restful import Resource, reqparse
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import Category, db


class CategoryResource(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument("name", type=str, required=True, help="Category name is required")
    parser.add_argument("image_url", type=str, required=True, help="Image URL is required")
    @jwt_required()
    def get(self, id=None):
        # user_id = get_jwt_identity()

        if id is None:
            categories = Category.query.all()
            return jsonify([category.to_dict() for category in categories]) # displayes image in get resource
        else:
            category = Category.query.filter_by(id=id).first()
            if category is None:
                return {"message": "Category not found"}, 404
            return jsonify(category.to_dict())

    @jwt_required()
    def post(self):
        user_id = get_jwt_identity()
        data = self.parser.parse_args()

        if not data.get("name"):
            return {"message": "Category name is required"}, 400
        if not data.get("image_url"):
            return {"message": "Image URL is required"}, 400


        category = Category(name=data["name"], image_url=data["image_url"], user_id=user_id)
        db.session.add(category)
        db.session.commit()

        return {"message": "Category created successfully"}, 201

    @jwt_required()
    def patch(self, id):
        user_id = get_jwt_identity()
        data = self.parser.parse_args()

        category = Category.query.filter_by(id=id, user_id=user_id).first()
        if category is None:
            return {"message": "Category not found"}, 404

        if not data.get("name"):
            return {"message": "Category name is required"}, 400
        if not data.get("image_url"):
            return {"message": "Image URL is required"}, 400


        category.name = data["name"]
        category.image_url = data["image_url"]
        db.session.commit()

        return {
            "message": "Category updated successfully",
            "category": category.to_dict(),
        }, 200

    @jwt_required()
    def delete(self, id):
        user_id = get_jwt_identity()
        category = Category.query.filter_by(id=id, user_id=user_id).first()

        if category is None:
            return {"message": "Category not found"}, 404

        db.session.delete(category)
        db.session.commit()

        return {"message": "Category deleted successfully"}, 200
    