from flask import request
from flask_restful import Resource
from models import db, Image

class ImageResource(Resource):
    def post(self):
        data = request.get_json()
        if not data or "url" not in data or "user_id" not in data:
            return {"error": "Missing 'url' or 'user_id'"}, 400

        image = Image(url=data["url"], user_id=data["user_id"])
        db.session.add(image)
        db.session.commit()
        return {"message": "Image uploaded", "image": image.serialize()}, 201

    def get(self):
        images = Image.query.all()
        return {"images": [img.serialize() for img in images]}, 200

    def delete(self):
        data = request.get_json()
        if not data or "id" not in data:
            return {"error": "Missing image 'id'"}, 400

        image = Image.query.get(data["id"])
        if image:
            db.session.delete(image)
            db.session.commit()
            return {"message": "Image deleted"}, 200

        return {"error": "Image not found"}, 404
q