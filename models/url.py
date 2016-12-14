from .shared import db


class Url(db.Model):
    url = db.Column(db.String(500), primary_key=True)
    key = db.Column(db.String(20), unique=True)
