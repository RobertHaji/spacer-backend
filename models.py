from sqlalchemy import MetaData
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy_serializer import SerializerMixin
from datetime import datetime
from sqlalchemy import Numeric


metadata = MetaData()
db = SQLAlchemy(metadata=metadata)

class User(db.Model, SerializerMixin):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.VARCHAR, nullable=False)
    email = db.Column(db.VARCHAR, nullable=False)
    role = db.Column(db.Enum("admin", "user"), nullable=False, server_default="user")
    password_hash = db.Column(db.VARCHAR, nullable=False)
    created_at = db.Column(db.Timestamp, default=datetime.now())

    bookings = db.relationship("Booking", backref="user")
    categories = db.relationship("Category", back_populates="user")

    serialize_rules = ("-bookings.user", "-categories.user")


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

    bookings = db.relationship("Booking", backref="space")
    categories = db.relationship("Category", back_populates="spaces")

    serialize_rules = ("-bookings.space", "-category.spaces")


class Booking(db.Model, SerializerMixin):
    __tablename__ = "bookings"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    space_id = db.Column(db.Integer, db.ForeignKey("spaces.id"), nullable=False)
    number_of_guests = db.Column(db.Integer, nullable=False)
    date_of_booking = db.Column(db.DateTime, default=datetime.now())
    total_amount = db.Column(db.Numeric(10, 2), nullable=False)

    serialize_rules = ("-user.bookings", "-space.bookings")
    
class Category(db.Model, SerializerMixin):
    __tablename__ = "categories"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), nullable=False)
    image_url = db.Column(db.String(500), nullable=True)

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    user = db.relationship("User", back_populates="categories")
    spaces = db.relationship("Space", backref="category")

    serialize_rules = ("-user.categories",)    
    
