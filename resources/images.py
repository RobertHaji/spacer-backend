from flask import request
from flask_restful import Resource
from models import db, Image, Space
from utils import admin_required

def format_image(image):
    return {
        "id": image.id,
        "url": image.url,
        "space_id": image.space_id,
        "created_at": image.created_at.isoformat(),
    }

class ImageListResource(Resource):
    @admin_required()
    def post(self):
        """Admin only: Add a new image."""
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

        return {"message": "Image uploaded successfully", "image": format_image(image)}, 201


class ImageResource(Resource):
    def get(self, id):
        """Public: Get a single image by ID."""
        image = Image.query.filter_by(id=id).first()
        if not image:
            return {"error": "Image not found"}, 404
        return format_image(image), 200

    @admin_required()
    def delete(self, image_id):
        """Admin only: Delete an image by ID."""
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
