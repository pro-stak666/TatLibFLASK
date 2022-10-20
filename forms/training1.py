from flask_wtf import FlaskForm
from wtforms import SubmitField, RadioField
from wtforms.validators import DataRequired


class TrainingOneForm(FlaskForm):
    variants = RadioField('Label')
    submit = SubmitField("submit")