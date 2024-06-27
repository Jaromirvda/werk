from app import db
import sqlalchemy as sa


class Nvidia(db.Model):
    __tablename__ = 'nvidia'
    id = sa.Column(sa.Integer, nullable=False, primary_key=True)
    name = sa.Column(sa.String(50), nullable=False, unique=True)
    release_date = sa.Column(sa.String(50), nullable=False)
    vram = sa.Column(sa.String(50), nullable=False)
    series = sa.Column(sa.String(50), nullable=False)
    picture = sa.Column(sa.String(50), nullable=False)

    def __init__(self, name, release_date, vram, series, picture):
        self.name = name
        self.release_date = release_date
        self.vram = vram
        self.series = series
        self.picture = picture
