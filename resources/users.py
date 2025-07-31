from flask_restful import Resource, reqparse
from flask_bcrypt import generate_password_hash, check_password_hash
from flask_jwt_extended import (
    create_access_token,
    jwt_required,
    get_jwt_identity,
    get_jwt,
)

from models import db, User

from utils import admin_required
from datetime import timedelta


def format_user(user):
    return {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "role": user.role,
        "created_at": user.created_at.isoformat(),
    }


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
                identity=str(user.id),
                additional_claims={"role": user.role},
                expires_delta=timedelta(hours=24),
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
            identity=str(user.id),
            additional_claims={"role": user.role},
            expires_delta=timedelta(hours=24),
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
    @jwt_required()
    def get(self, id=None):
        current_user_id = int(get_jwt_identity())
        if id is None:
            claims = get_jwt().get("role")
            if claims != "admin":
                return {"message": "Admin access required"}, 403
            data = User.query.all()
            return [format_user(user) for user in data], 200
        else:
            if int(id) != current_user_id:
                return {"message": "Unauthorized"}, 401
            user = User.query.get(id)
            if not user:
                return {"message": "User not found"}, 404
            return format_user(user), 200

    @jwt_required()
    def patch(self, id):
        current_user_id = int(get_jwt_identity())
        if int(id) != current_user_id:
            return {"message": "Unauthorized"}, 401

        parser = reqparse.RequestParser()
        parser.add_argument(
            "name", type=str, required=False, help="Name cannot be blank"
        )
        parser.add_argument(
            "email", type=str, required=False, help="Email cannot be blank"
        )
        data = parser.parse_args()

        user = User.query.get(id)
        if not user:
            return {"message": "User not found"}, 404

        if data["email"] and data["email"] != user.email:
            existing_user = User.query.filter_by(email=data["email"]).first()
            if existing_user:
                return {"message": "Email address is already taken"}, 409

        if data["name"]:
            user.name = data["name"]
        if data["email"]:
            user.email = data["email"]

        db.session.commit()
        return format_user(user), 200
