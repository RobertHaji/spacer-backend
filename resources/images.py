from flask import request
from flask_restful import Resource
from models import db, Image, User
import re


class ImageResource(Resource):
    def post(self):
        data = request.get_json()
        url = data.get("url")
        user_id = data.get("user_id")

        if not url or not user_id:
            return {"error": "Missing 'url' or 'user_id'"}, 400

       
        user = User.query.get(user_id)
        if not user:
            return {"error": f"User with id {user_id} does not exist"}, 404

        image = Image(url=url, user_id=user_id)
        db.session.add(image)
        db.session.commit()
        return {"message": "Image uploaded", "image": image.serialize()}, 201

    def get(self):
        images = Image.query.all()
        return {"images": [img.serialize() for img in images]}, 200

    def delete(self):
        data = request.get_json()
        image_id = data.get("id")

        if not image_id:
            return {"error": "Missing image 'id'"}, 400

        image = Image.query.get(image_id)
        if not image:
            return {"error": f"Image with id {image_id} not found"}, 404

        db.session.delete(image)
        db.session.commit()
        return {"message": "Image deleted"}, 200
