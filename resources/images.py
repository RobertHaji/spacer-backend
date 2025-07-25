from flask import request
from flask_restful import Resource
from models import db, Image, Space
from utils import admin_required

class ImageListResource(Resource):
    @admin_required()
    def post(self):
        data = request.get_json()
        if not data:
            return {"error": "No input data provided"}, 400

        url = data.get("url")
        space_id = data.get("space_id")

        if not url or not space_id:
            return {"error": "Missing 'url' or 'space_id'"}, 400

        space = Space.query.get(space_id)
        if not space:
            return {"error": f"Space with ID {space_id} not found"}, 404

        image = Image(url=url, space_id=space_id)
        try:
            db.session.add(image)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return {"error": f"Database error: {str(e)}"}, 500

        return {"message": "Image uploaded successfully", "image": image.to_dict()}, 201

class ImageResource(Resource):
    def get(self, image_id):
        image = Image.query.get(image_id)
        if not image:
            return {"error": "Image not found"}, 404
        return image.to_dict(), 200

    @admin_required()
    def delete(self, image_id):
        image = Image.query.get(image_id)
        if not image:
            return {"error": f"Image with ID {image_id} not found"}, 404

        try:
            db.session.delete(image)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return {"error": f"Database error: {str(e)}"}, 500

        return {"message": f"Image with ID {image_id} deleted successfully"}, 200

class SpaceListResource(Resource):
    def get(self):
        spaces = Space.query.all()
        return [{"id": s.id, "name": s.name} for s in spaces], 200
