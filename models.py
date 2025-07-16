from sqlalchemy import MetaData
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy_serializer import SerializerMixin
from datetime import datetime

metadata = MetaData()
db = SQLAlchemy(metadata=metadata)

class User(db.Model, SerializerMixin):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.VARCHAR, nullable=False)
    email = db.Column(db.VARCHAR, nullable=False)
    role = db.Column(db.Enum("admin", "user"), nullable=False, server_default="user")
    password_hash = db.Column(db.VARCHAR, nullable=False)
    created_at = db.Column(db.Timestamp, default=datetime.now()

class Space(db.Model, SerializerMixin):

    __tablename__ = "spaces"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.VARCHAR, nullable=False)
    owner_name = db.Column(db.String(), nullable=False)
    description = db.Column(db.Text, nullable = False)
    rent_rate = db.Column(db.DECIMAL(), nullable=False)
    image_url = db.Column(db.String(), nullable = False)
    available = db.Column(db.Boolean, nullable=False, default=True)
    time_available = db.Column(db.String())
    category_id = db.Column(
        db.Integer, db.ForeignKey("categories.id", ondelete="cascade"), nullable=False
    )



class Bookings(db.Model, SerializerMixin):
    __tablename__ = "bookings"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    space_id = db.Column(db.Integer, db.ForeignKey("spaces.id"), nullable=False)
    number_of_guests = db.Column(db.Integer, nullable=False)
    date_of_booking = db.Column(db.DateTime, default=datetime.now())
    total_amount = db.Column(db.Integer, nullable=False)
    
