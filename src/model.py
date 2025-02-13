from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()


class PubChem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cas_number = db.Column(db.String(40), nullable=False)
    cid = db.Column(db.String(40))
    molecular_formula = db.Column(db.String(300))
    synonyms = db.Column(db.String(300))
    molecular_weight = db.Column(db.String(300))
    dates = db.Column(db.String(300))
    description = db.Column(db.text, nullable=True)
    created_date = db.Column(db.DateTime, default=datetime.utcnow)
    updated_date = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )


class Echa(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cas_number = db.Column(db.String(40), nullable=False)
    ec = db.Column(db.String(40))
    molecular_formula = db.Column(db.String(300))
    haz_classification = db.Column(db.text, nullable=True)
    about_1 = db.Column(db.text, nullable=True)
    about_2 = db.Column(db.text, nullable=True)
    consumer_user = db.Column(db.String(300))
    created_date = db.Column(db.DateTime, default=datetime.utcnow)
    updated_date = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )
