from sqlalchemy import create_engine, CheckConstraint
import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token
from datetime import timedelta

class Base(DeclarativeBase):
  pass

db = SQLAlchemy(model_class=Base)

class Painting(db.Model):
    __tablename__ = 'paintings'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(255), nullable=False)
    body = db.Column(db.Text)
    status = db.Column(db.String(10), nullable=False)
    __table_args__ =(CheckConstraint("status IN ('sold', 'on sale')", name='check_status'),)
    size = db.Column(db.String(50))
    price = db.Column(db.DECIMAL(10, 2))
    search_query = db.Column(db.String(255))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    creator  = db.relationship('User', back_populates='artworks')
    created_at = db.Column(db.TIMESTAMP, default=datetime.datetime.utcnow)
    updated_at = db.Column(db.TIMESTAMP, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    image = db.Column(db.Text)

class Exhibition(db.Model):
    __tablename__ = 'exhibitions'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    current_exhibitions = db.Column(db.String(255))
    created_at = db.Column(db.TIMESTAMP, default=datetime.datetime.utcnow)

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    role = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    created_at = db.Column(db.TIMESTAMP, default=datetime.datetime.utcnow)
    updated_at = db.Column(db.TIMESTAMP, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    artworks = db.relationship('Painting', back_populates='creator', lazy=True)
    twofa_code_expires = db.Column(db.DateTime)
    twofa_code = db.Column(db.String(6))
    is_2fa_enabled = db.Column(db.Boolean, default=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_auth_token(self, expires_in=3600):
        return create_access_token(
            identity=self.id,
            expires_delta=timedelta(seconds=expires_in)
        )


def init_db(database_url):
    engine = create_engine(database_url)
    Base.metadata.create_all(engine)
    return engine