from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField
from wtforms.validators import DataRequired


class CreateGPUForm(FlaskForm):
    category = SelectField('Category', choices=[('Nvidia', 'Nvidia'), ('AMD', 'AMD')], validators=[DataRequired()])
    name = StringField('Name', validators=[DataRequired()])
    release_date = StringField('Release Date', validators=[DataRequired()])
    vram = StringField('VRAM', validators=[DataRequired()])
    picture = StringField('Picture')
    submit = SubmitField('Submit')