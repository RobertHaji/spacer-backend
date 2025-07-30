from flask_restful import Resource, reqparse
from models import User, db
from flask_bcrypt import generate_password_hash




class CheckEmailResource(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument("email", type=str, required=True, help="Email is required")

    def post(self):
        data = self.parser.parse_args()

        user = User.query.filter_by(email=data["email"]).first()

        if user:
            return {"message": "Email exists"}, 200
        else:
            return {"message": "Invalid email"}, 404


class ResetPasswordResource(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument("email", type=str, required=True, help="Email is required")
    parser.add_argument(
        "new_password", type=str, required=True, help="New password is required"
    )

    def post(self):
        data = self.parser.parse_args()

        user = User.query.filter_by(email=data["email"]).first()

        if not user:
            return {"message": "Email address not found"}, 404

        # hash new password
        hashed_password = generate_password_hash(data["new_password"]).decode("utf-8")
        user.password_hash = hashed_password

        db.session.commit()

        return {"message": "Password has been reset successfully"}, 200
