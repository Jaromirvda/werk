from app import db
import sqlalchemy as sa


class Hero(db.Model):
    __tablename__ = 'heroes'
    id = sa.Column(sa.Integer, nullable=False, primary_key=True)
    name = sa.Column(sa.String(50), nullable=False, unique=True)
    description = sa.Column(sa.String(512), nullable=False)

    def __init__(self, name, description):
        self.name = name
        self.description = description
    def __repr__(self):
        return '<Hero {}>'.format(self.name)