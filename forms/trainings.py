from flask_wtf import FlaskForm
from wtforms import SubmitField, RadioField, StringField


class TrainingOneForm(FlaskForm):
    variants = RadioField('Label', default=1)
    submit = SubmitField("submit")


class TrainingTwoForm(FlaskForm):
    answer = StringField('Label')
    submit = SubmitField("submit")