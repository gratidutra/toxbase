from datetime import datetime

from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Text

from src import bcrypt, db, login_manager

#db = SQLAlchemy()

@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))

class Users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(length=40), nullable=False, unique=True)
    email = db.Column(db.String(length=40), nullable=False, unique=True)
    password = db.Column(db.String(length=300), nullable=False, unique=True)
    role = db.Column(db.String(20), nullable=False, default="user")  # 'admin' ou 'user'

    def is_admin(self):
        return self.role == "admin"

    @property
    def password_cryp(self):
        return self.password_cryp

    @password_cryp.setter
    def password_cryp(self, password_text):
        self.password = bcrypt.generate_password_hash(password_text).decode("utf-8")

    def convert_password(self, password_clean_text):
        return bcrypt.check_password_hash(self.password, password_clean_text)

    def __repr__(self):
        return f"Register: {self.name}"


class PubChem(db.Model):
    __tablename__ = "pubchem" 
    id = db.Column(db.Integer, primary_key=True)
    cas_number = db.Column(db.String(40), nullable=False)
    cid = db.Column(db.String(40))
    molecular_formula = db.Column(db.String(300))
    synonyms = db.Column(db.String(300))
    molecular_weight = db.Column(db.String(300))
    dates = db.Column(db.String(300))
    description = db.Column(Text, nullable=True)
    created_date = db.Column(db.DateTime, default=datetime.utcnow)
    updated_date = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )


class Echa(db.Model):
    __tablename__ = "echa" 
    id = db.Column(db.Integer, primary_key=True)
    cas_number = db.Column(db.String(40), nullable=False)
    ec = db.Column(db.String(40))
    molecular_formula = db.Column(db.String(300))
    haz_classification = db.Column(Text, nullable=True)
    about_1 = db.Column(Text, nullable=True)
    about_2 = db.Column(Text, nullable=True)
    consumer_user = db.Column(db.String(300))
    created_date = db.Column(db.DateTime, default=datetime.utcnow)
    updated_date = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )


class TokensPassword(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    token = db.Column(db.String(64), nullable=False, unique=True)
    link = db.Column(db.String(90))
    created_date = db.Column(db.DateTime, default=datetime.utcnow())
    updated_date = db.Column(db.DateTime, default=datetime.utcnow())
