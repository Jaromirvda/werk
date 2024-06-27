from app import db


class User(db.Model):
    user_name = db.Column(db.String(80), unique=True, nullable=False, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)
    def __init__(self, user_name, email, password):
        self.user_name = user_name
        self.email = email
        self.password = password