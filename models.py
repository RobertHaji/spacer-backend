from sqlalchemy import MetaData
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy_serializer import SerializerMixin
from datetime import datetime

naming_convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}

metadata = MetaData(naming_convention=naming_convention)
db = SQLAlchemy(metadata=metadata)


class User(db.Model, SerializerMixin):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.VARCHAR, nullable=False)
    email = db.Column(db.VARCHAR, nullable=False)
    role = db.Column(db.Enum("admin", "user"), nullable=False, server_default="user")
    password_hash = db.Column(db.VARCHAR, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    bookings = db.relationship("Booking", backref="user")
    categories = db.relationship("Category", back_populates="user")

    serialize_rules = ("-bookings.user", "-categories.user")


class Space(db.Model, SerializerMixin):
    __tablename__ = "spaces"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.VARCHAR, nullable=False)
    owner_name = db.Column(db.String(), nullable=False)
    description = db.Column(db.Text, nullable=False)
    rent_rate = db.Column(db.Numeric(10, 2), nullable=False)
    image_url = db.Column(db.String(), nullable=False)
    available = db.Column(db.Boolean, nullable=False, default=True)
    location = db.Column(db.String(), nullable=False, default="unknown")

    time_available = db.Column(db.String())
    category_id = db.Column(
        db.Integer, db.ForeignKey("categories.id", ondelete="cascade"), nullable=False
    )
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
    deleted_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship("User", backref="spaces")
    bookings = db.relationship("Booking", backref="space")
    category = db.relationship("Category", back_populates="spaces")
    images = db.relationship("Image", backref="space", cascade="all, delete-orphan")

    serialize_rules = (
        "-bookings.space",
        "-category.spaces",
        "-images.space",
        "-users.spaces",
    )

    def to_json(self):
        return {
            "id": self.id,
            "name": self.name,
            "owner_name": self.owner_name,
            "description": self.description,
            "rent_rate": float(self.rent_rate),
            "image_url": self.image_url,
            "available": self.available,
            "location": self.location,
            "time_available": self.time_available,
            "category_id": self.category_id,
            "user_id": self.user_id,
            "created_at": self.created_at.isoformat()
            if self.created_at
            else None,  # Convert datetime to string
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "deleted_at": self.deleted_at.isoformat() if self.deleted_at else None,
            "category_name": self.category.name if self.category else None,
        }


class Booking(db.Model, SerializerMixin):
    __tablename__ = "bookings"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    space_id = db.Column(db.Integer, db.ForeignKey("spaces.id"), nullable=False)
    number_of_guests = db.Column(db.Integer, nullable=False)
    date_of_booking = db.Column(db.DateTime, default=datetime.utcnow)
    number_of_hours = db.Column(db.Integer, nullable=False, default=1)
    total_amount = db.Column(db.Numeric(10, 2), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    serialize_rules = ("-user.bookings", "-space.bookings")


class Category(db.Model, SerializerMixin):
    __tablename__ = "categories"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), nullable=False)
    image_url = db.Column(db.String(500), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
    deleted_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship("User", back_populates="categories")
    spaces = db.relationship("Space", back_populates="category")

    serialize_rules = ("-user.categories", "-spaces.category")


class Payment(db.Model, SerializerMixin):
    __tablename__ = "payments"

    id = db.Column(db.Integer, primary_key=True)
    booking_id = db.Column(
        db.Integer, db.ForeignKey("bookings.id"), nullable=False, unique=True
    )
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    payment_mode = db.Column(db.String(50), nullable=False)
    payment_status = db.Column(db.String(20), nullable=False, default="pending")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    booking = db.relationship("Booking", backref="payment")

    serialize_rules = ("-booking.payment",)


class Image(db.Model, SerializerMixin):
    __tablename__ = "images"

    id = db.Column(db.Integer, primary_key=True)
    space_id = db.Column(db.Integer, db.ForeignKey("spaces.id"), nullable=False)
    url = db.Column(db.String(500), nullable=False)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)

    serialize_rules = ("-space.images",)
