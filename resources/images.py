from flask import request
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt
from models import db, Image, Space


class ImageResource(Resource):

    @jwt_required()
    def post(self):
        claims = get_jwt()
        role = claims.get("role")

        if role != "admin":
            return {"error": "Admin access required"}, 403

        data = request.get_json()
        if not data:
            return {"error": "No input data provided"}, 400

        url = data.get("url")
        space_id = data.get("space_id")

        if not url or not space_id:
            return {"error": "Missing 'url' or 'space_id'"}, 400

        space = Space.query.get(space_id)
        if not space:
            return {"error": f"Space with id {space_id} does not exist"}, 404

        image = Image(url=url, space_id=space_id)
        try:
            db.session.add(image)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return {"error": f"Database error: {str(e)}"}, 500

        return {
            "message": "Image uploaded successfully",
            "image": image.serialize() if hasattr(image, "serialize") else {"id": image.id, "url": image.url}
        }, 201

    def get(self):
        images = Image.query.all()
        return {
            "images": [img.serialize() if hasattr(img, "serialize") else {"id": img.id, "url": img.url} for img in images]
        }, 200

    @jwt_required()
    def delete(self, id):
        claims = get_jwt()
        role = claims.get("role")

        if role != "admin":
            return {"error": "Admin access required"}, 403

        image = Image.query.get(id)
        if not image:
            return {"error": f"Image with id {id} not found"}, 404

        try:
            db.session.delete(image)
            db.session.commit()
            return {"message": f"Image with ID {id} deleted successfully"}, 200
        except Exception as e:
            db.session.rollback()
            return {"error": str(e)}, 500
