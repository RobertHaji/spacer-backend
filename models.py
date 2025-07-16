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
    created_at = db.Column(db.Timestamp, default=datetime.now())

