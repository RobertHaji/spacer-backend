from flask_restful import Resource, reqparse
from flask_bcrypt import generate_password_hash, check_password_hash

from models import db, User


class SignInResource(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument("full_name", required=True, help="full_name is required")
    parser.add_argument("email", required=True, help="email is required")
    parser.add_argument("password", required=True, help="password is required")

    def post(self):
        data = self.parser.parse_args()

        user = User.query.filter_by(email=data["email"]).first()

        if user is None:
            return {"message": "invalid email or password"}, 403

        # validate password
        if check_password_hash(user.password_hash, data["password_hash"]):
            # then generate access token

            return {"message": "login successfull", "user": user.to_dict()}, 201


class SignUpResource(Resource):
    parser = reqparse.RequestParser()

    parser.add_argument("full_name", required=True, help="full_name is required")
    parser.add_argument("email", required=True, help="email is required")
    parser.add_argument("password_hash", required=True, help="password is required")

    def post(self):
        data = self.parser.parse_args()

        email = User.query.filter_by(email=data["email"]).first()

        if email:
            return {"message": "email address is already taken"}

        # encrypt the password
        hash = generate_password_hash(data["password_hash"]).decode("utf-8")

        user = User(**data, password_hash=hash)

        db.session.add(user)
        db.session.commit()

        # generate access Token

        # send email

        return {"message": "account created successfully", "user": user.to_dict()}, 201


class UserResource(Resource):
    def get(self):
        data = User.query.all()
        result = []
        for user in data:
            result.append(user.to_dict())

        return result
