from flask_wtf import FlaskForm
from wtforms import SubmitField, RadioField
from wtforms.validators import DataRequired


class TrainingOneForm(FlaskForm):
    variants = RadioField('Label', default=1)
    submit = SubmitField("submit")
