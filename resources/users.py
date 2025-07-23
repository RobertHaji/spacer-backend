from flask_restful import Resource, reqparse
from flask_bcrypt import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token

from models import db, User

from utils import admin_required


class SignInResource(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument("email", required=True, help="email is required")
    parser.add_argument("password_hash", required=True, help="password is required")

    def post(self):
        data = self.parser.parse_args()

        user = User.query.filter_by(email=data["email"]).first()

        if user is None:
            return {"message": "invalid email or password"}, 403

        # validate password
        if check_password_hash(user.password_hash, data["password_hash"]):
            # then generate access token
            access_token = create_access_token(
                identity=str(user.id), additional_claims={"role": user.role}
            )

            return {
                "message": "Logged in successfully",
                "access_token": access_token,
                "user": {
                    "id": user.id,
                    "name": user.name,
                    "email": user.email,
                    "role": user.role,
                },
            }, 200
        else:
            return {"message": "invalid email or password"}, 403


class SignUpResource(Resource):
    parser = reqparse.RequestParser()

    parser.add_argument("name", type=str, required=True, help="name is required")
    parser.add_argument("email", type=str, required=True, help="email is required")
    parser.add_argument(
        "password_hash", type=str, required=True, help="password is required"
    )

    def post(self):
        data = self.parser.parse_args()

        email = User.query.filter_by(email=data["email"]).first()

        if email:
            return {"message": "email address is already taken"}, 409

        # encrypt the password
        hash = generate_password_hash(data["password_hash"]).decode("utf-8")

        del data["password_hash"]

        user = User(**data, password_hash=hash)

        db.session.add(user)
        db.session.commit()

        # generate access Token
        access_token = create_access_token(
            identity=str(user.id), additional_claims={"role": user.role}
        )

        # send email

        return {
            "message": "Account created successfully",
            "access_token": access_token,
            "user": {
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "role": user.role,
            },
        }, 201


class UserResource(Resource):
    @admin_required()
    def get(self, id=None):
        if id is None:
            data = User.query.all()
            result = [user.to_dict() for user in data]
            return result
        else:
            user = User.query.get(id)
            if not user:
                return {"message": "User not found"}, 404
            return user.to_dict()
