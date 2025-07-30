from flask import jsonify
from flask_restful import Resource, reqparse
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import Category, db, User
from utils import admin_required

def format_category(self):
    return {
        "id": self.id,
        "name": self.name,
        "image_url": self.image_url,
        "user_id": self.user_id,
        "created_at": self.created_at.isoformat() if self.created_at else None,
        "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        "deleted_at": self.deleted_at.isoformat() if self.deleted_at else None,
    }


class CategoryResource(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument(
        "name", type=str, required=True, help="Category name is required"
    )
    parser.add_argument(
        "image_url", type=str, required=True, help="Image URL is required"
    )



    def get(self, id=None):
        if id is None:
            categories = Category.query.all()
            return jsonify([format_category(c) for c in categories])
        else:
            category = Category.query.filter_by(id=id).first()
            if category is None:
                return {"message": "Category not found"}, 404
            return format_category(category), 200


    # creats new category
    # @jwt_required()
    @admin_required()
    def post(self):
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        if user.role != "admin":
            return {"message": "Admin access required"}, 403

        data = self.parser.parse_args()

        if not data.get("name"):
            return {"message": "Category name is required"}, 400
        if not data.get("image_url"):
            return {"message": "Image URL is required"}, 400

        category = Category(
            name=data["name"], image_url=data["image_url"], user_id=user_id
        )
        db.session.add(category)
        db.session.commit()

        return {"message": "Category created successfully"}, 201

 
    @admin_required()
    def patch(self, id):
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        if user.role != "admin":
            return {"message": "Admin access required"}, 403

        data = self.parser.parse_args()

        category = Category.query.filter_by(id=id, user_id=user_id).first()  # specific admin
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
            "category": format_category(category)
        }, 200


    # deletes entire category by id
    @admin_required()
    def delete(self, id):
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        if user.role != "admin":
            return {"message": "Admin access required"}, 403

        category = Category.query.filter_by(id=id, user_id=user_id).first()

        if category is None:
            return {"message": "Category not found"}, 404

        db.session.delete(category)
        db.session.commit()

        return {"message": "Category deleted successfully"}, 200
