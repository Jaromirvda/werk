from app import db


class AMD(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    release_date= db.Column(db.String(50), nullable=False)
    vram = db.Column(db.String(50), nullable=False)
    series = db.Column(db.String(50), nullable=False)
    picture = db.Column(db.String(50), nullable=False)

    def __init__(self, name, release_date, vram, series, picture):
        self.name = name
        self.release_date = release_date
        self.vram = vram
        self.series = series
        self.picture = picture

    def __repr__(self):
        return '<HeroList %r>' % self.name